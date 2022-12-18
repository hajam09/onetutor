from django import template
from django.utils.safestring import mark_safe

from accounts.models import TutorProfile, StudentProfile, ParentProfile
from onetutor.operations import generalOperations

register = template.Library()


@register.simple_tag
def renderTabComponent(request, tab):
    isActive = "active" if request.GET.get("tab") == tab.tab else ""
    itemContent = f"""
    <a class="nav-link mb-3 p-3 shadow {isActive}" id="{tab.identifier}" href="{tab.url}" aria-selected="true">
        <i class="{tab.icon}"></i>
        <span class="font-weight-bold small text-uppercase">{tab.internalKey}</span>
    </a>
    """
    return itemContent


@register.simple_tag
def getTabsForProfile(request):
    profile = generalOperations.getProfileForUser(request.user)

    if isinstance(profile, TutorProfile):
        tabList = generalOperations.getTutorSettingsTab()
    elif isinstance(profile, StudentProfile):
        tabList = generalOperations.getStudentSettingsTab()
    elif isinstance(profile, ParentProfile):
        tabList = generalOperations.getParentSettingsTab()
    else:
        raise NotImplementedError

    itemContent = f"""
    <div class="nav flex-column nav-pills nav-pills-custom" id="v-pills-tab" role="tablist" aria-orientation="vertical">
        {"".join([renderTabComponent(request, tab) for tab in tabList])}
    </div>
    """
    return mark_safe(itemContent)
