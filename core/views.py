from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView


def indexView(request):
    return render(request, 'core/indexView.html')


class StaticPageView(TemplateView):

    def get_template_names(self):
        page = self.kwargs.get('pageName')
        validPages = [
            'termsAndConditions',
            'privacyPolicy',
            'ourFeatures',
            'aboutUs',
            'contactUs',
            'faq',
            'cookiePolicy',
            'userAgreement',
            'communityGuidelines',
            'refundPolicy'
        ]

        if page in validPages:
            return f'core/static/{page}.html'
        raise Http404('Page not found')
