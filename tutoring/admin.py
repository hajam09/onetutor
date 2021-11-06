from django.contrib import admin
from tutoring.models import Availability
from tutoring.models import QuestionAnswerComment
from tutoring.models import QuestionAnswer
from tutoring.models import TutorReview

admin.site.register(Availability)
admin.site.register(QuestionAnswerComment)
admin.site.register(QuestionAnswer)
admin.site.register(TutorReview)