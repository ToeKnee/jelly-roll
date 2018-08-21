from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from satchmo.configuration.forms import SettingsEditor
from satchmo.configuration.functions import ConfigurationSettings

import logging
log = logging.getLogger(__name__)


def group_settings(request, group, template='configuration/group_settings.html'):
    # Determine what set of settings this editor is used for
    mgr = ConfigurationSettings()
    if group is None:
        settings = mgr
        title = 'Site settings'
    else:
        settings = mgr[group]
        title = settings.name
        log.debug('title: %s', title)

    if request.method == 'POST':
        # Populate the form with user-submitted data
        data = request.POST.copy()
        form = SettingsEditor(data, settings=settings)
        if form.is_valid():
            form.full_clean()
            for name, value in list(form.cleaned_data.items()):
                group, key = name.split('__')
                cfg = mgr.get_config(group, key)
                if cfg.update(value):
                    # Give user feedback as to which settings were changed
                    messages.add_message(
                        request, messages.SUCCESS, 'Updated %s on %s' % (cfg.key, cfg.group.key))

            return HttpResponseRedirect(request.path)
    else:
        # Leave the form populated with current setting values
        form = SettingsEditor(settings=settings)

    return render(request, template, {
        'title': title,
        'group': group,
        'form': form,
    })


group_settings = staff_member_required(group_settings)

# Site-wide setting editor is identical, but without a group
# staff_member_required is implied, since it calls group_settings


def site_settings(request):
    return group_settings(request, group=None, template='configuration/site_settings.html')
