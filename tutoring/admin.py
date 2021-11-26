from django.contrib import admin

from tutoring.models import Availability
from tutoring.models import Feature
from tutoring.models import Lesson
from tutoring.models import Payment
from tutoring.models import PaymentMethod
from tutoring.models import QuestionAnswer
from tutoring.models import QuestionAnswerComment
from tutoring.models import TutorReview

admin.site.register(Availability)
admin.site.register(QuestionAnswerComment)
admin.site.register(QuestionAnswer)
admin.site.register(Feature)
admin.site.register(TutorReview)
admin.site.register(Lesson)
admin.site.register(Payment)
admin.site.register(PaymentMethod)
