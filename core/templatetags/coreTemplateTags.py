from django import template
from django.urls import reverse

from onetutor.operations.navigationOperations import linkItem, Icon

register = template.Library()


@register.simple_tag
def navigationPanel(request):
    links = [
        linkItem('Home', reverse('core:index-view'), None),
    ]

    if request.user.is_authenticated:
        links.extend(
            [
                linkItem('Account', '', None, [
                    None,
                    linkItem('Logout', reverse('accounts:logout-view'), Icon('', 'fas fa-sign-out-alt', '15')),
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
    return links
