from django.contrib import admin

from core.models import (
    Availability,
    ComponentGroup,
    Component,
    Question,
    Response,
    TutorReview,
    Lesson
)

admin.site.register(Availability)
admin.site.register(ComponentGroup)
admin.site.register(Component)
admin.site.register(Question)
admin.site.register(Response)
admin.site.register(TutorReview)
admin.site.register(Lesson)
