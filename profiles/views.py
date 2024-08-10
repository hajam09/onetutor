from datetime import datetime

from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views.generic import TemplateView

from onetutor.utils import utilsOperations, common
from onetutor.utils.common import (
    tutorTabs,
    studentTabs,
    parentTabs, Render
)
from onetutor.utils.exceptions import ProfileNotFound
from profiles.forms import (
    TutorProfileForm,
    StudentProfileForm,
    ParentProfileForm, CustomPasswordChangeForm
)


class CreateProfileTemplateView(TemplateView):

    def __init__(self):
        super(CreateProfileTemplateView, self).__init__()
        self.profiles = {
            'tutor': {
                'form': TutorProfileForm,
                'title': 'Create tutor profile'
            },
            'student': {
                'form': StudentProfileForm,
                'title': 'Create student profile'
            },
            'parent': {
                'form': ParentProfileForm,
                'title': 'Create parent profile'
            }
        }

    def getRequestedProfileType(self):
        _type = self.request.GET.get('type')
        return _type if _type is None else _type.casefold()

    def get_template_names(self):
        profileType = self.getRequestedProfileType()

        if profileType is None:
            return 'profiles/selectProfileTemplate.html'

        if profileType in self.profiles:
            return 'profiles/createProfileTemplate.html'

        raise Exception

    def getFormAndTitle(self, profileType):
        if profileType not in self.profiles:
            return None, None

        formClass = self.profiles[profileType]['form']
        formTitle = self.profiles[profileType]['title']
        form = formClass(self.request.POST or None)
        return form, formTitle

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profileType = self.getRequestedProfileType()
        form, formTitle = self.getFormAndTitle(profileType)
        context['form'] = form
        context['formTitle'] = formTitle
        return context

    def post(self, request, *args, **kwargs):
        profileType = self.getRequestedProfileType()
        form, _ = self.getFormAndTitle(profileType)

        if form and form.is_valid():
            profile = form.save(commit=False)
            profile.user = self.request.user

            if profileType == 'student' and self.request.POST.get('dateOfBirth'):
                dateOfBirth = datetime.strptime(self.request.POST.get('dateOfBirth'), "%Y-%m-%d")
                if utilsOperations.isBelow18(dateOfBirth):
                    profile.parent = User.objects.get(parentProfile__code__exact=self.request.POST.get('parentCode'))
            profile.save()

            messages.info(
                request,
                'Profile created successfully. There\'s couple more things to do. Familiarise with your profile.'
            )
            return redirect('profiles:settings-view')
        return self.render_to_response(self.get_context_data(form=form))


class SettingsTemplateView(TemplateView):
    template_name = "profiles/baseSettings.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setting = None
        self.profile = None
        self.tabCode = None

    def dispatch(self, request, *args, **kwargs):
        self.setting = self.getSetting()
        self.profile = self.getProfile()
        self.tabCode = self.getTabCode()
        return super().dispatch(request, *args, **kwargs)

    def getTabCode(self):
        _type = self.request.GET.get('tab')
        return 'password' if _type is None else _type.casefold()

    def getProfile(self):
        if hasattr(self.request.user, 'tutorProfile'):
            return self.request.user.tutorProfile
        elif hasattr(self.request.user, 'studentProfile'):
            return self.request.user.studentProfile
        elif hasattr(self.request.user, 'parentProfile'):
            return self.request.user.parentProfile
        raise ProfileNotFound

    def getSetting(self):
        if hasattr(self.request.user, 'tutorProfile'):
            return common.getSettingByTabCode(tutorTabs, self.getTabCode())
        elif hasattr(self.request.user, 'studentProfile'):
            return common.getSettingByTabCode(studentTabs, self.getTabCode())
        elif hasattr(self.request.user, 'parentProfile'):
            return common.getSettingByTabCode(parentTabs, self.getTabCode())
        raise ProfileNotFound

    def get_template_names(self):
        if self.setting is not None and self.setting.render == Render.TEMPLATE:
            pass
        elif self.setting is not None and self.setting.render == Render.FORM:
            return 'profiles/baseSettings.html'
        raise Exception

    def getForm(self, *args):
        if self.setting is not None and self.setting.code == 'password' and self.setting.render == Render.FORM:
            return CustomPasswordChangeForm(*args)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.getForm(self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context.get('form')#(self.request.user, self.request.POST or None)
        if form and form.is_valid():
            pass
        return self.render_to_response(context)
