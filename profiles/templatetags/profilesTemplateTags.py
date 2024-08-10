from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

from onetutor.utils.common import SettingTab, tutorTabs
from onetutor.utils.exceptions import ProfileNotFound

register = template.Library()


class Profile:

    def __init__(self, name, description, icon, user):
        self.name = name
        self.description = description
        self.icon = icon
        self.url = reverse('profiles:create-profile-view') + f'?type={user}'


def getProfileSelectComponent(profile: Profile):
    itemContent = f'''
    <div class='col-lg-4 col-md-4 col-sm-10 pb-4 d-block m-auto'>
        <div class='pricing-item' style='box-shadow: 0px 0px 30px -7px rgba(0,0,0,0.29);'>
            <div class='pt-4 pb-3' style='letter-spacing: 2px'>
                <h4>{profile.name}</h4>
            </div>
            <div class='pricing-price pb-1 text-primary color-primary-text '>
                <img src='{profile.icon}'
                     height='143' width='137'>
            </div>
            <div class='pricing-description'>
                <ul class='list-unstyled mt-3 mb-4'>
                    <li class='pl-3 pr-3'>{profile.description}
                    </li>
                </ul>
            </div>
            <div class='pricing-button pb-4'>
                <a href='{profile.url}' type='button'
                   class='btn btn-lg btn-outline-primary w-75'>Select</a>
            </div>
        </div>
    </div>
    '''
    return mark_safe(itemContent)


@register.simple_tag
def render():
    profiles = [
        Profile(
            'Student',
            'Get taught by verified tutors, review study materials or chat with a tutor.',
            'https://cdn-thumbs.imagevenue.com/87/6b/3a/ME18SUPE_t.JPG',
            'student',
        ),
        Profile(
            'Parent',
            'Parents account to manage their children\'s activities and for consent.',
            'https://cdn-thumbs.imagevenue.com/db/1c/cd/ME18SUPD_t.jpg',
            'parent'
        ),
        Profile(
            'Tutor',
            'Tutor the students and manage lessons with your students.',
            'https://cdn-thumbs.imagevenue.com/7c/08/8f/ME18SUPC_t.JPG',
            'tutor',
        )
    ]
    itemContent = f'''
        <br>
        <h2 class='text-center'>Select the profile you want to create.</h2>
        <br><br><br>
        <div class='container text-center'>
            <div class='row'>
                {''.join([getProfileSelectComponent(profile) for profile in profiles])}
            </div>
        </div>
    '''
    return mark_safe(itemContent)


@register.simple_tag
def renderTabComponent(request, tab: SettingTab):
    style = 'style=\'background-color: lightgrey\'' if request.GET.get('tab') == tab.code else ''
    itemContent = f'''
        <a href='{reverse('profiles:settings-view') + f'?tab={tab.code}'}' class='list-group-item' {style}>{tab.name}</a>
    '''
    return itemContent


@register.simple_tag
def getTabsForProfile(request):
    if request.user.is_authenticated and hasattr(request.user, 'tutorProfile'):
        tabList = ''.join([renderTabComponent(request, tab) for tab in tutorTabs])
    elif request.user.is_authenticated and hasattr(request.user, 'studentProfile'):
        tabList = ''
    elif request.user.is_authenticated and hasattr(request.user, 'parentProfile'):
        tabList = ''
    else:
        raise ProfileNotFound

    itemContent = f'''
        <div class='card' style='width: 18rem;'>
            <ul class='list-group list-group-flush'>
                {tabList}
            </ul>
        </div>
    '''
    return mark_safe(itemContent)
