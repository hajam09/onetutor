from django.urls import path

from tutoring import views
from tutoring.api import ComponentObjectsApiEventVersion1Component, TutorListingApiEventVersion1Component, \
    EducationObjectApiEventVersion1Component, AvailabilityObjectApiEventVersion1Component
from tutoring.api import QuestionAnswerCommentObjectApiEventVersion1Component
from tutoring.api import QuestionAnswerCommentObjectLikeOrDislikeApiEventVersion1Component
from tutoring.api import QuestionAnswerObjectApiEventVersion1Component
from tutoring.api import QuestionAnswerObjectLikeOrDislikeApiEventVersion1Component
from tutoring.api import TutorReviewObjectApiEventVersion1Component
from tutoring.api import TutorReviewObjectLikeOrDislikeApiEventVersion1Component

app_name = "tutoring"

urlpatterns = [
    path("", views.indexView, name="index-view"),
    path("tutor-profile/<slug:url>/", views.tutorProfileView, name="tutor-profile-view"),
    path('tutor-profile2/<slug:url>/', views.viewTutorProfile, name='view-tutor-profile2'),
    path('student-profile/<int:url>/', views.viewStudentProfile, name='view-student-profile'),
    path('tutors-questions/', views.tutorsQuestions, name='tutors-questions'),
    path('question-answer-thread/<int:questionId>/', views.questionAnswerThread, name='question-answer-thread'),
]

# api
urlpatterns += [
    path(
        'api/v1/tutorListingApiEventVersion1Component',
        TutorListingApiEventVersion1Component.as_view(),
        name='tutorListingApiEventVersion1Component'
    ),
    path(
        'api/v1/educationObjectApiEventVersion1Component',
        EducationObjectApiEventVersion1Component.as_view(),
        name='educationObjectApiEventVersion1Component'
    ),
    path(
        'api/v1/availabilityObjectApiEventVersion1Component',
        AvailabilityObjectApiEventVersion1Component.as_view(),
        name='availabilityObjectApiEventVersion1Component'
    ),
    path(
        'api/v1/questionAnswerObjectApiEventVersion1Component/<int:id>',
        QuestionAnswerObjectApiEventVersion1Component.as_view(),
        name='questionAnswerObjectApiEventVersion1Component'
    ),
    path(
        'api/v1/questionAnswerObjectApiEventVersion1Component',
        QuestionAnswerObjectApiEventVersion1Component.as_view(),
        name='questionAnswerObjectApiEventVersion1Component'
    ),
    path(
        'api/v1/tutorReviewObjectApiEventVersion1Component/<int:id>',
        TutorReviewObjectApiEventVersion1Component.as_view(),
        name='tutorReviewObjectApiEventVersion1Component'
    ),
    path(
        'api/v1/tutorReviewObjectApiEventVersion1Component',
        TutorReviewObjectApiEventVersion1Component.as_view(),
        name='tutorReviewObjectApiEventVersion1Component'
    ),
    path(
        'api/v1/questionAnswerObjectLikeOrDislikeApiEventVersion1Component/<int:id>/<slug:action>',
        QuestionAnswerObjectLikeOrDislikeApiEventVersion1Component.as_view(),
        name='questionAnswerObjectLikeOrDislikeApiEventVersion1Component'
    ),
    path(
        'api/v1/tutorReviewObjectLikeOrDislikeApiEventVersion1Component/<int:id>/<slug:action>',
        TutorReviewObjectLikeOrDislikeApiEventVersion1Component.as_view(),
        name='TutorReviewObjectLikeOrDislikeApiEventVersion1Component'
    ),
    path(
        'api/v1/questionAnswerCommentObjectApiEventVersion1Component/<int:id>',
        QuestionAnswerCommentObjectApiEventVersion1Component.as_view(),
        name='questionAnswerCommentObjectApiEventVersion1Component'
    ),
    path(
        'api/v1/questionAnswerCommentObjectApiEventVersion1Component',
        QuestionAnswerCommentObjectApiEventVersion1Component.as_view(),
        name='questionAnswerCommentObjectApiEventVersion1Component'
    ),
    path(
        'api/v1/questionAnswerCommentObjectLikeOrDislikeApiEventVersion1Component/<int:id>/<slug:action>',
        QuestionAnswerCommentObjectLikeOrDislikeApiEventVersion1Component.as_view(),
        name='questionAnswerCommentObjectLikeOrDislikeApiEventVersion1Component'
    ),
    path(
        'api/v1/componentObjectsApiEventVersion1Component',
        ComponentObjectsApiEventVersion1Component.as_view(),
        name='componentObjectsApiEventVersion1Component'
    ),
]
