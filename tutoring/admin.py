from django.contrib import admin
from .models import QuestionAnswer, QAComment

admin.site.register(QuestionAnswer)
admin.site.register(QAComment)