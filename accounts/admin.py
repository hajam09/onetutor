from django.contrib import admin
from .models import StudentProfile, TutorProfile, Countries, Subject, SocialConnection, UserSession

admin.site.register(StudentProfile)
admin.site.register(TutorProfile)
admin.site.register(Countries)
admin.site.register(Subject)
admin.site.register(SocialConnection)
admin.site.register(UserSession)