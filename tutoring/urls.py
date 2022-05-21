from django.urls import path

from tutoring import views
from tutoring.api import QuestionAnswerCommentObjectApiEventVersion1Component
from tutoring.api import QuestionAnswerCommentObjectLikeOrDislikeApiEventVersion1Component
from tutoring.api import QuestionAnswerObjectApiEventVersion1Component
from tutoring.api import QuestionAnswerObjectLikeOrDislikeApiEventVersion1Component
from tutoring.api import TutorReviewObjectApiEventVersion1Component
from tutoring.api import TutorReviewObjectLikeOrDislikeApiEventVersion1Component

app_name = "tutoring"

urlpatterns = [
    path('', views.mainpage, name='mainpage'),
    path('tutor-profile/<slug:url>/', views.viewTutorProfile, name='view-tutor-profile'),
    path('student-profile/<int:url>/', views.viewStudentProfile, name='view-student-profile'),
    path('tutors-questions/', views.tutorsQuestions, name='tutors-questions'),
    path('question-answer-thread/<int:questionId>/', views.questionAnswerThread, name='question-answer-thread'),
]

# api
urlpatterns += [
    path(
        'tutoring/api/v1/questionAnswerObjectApiEventVersion1Component/<int:id>',
        QuestionAnswerObjectApiEventVersion1Component.as_view(),
        name='questionAnswerObjectApiEventVersion1Component'
    ),
    path(
        'tutoring/api/v1/questionAnswerObjectApiEventVersion1Component',
        QuestionAnswerObjectApiEventVersion1Component.as_view(),
        name='questionAnswerObjectApiEventVersion1Component'
    ),
    path(
        'tutoring/api/v1/tutorReviewObjectApiEventVersion1Component/<int:id>',
        TutorReviewObjectApiEventVersion1Component.as_view(),
        name='tutorReviewObjectApiEventVersion1Component'
    ),
    path(
        'tutoring/api/v1/tutorReviewObjectApiEventVersion1Component',
        TutorReviewObjectApiEventVersion1Component.as_view(),
        name='tutorReviewObjectApiEventVersion1Component'
    ),
    path(
        'tutoring/api/v1/questionAnswerObjectLikeOrDislikeApiEventVersion1Component/<int:id>/<slug:action>',
        QuestionAnswerObjectLikeOrDislikeApiEventVersion1Component.as_view(),
        name='questionAnswerObjectLikeOrDislikeApiEventVersion1Component'
    ),
    path(
        'tutoring/api/v1/tutorReviewObjectLikeOrDislikeApiEventVersion1Component/<int:id>/<slug:action>',
        TutorReviewObjectLikeOrDislikeApiEventVersion1Component.as_view(),
        name='TutorReviewObjectLikeOrDislikeApiEventVersion1Component'
    ),
    path(
        'tutoring/api/v1/questionAnswerCommentObjectApiEventVersion1Component/<int:id>',
        QuestionAnswerCommentObjectApiEventVersion1Component.as_view(),
        name='questionAnswerCommentObjectApiEventVersion1Component'
    ),
    path(
        'tutoring/api/v1/questionAnswerCommentObjectApiEventVersion1Component',
        QuestionAnswerCommentObjectApiEventVersion1Component.as_view(),
        name='questionAnswerCommentObjectApiEventVersion1Component'
    ),
    path(
        'tutoring/api/v1/questionAnswerCommentObjectLikeOrDislikeApiEventVersion1Component/<int:id>/<slug:action>',
        QuestionAnswerCommentObjectLikeOrDislikeApiEventVersion1Component.as_view(),
        name='questionAnswerCommentObjectLikeOrDislikeApiEventVersion1Component'
    ),
]
