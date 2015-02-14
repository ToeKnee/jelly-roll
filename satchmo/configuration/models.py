from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import loading
from django.db.utils import DatabaseError
from django.utils.translation import ugettext_lazy as _
from satchmo.caching import cache_key, cache_get, cache_set, NotCachedError
from satchmo.caching.models import CachedObjectMixin

import logging
log = logging.getLogger(__name__)

__all__ = ['SettingNotSet', 'Setting', 'LongSetting', 'find_setting']


def _safe_get_siteid(site):
    if site:
        siteid = site.id
    else:
        try:
            site = Site.objects.get_current()
            siteid = site.id
        # DatabaseError is likely to occur when running tests/initial
        # migrations as the django_site table may not exist yet.
        except (Site.DoesNotExist, DatabaseError):
            siteid = settings.SITE_ID
    return siteid


def find_setting(group, key, site=None):
    """Get a setting or longsetting by group and key, cache and return it."""

    siteid = _safe_get_siteid(site)

    ck = cache_key('Setting', siteid, group, key)
    setting = None
    try:
        setting = cache_get(ck)

    except NotCachedError:
        if loading.app_cache_ready():
            try:
                setting = Setting.objects.get(site__id__exact=siteid, key__exact=key, group__exact=group)

            except Setting.DoesNotExist:
                # maybe it is a "long setting"
                try:
                    setting = LongSetting.objects.get(site__id__exact=siteid, key__exact=key, group__exact=group)

                except LongSetting.DoesNotExist:
                    pass

            cache_set(ck, value=setting)

    if not setting:
        raise SettingNotSet(key, cachekey=ck)

    return setting


class SettingNotSet(Exception):
    def __init__(self, k, cachekey=None):
        self.key = k
        self.cachekey = cachekey


class SettingManager(models.Manager):
    def get_queryset(self):
        all = super(SettingManager, self).get_queryset()
        siteid = _safe_get_siteid(None)
        return all.filter(site__id__exact=siteid)


class Setting(models.Model, CachedObjectMixin):
    site = models.ForeignKey(Site, verbose_name=_('Site'))
    group = models.CharField(max_length=100, blank=False, null=False)
    key = models.CharField(max_length=100, blank=False, null=False)
    value = models.CharField(max_length=255, blank=True)

    objects = SettingManager()

    class Meta:
        db_table = "configuration_setting"
        unique_together = ('site', 'group', 'key')

    def __unicode__(self):
        return u"{group}:{key} {value}".format(
            group=self.group,
            key=self.key,
            value=self.value
        )

    def save(self, *args, **kwargs):
        try:
            site = self.site
        except Site.DoesNotExist:
            self.site = Site.objects.get_current()

        super(Setting, self).save(*args, **kwargs)

        self.cache_set()

    def __nonzero__(self):
        return self.id is not None

    def cache_key(self, *args, **kwargs):
        return cache_key('Setting', self.site, self.group, self.key)

    def delete(self):
        self.cache_delete()
        super(Setting, self).delete()


class LongSettingManager(models.Manager):
    def get_queryset(self):
        all = super(LongSettingManager, self).get_queryset()
        siteid = _safe_get_siteid(None)
        return all.filter(site__id__exact=siteid)


class LongSetting(models.Model, CachedObjectMixin):
    """A Setting which can handle more than 255 characters"""
    site = models.ForeignKey(Site, verbose_name=_('Site'))
    group = models.CharField(max_length=100, blank=False, null=False)
    key = models.CharField(max_length=100, blank=False, null=False)
    value = models.TextField(blank=True)

    objects = LongSettingManager()

    class Meta:
        db_table = "configuration_longsetting"
        unique_together = ('site', 'group', 'key')

    def __nonzero__(self):
        return self.id is not None

    def save(self, *args, **kwargs):
        try:
            site = self.site
        except Site.DoesNotExist:
            self.site = Site.objects.get_current()
        super(LongSetting, self).save(*args, **kwargs)
        self.cache_set()

    def cache_key(self, *args, **kwargs):
        # note same cache pattern as Setting.  This is so we can look up in one check.
        # they can't overlap anyway, so this is moderately safe.  At the worst, the
        # Setting will override a LongSetting.
        return cache_key('Setting', self.site, self.group, self.key)

    def delete(self):
        self.cache_delete()
        super(LongSetting, self).delete()
