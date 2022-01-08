import json
import math
import random
import string
from http import HTTPStatus

import pandas as pd
from django.contrib import messages
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify
from sklearn.preprocessing import MinMaxScaler

from forum.models import Community
from forum.models import Forum
from forum.models import ForumComment
from onetutor.operations import dateOperations


def mainpage(request):

    if request.method == "POST" and "createCommunity" in request.POST:

        title = request.POST['title']
        url = slugify(title + " " + randomString())
        tags = ', '.join([i.capitalize() for i in request.POST.getlist('tags')])
        description = request.POST['description']

        try:
            banner = request.FILES["banner"]
        except KeyError:
            banner = None

        try:
            logo = request.FILES["logo"]
        except KeyError:
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

    paginator = Paginator(forums, 15)
    pageStartNumber = 1

    if request.is_ajax():
        functionality = request.GET.get('functionality', None)

        if functionality == "fetchForums":
            nextIndex = int(request.GET.get('nextIndex', None)) + pageStartNumber

            try:
                nextForums = paginator.page(nextIndex)
            except EmptyPage:
                response = {
                    "statusCode": HTTPStatus.NO_CONTENT
                }
                return JsonResponse(response)

            forums = [
                forumComponentJson(request, e)
                for e in nextForums
            ]

            response = {
                "statusCode": HTTPStatus.OK,
                "forums": forums
            }
            return JsonResponse(response)

    initialForum = [
        forumComponentJson(request, e)
        for e in paginator.page(1) if paginator.num_pages > 0
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
        except KeyError:
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
    paginator = Paginator(forums, 15)
    pageStartNumber = 1

    if request.is_ajax():
        functionality = request.GET.get('functionality', None)

        if functionality == "fetchForums":
            nextIndex = int(request.GET.get('nextIndex', None)) + pageStartNumber

            try:
                nextForums = paginator.page(nextIndex)
            except EmptyPage:
                response = {
                    "statusCode": HTTPStatus.NO_CONTENT
                }
                return JsonResponse(response)

            forums = [
                forumComponentJson(request, e)
                for e in nextForums
            ]

            response = {
                "statusCode": HTTPStatus.OK,
                "forums": forums
            }
            return JsonResponse(response)

        raise Exception("Unknown functionality in communityPage")

    initialForum = [
        forumComponentJson(request, e)
        for e in paginator.page(1) if paginator.num_pages > 0
    ]

    context = {
        "community": community,
        "forums": json.dumps(initialForum),
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
                                                                                      'forumComments__reply').get(url=forumUrl, community__url=communityUrl)
    except Forum.DoesNotExist:
        raise Http404

    if forum.community.url != communityUrl:
        # Forum's community is not the same as the expected community from url.
        return HttpResponse("<h1>Bad Request. Looks like you are messing with the url.</h1>")

    if request.is_ajax():
        functionality = request.GET.get('functionality', None)

        if functionality == "deleteForumComment":
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
        forumComponentJson(request, forum)
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
    return render(request, "forum/forumPage.html", context)


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


def forumComponentJson(request, e):
    response = {
        'forumId': e.id,
        'communityId': e.community.id,
        'forumUrl': e.url,
        'communityUrl': e.community.url,
        'votes': intCompromise(e.likes.count() - e.dislikes.count()),
        'creatorFullName': e.creator.get_full_name(),
        'date': dateOperations.humanizePythonDate(e.createdAt),
        'title': e.title.replace("\n", "<br />"),
        'image': str(e.image),
        'description': e.description.replace("\n", "<br />"),
        'commentCount': e.forumComments.count(),
        'canEdit': True if e.creator == request.user else False,
        'isWatching': True if request.user in e.watchers.all() else False,
        'watchingCount': e.watchers.count(),
    }
    return response


def communityOperationsAPI(request, communityId):

    if not request.user.is_authenticated:
        response = {
            "statusCode": HTTPStatus.UNAUTHORIZED,
            "message": "Please login to perform this action."
        }
        return JsonResponse(response)

    try:
        community = Community.objects.get(id=communityId)
    except Community.DoesNotExist:
        response = {
            'statusCode': HTTPStatus.NOT_FOUND,
            'message': 'Could not find a community with id {}'.format(communityId)
        }
        return JsonResponse(response)

    functionality = request.GET.get('functionality', None)
    if functionality == "joinOrLeaveCommunity":

        if request.user not in community.members.all():
            community.members.add(request.user)
            inCommunity = True
        else:
            community.members.remove(request.user)
            inCommunity = False

        response = {
            "inCommunity": inCommunity,
            "statusCode": HTTPStatus.OK
        }
        return JsonResponse(response)

    response = {
        'statusCode': HTTPStatus.OK
    }
    return JsonResponse(response)


def forumOperationsAPI(request, forumId):

    if not request.user.is_authenticated:
        response = {
            "statusCode": HTTPStatus.UNAUTHORIZED,
            "message": "Please login to perform this action."
        }
        return JsonResponse(response)

    try:
        forum = Forum.objects.get(id=forumId)
    except Forum.DoesNotExist:
        response = {
            'statusCode': HTTPStatus.NOT_FOUND,
            'message': 'Could not find a forum with id {}'.format(forumId)
        }
        return JsonResponse(response)

    functionality = request.GET.get('functionality', None)
    if functionality == "watchUnwatchForum":

        if request.user not in forum.watchers.all():
            forum.watchers.add(request.user)
            isWatching = True
        else:
            forum.watchers.remove(request.user)
            isWatching = False

        response = {
            "isWatching": isWatching,
            "newWatchCount": forum.watchers.count(),
            "statusCode": HTTPStatus.OK
        }
        return JsonResponse(response)

    elif functionality == "upVoteForum":

        forum.like(request)

        response = {
            "statusCode": HTTPStatus.OK,
            "likeCount": forum.likes.count(),
            "dislikeCount": forum.dislikes.count(),
        }
        return JsonResponse(response)

    elif functionality == "downVoteForum":

        forum.dislike(request)

        response = {
            "statusCode": HTTPStatus.OK,
            "likeCount": forum.likes.count(),
            "dislikeCount": forum.dislikes.count(),
        }
        return JsonResponse(response)

    response = {
        'statusCode': HTTPStatus.OK
    }
    return JsonResponse(response)


def forumCommentOperationsAPI(request, commentId):

    if not request.user.is_authenticated:
        response = {
            "statusCode": HTTPStatus.UNAUTHORIZED,
            "message": "Please login to perform this action."
        }
        return JsonResponse(response)

    try:
        forumComment = ForumComment.objects.get(id=commentId)
    except ForumComment.DoesNotExist:
        response = {
            'statusCode': HTTPStatus.NOT_FOUND,
            'message': 'Could not find a forum comment with id {}'.format(commentId)
        }
        return JsonResponse(response)

    functionality = request.GET.get('functionality', None)

    if functionality == "likeForumComment":

        forumComment.like(request)

        response = {
            "statusCode": HTTPStatus.OK,
            "likeCount": forumComment.likes.count(),
            "dislikeCount": forumComment.dislikes.count(),
        }
        return JsonResponse(response)

    elif functionality == "dislikeForumComment":
        forumComment.dislike(request)

        response = {
            "statusCode": HTTPStatus.OK,
            "likeCount": forumComment.likes.count(),
            "dislikeCount": forumComment.dislikes.count(),
        }
        return JsonResponse(response)

    response = {
        'statusCode': HTTPStatus.OK
    }
    return JsonResponse(response)
