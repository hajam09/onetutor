from accounts.models import TutorProfile


def getTutorsAverageRating(tutor: TutorProfile):
    tutorReviewsObjects = tutor.user.tutorReviews
    outOfPoints = tutorReviewsObjects.count() * 5
    sumOfRating = sum([i.rating for i in tutorReviewsObjects.all()])

    try:
        averageRating = sumOfRating * 5 / outOfPoints
        roundedRating = round(averageRating * 2) / 2
    except ZeroDivisionError:
        roundedRating = 0

    return int(roundedRating)
