from datetime import datetime

from django.views.generic import TemplateView


class CreateProfileTemplateViewApi(TemplateView):

    def __init__(self, **kwargs):
        super().__init__()
        self.today = datetime.today().date()

    def getRequestedProfileType(self):
        _type = self.request.GET.get('type')
        return _type if _type is None else _type.casefold()

    def get_template_names(self):
        profileType = self.getRequestedProfileType()

        if profileType is None:
            return 'profiles/selectProfileTemplate.html'
        elif profileType == 'tutor':
            return 'profiles/createTutorProfile.html'
        elif profileType == 'parent':
            return 'profiles/createParentProfile.html'
        elif profileType == 'student':
            return 'profiles/createStudentProfile.html'

        raise NotImplementedError

    def handleStudentProfile(self):
        pass

    def handleParentProfile(self):
        pass

    def handleTutorProfile(self):
        pass

    def post(self, request, *args, **kwargs):
        pass
