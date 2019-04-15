from django.apps import apps
from django.db import models

from satchmo.caching import cache_key, cache_get, cache_set, NotCachedError
from satchmo.caching.models import CachedObjectMixin

from .exceptions import SettingNotSet

import logging

log = logging.getLogger(__name__)

__all__ = ["Setting", "LongSetting", "find_setting"]


def find_setting(group, key):
    """Get a setting or longsetting by group and key, cache and return it."""

    ck = cache_key("setting", group, key)
    setting = None
    try:
        setting = cache_get(ck)

    except NotCachedError:
        if apps.ready:
            try:
                setting = Setting.objects.get(key__exact=key, group__exact=group)

            except Setting.DoesNotExist:
                # maybe it is a "long setting"
                try:
                    setting = LongSetting.objects.get(
                        key__exact=key, group__exact=group
                    )

                except LongSetting.DoesNotExist:
                    pass

            cache_set(ck, value=setting)

    if not setting:
        raise SettingNotSet(key, cachekey=ck)

    return setting


class Setting(models.Model, CachedObjectMixin):
    group = models.CharField(max_length=100, blank=False, null=False)
    key = models.CharField(max_length=100, blank=False, null=False)
    value = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "configuration_setting"
        unique_together = ("group", "key")

    def __str__(self):
        return "{group}:{key} {value}".format(
            group=self.group, key=self.key, value=self.value
        )

    def save(self, *args, **kwargs):

        super(Setting, self).save(*args, **kwargs)

        self.cache_set()

    def __bool__(self):
        return self.id is not None

    def cache_key(self, *args, **kwargs):
        return cache_key("setting", self.group, self.key)

    def delete(self):
        self.cache_delete()
        super(Setting, self).delete()


class LongSetting(models.Model, CachedObjectMixin):
    """A Setting which can handle more than 255 characters"""

    group = models.CharField(max_length=100, blank=False, null=False)
    key = models.CharField(max_length=100, blank=False, null=False)
    value = models.TextField(blank=True)

    class Meta:
        db_table = "configuration_longsetting"
        unique_together = ("group", "key")

    def __bool__(self):
        return self.id is not None

    def save(self, *args, **kwargs):
        super(LongSetting, self).save(*args, **kwargs)
        self.cache_set()

    def cache_key(self, *args, **kwargs):
        # note same cache pattern as Setting.  This is so we can look up in one check.
        # they can't overlap anyway, so this is moderately safe.  At the worst, the
        # Setting will override a LongSetting.
        return cache_key("setting", self.group, self.key)

    def delete(self):
        self.cache_delete()
        super(LongSetting, self).delete()
