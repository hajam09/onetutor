from django.contrib import admin

from core.models import (
    Question,
    Response,
    TutorReview,
    Lesson
)

admin.site.register(Question)
admin.site.register(Response)
admin.site.register(TutorReview)
admin.site.register(Lesson)
