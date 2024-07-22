from django.contrib import admin

from accounts.models import (
    TutorProfile,
    StudentProfile,
    ParentProfile,
    Education,
    TutorQualification,
    SubjectOffered,
    GetInTouch
)

admin.site.register(TutorProfile)
admin.site.register(StudentProfile)
admin.site.register(ParentProfile)
admin.site.register(Education)
admin.site.register(TutorQualification)
admin.site.register(SubjectOffered)
admin.site.register(GetInTouch)
