import json
import math
import random
import string
from datetime import datetime
from http import HTTPStatus

import pandas as pd
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify
from sklearn.preprocessing import MinMaxScaler

from forum.models import Community, ForumComment
from forum.models import Forum


def mainpage(request):

    if request.method == "POST" and "createCommunity" in request.POST:

        title = request.POST['title']
        url = slugify(title + " " + randomString())
        tags = ', '.join([i.capitalize() for i in request.POST.getlist('tags')])
        description = request.POST['description']

        try:
            banner = request.FILES["banner"]
        except KeyError as e:
            banner = None

        try:
            logo = request.FILES["logo"]
        except KeyError as e:
            logo = None

        Community.objects.create(
            creator=request.user,
            title=title,
            url=url,
            tags=tags,
            description=description,
            banner=banner,
            logo=logo
        )

        messages.success(
            request,
            "WOW! It's a new community. Create a sub-forum, upload stuff or do what ever you want. Sky's the limit!"
        )
        return redirect('forum:communityPage', communityUrl=url)

    # TODO: Retrieve specific fields from the objects rather than all the related objects.
    forums = Forum.objects.all().select_related('creator', 'community').prefetch_related('likes',
                                                                                         'dislikes',
                                                                                         'watchers',
                                                                                         'forumComments').order_by('-id')
    forumsPagination = [forums[i:i + 15] for i in range(0, len(forums), 15)]

    if request.is_ajax():
        functionality = request.GET.get('functionality', None)

        if functionality == "fetchForums":
            nextIndex = request.GET.get('nextIndex', None)

            try:
                nextForums = forumsPagination[int(nextIndex)]
            except IndexError:
                response = {
                    "statusCode": HTTPStatus.NO_CONTENT
                }
                return JsonResponse(response)

            forums = [
                {
                    'id': e.id,
                    'communityUrl': e.community.url,
                    'forumUrl': e.url,
                    'votes': intCompromise(e.likes.count() - e.dislikes.count()),
                    'creatorFullName': e.creator.get_full_name(),
                    'date': vanilla_JS_date_conversion(e.createdAt),
                    'title': e.title.replace("\n", "<br />"),
                    'image': str(e.image),
                    'description': e.description.replace("\n", "<br />"),
                    'commentCount': e.forumComments.count(),
                    'canEdit': True if e.creator == request.user else False,
                    'isWatching': True if request.user in e.watchers.all() else False,
                    'watchingCount': e.watchers.count(),
                }
                for e in nextForums
            ]

            response = {
                "statusCode": HTTPStatus.OK,
                "forums": forums
            }
            return JsonResponse(response)

    initialForum = [
        {
            'id': e.id,
            'communityUrl': e.community.url,
            'forumUrl': e.url,
            'votes': intCompromise(e.likes.count() - e.dislikes.count()),
            'creatorFullName': e.creator.get_full_name(),
            'date': vanilla_JS_date_conversion(e.createdAt),
            'title': e.title.replace("\n", "<br />"),
            'image': str(e.image),
            'description': e.description.replace("\n", "<br />"),
            'commentCount': e.forumComments.count(),
            'canEdit': True if e.creator == request.user else False,
            'isWatching': True if request.user in e.watchers.all() else False,
            'watchingCount': e.watchers.count(),
        }
        for e in forumsPagination[0] if forumsPagination
    ]

    context = {
        "forums": json.dumps(initialForum)
    }
    return render(request, 'forum/mainpage.html', context)


def communityPage(request, communityUrl):

    try:
        community = Community.objects.prefetch_related('members').get(url=communityUrl)
    except Community.DoesNotExist:
        raise Http404

    if request.method == "POST" and "startForum" in request.POST:

        title = request.POST['title']
        description = request.POST['description']
        url = slugify(title + " " + randomString())

        try:
            image = request.FILES["image"]
        except KeyError as e:
            image = None

        Forum.objects.create(
            community=community,
            creator=request.user,
            title=title,
            url=url,
            description=description,
            image=image
        )
        return redirect('forum:forumPage', communityUrl=communityUrl, forumUrl=url)

    forums = Forum.objects.filter(community=community).order_by('-id').select_related('creator').prefetch_related('likes', 'dislikes')
    forumsPagination = [forums[i:i + 15] for i in range(0, len(forums), 15)]

    if request.is_ajax():
        functionality = request.GET.get('functionality', None)

        if functionality == "joinCommunity":
            community.members.add(request.user)

            response = {
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response)

        elif functionality == "leaveCommunity":
            community.members.remove(request.user)

            response = {
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response)

        elif functionality == "upvoteForum":
            id = request.GET.get('forumId', None)
            forum = next((f for f in forums if str(f.id) == id), None)

            if forum is None:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": 'Error up voting this forum!',
                }
                return JsonResponse(response)

            forum.like(request)

            response = {
                "statusCode": HTTPStatus.OK,
                "likeCount": forum.likes.count(),
                "dislikeCount": forum.dislikes.count(),
            }
            return JsonResponse(response)

        elif functionality == "downvoteForum":
            id = request.GET.get('forumId', None)
            forum = next((f for f in forums if str(f.id) == id), None)

            if forum is None:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": 'Error up voting this forum!',
                }
                return JsonResponse(response)

            forum.dislike(request)

            response = {
                "statusCode": HTTPStatus.OK,
                "likeCount": forum.likes.count(),
                "dislikeCount": forum.dislikes.count(),
            }
            return JsonResponse(response)

        if functionality == "fetchForums":
            nextIndex = request.GET.get('nextIndex', None)

            try:
                nextForums = forumsPagination[int(nextIndex)]
            except IndexError:
                response = {
                    "statusCode": HTTPStatus.NO_CONTENT
                }
                return JsonResponse(response)

            forums = [
                {
                    'id': e.id,
                    'votes': intCompromise(e.likes.count() - e.dislikes.count()),
                    'creatorFullName': e.creator.get_full_name(),
                    'date': vanilla_JS_date_conversion(e.createdAt),
                    'title': e.title.replace("\n", "<br />"),
                    'image': str(e.image),
                    'description': e.description.replace("\n", "<br />"),
                    'commentCount': e.forumComments.count(),
                    'canEdit': True if e.creator == request.user else False,
                }
                for e in nextForums
            ]

            response = {
                "statusCode": HTTPStatus.OK,
                "forums": forums
            }
            return JsonResponse(response)

        raise Exception("Unknown functionality in communityPage")

    context = {
        "community": community,
        "forums": forumsPagination[0] if len(forumsPagination) > 0 else [],
        "inCommunity": True if request.user in community.members.all() else False
    }
    return render(request, "forum/communityPage.html", context)


def forumPage(request, communityUrl, forumUrl):
    try:
        forum = Forum.objects.select_related('creator', 'community').prefetch_related('watchers',
                                                                                      'likes',
                                                                                      'dislikes',
                                                                                      'forumComments__likes',
                                                                                      'forumComments__dislikes',
                                                                                      'forumComments__creator',
                                                                                      'forumComments__reply').get(url=forumUrl)
    except Forum.DoesNotExist:
        raise Http404

    if forum.community.url != communityUrl:
        # Forum's community is not the same as the expected community from url.
        return HttpResponse("<h1>Bad Request. Looks like you are messing with the url.</h1>")

    if request.is_ajax():
        functionality = request.GET.get('functionality', None)

        if functionality == "joinCommunity":
            forum.community.members.add(request.user)

            response = {
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response)

        elif functionality == "leaveCommunity":
            forum.community.members.remove(request.user)

            response = {
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response)

        elif functionality == "upvoteForum":
            forum.like(request)

            response = {
                "statusCode": HTTPStatus.OK,
                "votes": intCompromise(forum.likes.count() - forum.dislikes.count())
            }
            return JsonResponse(response)

        elif functionality == "downvoteForum":
            forum.dislike(request)

            response = {
                "statusCode": HTTPStatus.OK,
                "votes": intCompromise(forum.likes.count() - forum.dislikes.count())
            }
            return JsonResponse(response)

        elif functionality == "likeComment":
            id = request.GET.get('id', None)
            comment = next((c for c in forum.forumComments.all() if str(c.id) == id), None)

            if comment is None:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": 'Sorry. Something went wrong!',
                }
                return JsonResponse(response)

            comment.like(request)

            response = {
                "statusCode": HTTPStatus.OK,
                "likeCount": comment.likes.count(),
                "dislikeCount": comment.dislikes.count(),
            }
            return JsonResponse(response)

        elif functionality == "dislikeComment":
            id = request.GET.get('id', None)
            comment = next((c for c in forum.forumComments.all() if str(c.id) == id), None)

            if comment is None:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": 'Sorry. Something went wrong!',
                }
                return JsonResponse(response)

            comment.dislike(request)

            response = {
                "statusCode": HTTPStatus.OK,
                "likeCount": comment.likes.count(),
                "dislikeCount": comment.dislikes.count(),
            }
            return JsonResponse(response)

        elif functionality == "deleteForumComment":
            id = request.GET.get('id', None)
            comment = next((c for c in forum.forumComments.all() if str(c.id) == id), None)

            if comment is None:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                }
                return JsonResponse(response)

            comment.delete()

            response = {
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response)

        elif functionality == "createForumComment":
            comment = request.GET.get('comment', None)
            masterComment = request.GET.get('masterCommentId', None)

            if masterComment is not None:
                masterComment = ForumComment.objects.get(id=int(masterComment))

            forumComment = ForumComment.objects.create(
                forum=forum,
                creator=request.user,
                description=comment,
                reply=masterComment,
            )
            forum = [
                {
                    'id': forumComment.pk,
                    'creatorFullName': forumComment.creator.get_full_name(),
                    'edited': forumComment.edited,
                    'comment': forumComment.description.replace("\n", "<br />"),
                    'likeCount': forumComment.likes.count(),
                    'dislikeCount': forumComment.dislikes.count(),
                    'canEdit': True if forumComment.creator == request.user else False,
                    'masterCommentId': forumComment.reply.pk if forumComment.reply else None
                }
            ]
            response = {
                "statusCode": HTTPStatus.OK,
                "forum": forum
            }
            return JsonResponse(response)

    forumJson = [
        {
            'id': forum.id,
            'communityUrl': forum.community.url,
            'forumUrl': forum.url,
            'votes': intCompromise(forum.likes.count() - forum.dislikes.count()),
            'creatorFullName': forum.creator.get_full_name(),
            'date': vanilla_JS_date_conversion(forum.createdAt),
            'title': forum.title.replace("\n", "<br />"),
            'image': str(forum.image),
            'description': forum.description.replace("\n", "<br />"),
            'commentCount': forum.forumComments.count(),
            'canEdit': True if forum.creator == request.user else False,
            'isWatching': True if request.user in forum.watchers.all() else False,
            'watchingCount': forum.watchers.count(),
        }
    ]

    forumComments = [
        {
            'id': i.pk,
            'creatorFullName': i.creator.get_full_name(),
            'edited': i.edited,
            'comment': i.description.replace("\n", "<br />"),
            'likeCount': i.likes.count(),
            'dislikeCount': i.dislikes.count(),
            'canEdit': True if i.creator == request.user else False,
            'masterCommentId': i.reply.pk if i.reply else None
        }
        for i in forum.forumComments.all()
    ]

    context = {
        "forum": json.dumps(forumJson),
        "community": forum.community,
        "forumComments": json.dumps(forumComments),
        "inCommunity": True if request.user in forum.community.members.all() else False
    }
    return render(request, "forum/forumpage.html", context)


def GetPopularPosts():
    """
        Return the most popular posts created on any community.
        Attributes to determine the popularity:
            forum vote, comment count, watch count and creation date is today (future).
    """
    if Forum.objects.count() == 0:
        return []

    allForums = Forum.objects.all().prefetch_related('likes', 'dislikes', 'watchers', 'forums').select_related(
        'creator', 'community')

    forumDict = [{
        'id': e.pk,
        'forumVote': e.likes.count() - e.dislikes.count(),
        'commentCount': e.forums.all().count(),
        'watchCount': e.watchers.all().count()
    } for e in allForums]

    df = pd.DataFrame(forumDict)
    scaling = MinMaxScaler()
    divedent = 100 / 3

    forumScaled = scaling.fit_transform(df[['forumVote', 'commentCount', 'watchCount']])
    forumNormalized = pd.DataFrame(forumScaled, columns=['forumVote', 'commentCount', 'watchCount'])

    df[['normalizedForumVote', 'normalizedCommentCount', 'normalizedWatchCount']] = forumNormalized
    df['score'] = df['normalizedForumVote'] * divedent + df['normalizedCommentCount'] * divedent + df[
        'normalizedWatchCount'] * divedent

    forumScoredDataFrame = df.sort_values(['score'], ascending=False)
    forumId = list(forumScoredDataFrame['id'])
    # return [allForums[i-1] for i in forumId] # use when pk is in order.
    return [j for i in forumId for j in allForums if i == j.pk]


def randomString(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def intCompromise(interger):
    millNames = ['', ' k', ' m', ' b', ' t']
    floatNumber = float(interger)
    milliDx = max(0,
                  min(len(millNames) - 1, int(math.floor(0 if floatNumber == 0 else math.log10(abs(floatNumber)) / 3))))
    return '{:.0f}{}'.format(floatNumber / 10 ** (3 * milliDx), millNames[milliDx])


def vanilla_JS_date_conversion(pyDate):
    date = pyDate.strftime("%b. %d, %Y,")
    time = datetime.strptime(pyDate.strftime("%H:%M"), "%H:%M")
    time = time.strftime("%I:%M %p").lower().replace("pm", "p.m.").replace("am", "a.m.")
    return str(date + " " + time)


def communityOperationsAPI(request, communityUrl):
    response = {
        'statusCode': HTTPStatus.OK
    }
    return JsonResponse(response)


def forumOperationsAPI(request, communityUrl, forumUrl):
    response = {
        'statusCode': HTTPStatus.OK
    }
    return JsonResponse(response)


def forumCommentOperationsAPI(request, communityUrl, forumUrl, commentId):
    response = {
        'statusCode': HTTPStatus.OK
    }
    return JsonResponse(response)
