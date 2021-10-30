from accounts.models import Countries
from accounts.models import Education
from accounts.models import SocialConnection
from accounts.models import StudentProfile
from accounts.models import Subject
from accounts.models import TutorProfile
from django.contrib import admin

admin.site.register(Countries)
admin.site.register(Education)
admin.site.register(SocialConnection)
admin.site.register(StudentProfile)
admin.site.register(Subject)
admin.site.register(TutorProfile)