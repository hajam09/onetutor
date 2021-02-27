from accounts.models import Countries
from accounts.models import SocialConnection
from accounts.models import StudentProfile
from accounts.models import Subject
from accounts.models import TutorProfile
from accounts.models import UserSession
from django.contrib import admin

admin.site.register(Countries)
admin.site.register(SocialConnection)
admin.site.register(StudentProfile)
admin.site.register(Subject)
admin.site.register(TutorProfile)
admin.site.register(UserSession)