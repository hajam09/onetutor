from django.contrib import admin

from tutoring.models import Availability
from tutoring.models import Component
from tutoring.models import ComponentGroup
from tutoring.models import Lesson
from tutoring.models import Payment
from tutoring.models import QuestionAnswer
from tutoring.models import QuestionAnswerComment
from tutoring.models import TutorReview


class LessonAdmin(admin.ModelAdmin):
    raw_id_fields = ['tutor', 'student']
    list_display = ['tutor', 'student', 'hoursTaught', 'dateTime', 'points', 'amount']
    list_filter = ['tutor', 'student', 'hoursTaught', 'dateTime', 'points', 'amount']
    search_fields = ['tutor']


class ComponentInline(admin.TabularInline):
    model = Component


class ComponentGroupAdmin(admin.ModelAdmin):
    inlines = [ComponentInline]


admin.site.register(Availability)
admin.site.register(Component)
admin.site.register(ComponentGroup, ComponentGroupAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Payment)
admin.site.register(QuestionAnswer)
admin.site.register(QuestionAnswerComment)
admin.site.register(TutorReview)
