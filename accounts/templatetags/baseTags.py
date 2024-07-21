from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

from accounts.models import TutorProfile, StudentProfile, ParentProfile
from onetutor.base.utils.navigationBar import linkItem, Icon
from onetutor.operations import generalOperations

register = template.Library()


@register.simple_tag
def navigationPanel(request):
    links = [
        linkItem('Home', reverse('tutoring:index-view'), None)
    ]

    if request.user.is_authenticated:
        if hasattr(request.user, 'tutorProfile'):
            profileTab = generalOperations.getTutorSettingsTab()[0].url
        elif hasattr(request.user, 'studentProfile'):
            profileTab = generalOperations.getStudentSettingsTab()[0].url
        elif hasattr(request.user, 'parentProfile'):
            profileTab = generalOperations.getParentSettingsTab()[0].url
        else:
            profileTab = reverse('accounts:create-profile')

        links.extend(
            [
                linkItem('Account', '', None, [
                    linkItem('Profile', profileTab, Icon('', 'fas fa-user-circle', '20')),
                    linkItem('Q & A', None, Icon('', 'fas fa-question-circle', '20')),
                    linkItem('My Students', None, Icon('', 'fas fa-child', '20')),
                    linkItem('Settings', None, Icon('', 'fas fa-cogs', '20')),
                    None,
                    linkItem('Logout', reverse('accounts:logout-view'), Icon('', 'fas fa-sign-out-alt', '20')),
                ]),
            ]
        )
    else:
        links.append(
            linkItem('Login / Register', '', None, [
                linkItem('Register', reverse('accounts:register-view'), Icon('', 'fas fa-user-circle', '20')),
                None,
                linkItem('Login', reverse('accounts:login-view'), Icon('', 'fas fa-sign-in-alt', '20')),
            ]),
        )

    links.append(
        linkItem('Forum', reverse('forum:index-view'), None)
    )
    return links


@register.simple_tag
def renderNavigationPanelComponent(panel):
    panelIcon = panel.get('icon') if panel.get('icon') else '<span></span>'
    if panel.get('subLinks') is None:
        itemContent = f'''
        <li class='nav-item active'>
            <a class='nav-link' href='{panel.get('url')}' data-toggle='tooltip' data-placement='right'
               title='{panel.get('name')}'>
                {panelIcon} {panel.get('name')}
            </a>
        </li>
        '''
    else:
        content = ''
        for subLink in panel.get('subLinks'):
            if subLink:
                content += f'''
                    <a class='dropdown-item'href='{subLink.get('url')}'> {subLink.get('icon')} {subLink.get('name')}</a>
                '''
            else:
                content += f'''<div class='dropdown-divider'></div>'''

        itemContent = f'''
        <li class='nav-item dropdown'>
            <a class='nav-link dropdown-toggle' href='#' id='navbarDropdown' role='button'
               data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>
                {panelIcon} {panel.get('name')}
            </a>
            <div class='dropdown-menu dropdown-menu-right' aria-labelledby='navbarDropdown'>
                {content}
            </div>
        </li>
        '''

    return mark_safe(itemContent)
