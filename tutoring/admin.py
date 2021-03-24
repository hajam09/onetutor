from django.contrib import admin
from tutoring.models import QAComment
from tutoring.models import QuestionAnswer
from tutoring.models import TutorReview

admin.site.register(QAComment)
admin.site.register(QuestionAnswer)
admin.site.register(TutorReview)