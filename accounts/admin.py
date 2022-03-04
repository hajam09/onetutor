from django.contrib import admin

from accounts.forms import TutorProfileForm
from accounts.models import Countries
from accounts.models import Education
from accounts.models import GetInTouch
from accounts.models import ParentProfile
from accounts.models import SocialConnection
from accounts.models import StudentProfile
from accounts.models import Subject
from accounts.models import TutorProfile


class GetInTouchAdmin(admin.ModelAdmin):
    readonly_fields = ('dateTime',)
    list_display = ['id', 'fullName', 'email', 'subject', 'message', 'dateTime']
    list_filter = ['fullName', 'email', 'subject', 'message', 'dateTime']
    list_editable = ['fullName', 'email', 'subject']
    search_fields = ['fullName', 'email', 'subject', 'message', 'dateTime']
    # list_editable = [field.name for field in GetInTouch._meta.get_fields()]


class TutorProfileAdmin(admin.ModelAdmin):
    form = TutorProfileForm


admin.site.register(Countries)
admin.site.register(GetInTouch, GetInTouchAdmin)
admin.site.register(Education)
admin.site.register(SocialConnection)
admin.site.register(StudentProfile)
admin.site.register(Subject)
admin.site.register(ParentProfile)
admin.site.register(TutorProfile, TutorProfileAdmin)
