from django.contrib import admin

from profiles.models import (
    TutorProfile,
    StudentProfile,
    ParentProfile,
    Education,
    TutorQualification,
    SubjectOffered,
)

admin.site.register(TutorProfile)
admin.site.register(StudentProfile)
admin.site.register(ParentProfile)
admin.site.register(Education)
admin.site.register(TutorQualification)
admin.site.register(SubjectOffered)
