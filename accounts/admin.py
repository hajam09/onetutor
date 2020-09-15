from django.contrib import admin
from .models import StudentProfile, TutorProfile, Countries

admin.site.register(StudentProfile)
admin.site.register(TutorProfile)
admin.site.register(Countries)