from .models import Category, Community, Forum, ForumComment
from datetime import datetime
from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from deprecated import deprecated
import json, random
from http import HTTPStatus

def mainpage(request):

	if request.method == "POST" and "create_community" in request.POST:
		if not request.user.is_authenticated:
			return redirect('accounts:login')
		studyLevel = request.POST['studyLevel']
		category = Category.objects.get(name=studyLevel)
		title = request.POST['title']
		description = request.POST['description']
		community_url = "n/a"

		new_community = Community.objects.create(
			creator = request.user,
			community_title = title,
			community_url = community_url,
			community_description = description,
		)

		return redirect('forum:communitypage', community_id=new_community.pk)
	context = {
		"category": Category.objects.all()
	}
	return render(request, "forum/mainpage.html", context)

def communitypage(request, community_id):
	try:
		community = Community.objects.get(pk=community_id)
	except Community.DoesNotExist:
		raise Http404


	if request.method == "POST" and "create_forum" in request.POST:
		forum_title = request.POST['forum_title']
		description = request.POST['description']

		if not description and not "forum_image" in request.FILES:
			return redirect('forum:communitypage', community_id=community_id)

		try:
			forum_image = request.FILES["forum_image"]
		except KeyError as e:
			forum_image = None

		newForum = Forum.objects.create(
			community = community,
			creator = request.user,
			forum_title = forum_title,
			forum_url = 'n/a',
			forum_description = description,
			forum_image = forum_image,
		)
		return redirect('forum:communitypage', community_id=community_id)

	all_forums = Forum.objects.filter(community=community).order_by('-id')
	forums_split = [all_forums[i:i + 15] for i in range(0, len(all_forums), 15)]

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "join_community":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to join this community."
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			community.community_members.add(request.user)

			response = {
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "leave_community":
			community.community_members.remove(request.user)
			response = {
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "upvote_forum":
			# TODO: Get the forum object from the list. Manual test the implementation.
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to up vote this forum."
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			forum_id = request.GET.get('forum_id', None)

			try:
				this_forum = Forum.objects.get(id=int(forum_id))
				# next((x for x in test_list if x.value == value), None)
				# This gets the first item from the list that matches the condition, and returns None if no item matches.
				# Get the Forum object from all_forums list.
			except Forum.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND,
					"message": "We think this forum has been deleted!"
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			# list_of_liked = Forum.objects.filter(forum_likes__id=request.user.pk)
			# list_of_disliked = Forum.objects.filter(forum_dislikes__id=request.user.pk)

			# if(this_forum not in list_of_liked):
			# 	this_forum.forum_likes.add(request.user)
			# else:
			# 	this_forum.forum_likes.remove(request.user)

			# if(this_forum in list_of_disliked):
			# 	this_forum.forum_dislikes.remove(request.user)

			if(request.user not in this_forum.forum_likes.all()):
				this_forum.forum_likes.add(request.user)
			else:
				this_forum.forum_likes.remove(request.user)

			if(request.user in this_forum.forum_dislikes.all()):
				this_forum.forum_dislikes.remove(request.user)

			response = {
				"status_code": HTTPStatus.OK,
				"this_forum": serializers.serialize("json", [this_forum,]),
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "downvote_forum":
			# TODO: Get the forum object from the list. Manual test the implementation.
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to down vote this forum."
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			forum_id = request.GET.get('forum_id', None)

			try:
				this_forum = Forum.objects.get(id=int(forum_id))
				# next((x for x in test_list if x.value == value), None)
				# This gets the first item from the list that matches the condition, and returns None if no item matches.
				# Get the Forum object from all_forums list.
			except Forum.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND,
					"message": "We think this forum has been deleted!"
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			# list_of_liked = Forum.objects.filter(forum_likes__id=request.user.pk)
			# list_of_disliked = Forum.objects.filter(forum_dislikes__id=request.user.pk)

			# if(this_forum not in list_of_disliked):
			# 	this_forum.forum_dislikes.add(request.user)
			# else:
			# 	this_forum.forum_dislikes.remove(request.user)
				
			# if(this_forum in list_of_liked):
			# 	this_forum.forum_likes.remove(request.user)

			if(request.user not in this_forum.forum_dislikes.all()):
				this_forum.forum_dislikes.add(request.user)
			else:
				this_forum.forum_dislikes.remove(request.user)

			if(request.user in this_forum.forum_likes.all()):
				this_forum.forum_likes.remove(request.user)

			response = {
				"status_code": HTTPStatus.OK,
				"this_forum": serializers.serialize("json", [this_forum,]),
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "fetch_forums":
			next_index = request.GET.get('next_index', None)
			forum_json = []
			try:
				next_forum = forums_split[int(next_index)]
			except IndexError:
				next_forum = []
			for e in next_forum:
				forum_json.append({
						'forumId': e.id,
						'forumVotes': e.forum_likes.count() - e.forum_dislikes.count(),
						'forumCreatorFullName': e.creator.get_full_name(),
						'forumCreatedDate': vanilla_JS_date_conversion(e.created_at),
						'forumTitle': e.forum_title,
						'forumImage': str(e.forum_image),
						'forumDescription': e.forum_description,
						'forumCommentCount': ForumComment.objects.filter(forum=e).count()
					})
			response = {
				"status_code": HTTPStatus.OK,
				"forum_json": forum_json
			}
			return HttpResponse(json.dumps(response), content_type="application/json")


		raise Exception("Unknown functionality communitypage")

	context = {
		"community": community,
		"forums": forums_split[0] if len(forums_split)>0 else [],
		"in_community": True if request.user in community.community_members.all() else False
	}
	return render(request, "forum/communitypage.html", context)

def forumpage(request, community_id, forum_id):
	try:
		forum = Forum.objects.get(pk=forum_id)
	except Forum.DoesNotExist:
		raise Http404

	try:
		community = Community.objects.get(pk=community_id)
	except Community.DoesNotExist:
		raise Http404
		
	if forum.community != community:
		# Forum's community is not the same as the expected community from url.
		return HttpResponse("<h1>Bad Request. Looks like you are messing with the url.</h1>")

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "join_community":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to join this community."
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			community.community_members.add(request.user)
			response = {
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "leave_community":
			community.community_members.remove(request.user)
			response = {
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "upvote_forum":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to up vote this forum."
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			if(request.user not in forum.forum_likes.all()):
				forum.forum_likes.add(request.user)
			else:
				forum.forum_likes.remove(request.user)

			if(request.user in forum.forum_dislikes.all()):
				forum.forum_dislikes.remove(request.user)

			response = {
				"status_code": HTTPStatus.OK,
				"this_forum": serializers.serialize("json", [forum,]),
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "downvote_forum":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to down vote this forum."
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			if(request.user not in forum.forum_dislikes.all()):
				forum.forum_dislikes.add(request.user)
			else:
				forum.forum_dislikes.remove(request.user)

			if(request.user in forum.forum_likes.all()):
				forum.forum_likes.remove(request.user)

			response = {
				"status_code": HTTPStatus.OK,
				"this_forum": serializers.serialize("json", [forum,]),
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "post_comment":
			comment = request.GET.get('comment', None)
			forum_comment = ForumComment.objects.create(
				forum = forum,
				creator = request.user,
				comment_description = comment,
			)
			response = {
				"forum_comment": serializers.serialize("json", [forum_comment,]),
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "like_comment":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to like the question and answer. "
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			commentId = request.GET.get('commentId', None)

			try:
				this_comment = ForumComment.objects.get(id=int(commentId))
			except ForumComment.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND,
					"message": "We think this comment has been deleted!"
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			if(request.user not in this_comment.forum_comment_likes.all()):
				this_comment.forum_comment_likes.add(request.user)
			else:
				this_comment.forum_comment_likes.remove(request.user)

			if(request.user in this_comment.forum_comment_dislikes.all()):
				this_comment.forum_comment_dislikes.remove(request.user)

			response = {
				"this_comment": serializers.serialize("json", [this_comment,]),
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "dislike_comment":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to like the question and answer. "
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			commentId = request.GET.get('commentId', None)
			
			try:
				this_comment = ForumComment.objects.get(id=int(commentId))
			except ForumComment.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND,
					"message": "We think this comment has been deleted!"
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			if(request.user not in this_comment.forum_comment_dislikes.all()):
				this_comment.forum_comment_dislikes.add(request.user)
			else:
				this_comment.forum_comment_dislikes.remove(request.user)

			if(request.user in this_comment.forum_comment_likes.all()):
				this_comment.forum_comment_likes.remove(request.user)

			response = {
				"this_comment": serializers.serialize("json", [this_comment,]),
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

	context = {
		"forum": forum,
		"in_community": True if request.user in community.community_members.all() else False
	}
	return render(request, "forum/forumpage.html", context)

@deprecated(reason="Legacy")
def mainpage_legacy(request):
	communities = Community.objects.all().order_by('-community_likes')

	if not communities:
		context = {
			"message": "Looks like you have to create a new community!.",
			"alert": "alert-info"
		}
		return render(request, "forum/mainpage.html", context)

	sub_communities = [communities[i:i + 10] for i in range(0, len(communities), 10)]

	if int(page_number)<1:
		return redirect('forum:mainpage', page_number=1)

	if int(page_number) > len(sub_communities):
		return redirect('forum:mainpage', page_number=len(sub_communities))

	if request.method == "POST" and "create_community" in request.POST:
		if not request.user.is_authenticated:
			return redirect('accounts:login')

		community_title = request.POST["community_title"]
		community_url = ''.join(e for e in community_title if e.isalnum())
		community_description = request.POST["community_description"]
		anonymous = request.POST.get('anonymise_me', False) == 'on'

		if Community.objects.filter(community_url=community_url).exists():
			context = {
				"sub_communities": sub_communities[int(page_number)-1],
				"pages": len(sub_communities),
				"current_page": page_number,
				"message": "Hey we think a similar forum already exists to what you're creating.",
				"url": community_url,
				"alert": "alert-info"
			}
			return render(request, "forum/mainpage.html", context)

		Community.objects.create(
			creator = request.user,
			community_title = community_title,
			community_url = community_url,
			community_description = community_description,
			anonymous=anonymous
		)
		request.session['new_community_message'] = "WOW! It's a new community. Create a sub-forum, upload stuff or do what ever you want. Sky's the limit!"
		return redirect('forum:communitypage', community_url=community_url, page_number=1)

	context = {
		"sub_communities": sub_communities[int(page_number)-1],
		"pages": len(sub_communities),
		"current_page": page_number
	}
	return render(request, "forum/mainpage.html", context)

@deprecated(reason="Legacy")
def communitypage_legacy(request, community_url, page_number):
	community = Community.objects.get(community_url=community_url)
	forums_all = Forum.objects.filter(community=community).order_by('-id')
	forums = [forums_all[i:i + 10] for i in range(0, len(forums_all), 10)]

	if request.method == "POST" and "create_forum" in request.POST:
		if not request.user.is_authenticated:
			return redirect('accounts:login')

		forum_title = request.POST["forum_title"]
		forum_description = request.POST["forum_description"]
		anonymous = request.POST.get('anonymise_me', False) == 'on'

		if "my-file-selector" in request.FILES:
			forumPicture = request.FILES["my-file-selector"]
			# tutorProfile.profilePicture = profilePicture
			# tutorProfile.save(update_fields=['profilePicture'])

		Forum.objects.create(
			community=community,
			creator=request.user,
			forum_title = forum_title,
			forum_url=''.join(e for e in forum_title if e.isalnum()),
			forum_description=forum_description,
			anonymous=anonymous
		)
		return redirect('forum:communitypage', community_url=community_url, page_number=page_number)

	if len(forums) != 0:
		if int(page_number)<1:
			return redirect('forum:communitypage', community_url=community_url, page_number=1)

		if int(page_number) > len(forums):
			return redirect('forum:communitypage', community_url=community_url, page_number=len(forums))

	context = {
		"community": community,
		"community_url": community_url,
		"forums": forums[int(page_number)-1] if len(forums)>0 else [],
		"current_page": page_number,
		"pages": len(forums)
	}

	if "new_community_message" in request.session:
		context["new_community_message"] = request.session["new_community_message"]
		context["alert"] = "alert-success"
		del request.session["new_community_message"]

	return render(request, "forum/communitypage.html", context)

@deprecated(reason="Implemented as part of the view that serves the HTML page.")
def upvote_community(request):
	if not request.is_ajax():
		response = {
			"status_code": 403,
			"message": "Bad Request"
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	if not request.user.is_authenticated:
		response = {
			"status_code": 401,
			"message": "Login to vote this community."
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	community_id = request.GET.get('community_id', None)
	user = User.objects.get(id=int(request.user.pk))
	this_community = Community.objects.get(id=int(community_id))
	list_of_liked = Community.objects.filter(community_likes__id=user.pk)
	list_of_disliked = Community.objects.filter(community_dislikes__id=user.pk)

	if(this_community not in list_of_liked):
		user.community_likes.add(this_community)
	else:
		user.community_likes.remove(this_community)

	if(this_community in list_of_disliked):
		user.community_dislikes.remove(this_community)

	response = {
		"this_community": serializers.serialize("json", [this_community,]),
		"status_code": 200
	}
	return HttpResponse(json.dumps(response), content_type="application/json")

@deprecated(reason="Implemented as part of the view that serves the HTML page.")
def downvote_community(request):
	if not request.is_ajax():
		response = {
			"status_code": 403,
			"message": "Bad Request"
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	if not request.user.is_authenticated:
		response = {
			"status_code": 401,
			"message": "Login to vote this community."
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	community_id = request.GET.get('community_id', None)
	user = User.objects.get(id=int(request.user.pk))
	this_community = Community.objects.get(id=int(community_id))
	list_of_liked = Community.objects.filter(community_likes__id=user.pk)
	list_of_disliked = Community.objects.filter(community_dislikes__id=user.pk)

	if(this_community not in list_of_disliked):
		user.community_dislikes.add(this_community)
	else:
		user.community_dislikes.remove(this_community)
		
	if(this_community in list_of_liked):
		user.community_likes.remove(this_community)

	response = {
		"this_community": serializers.serialize("json", [this_community,]),
		"status_code": 200
	}
	return HttpResponse(json.dumps(response), content_type="application/json")

@deprecated(reason="Implemented as part of the view that serves the HTML page.")
def upvote_forum(request):
	if not request.is_ajax():
		response = {
			"status_code": 403,
			"message": "Bad Request"
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	if not request.user.is_authenticated:
		response = {
			"status_code": 401,
			"message": "Login to vote this forum."
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	forum_id = request.GET.get('forum_id', None)
	user = User.objects.get(id=int(request.user.pk))
	this_forum = Forum.objects.get(id=int(forum_id))
	list_of_liked = Forum.objects.filter(forum_likes__id=user.pk)
	list_of_disliked = Forum.objects.filter(forum_dislikes__id=user.pk)

	if(this_forum not in list_of_liked):
		user.forum_likes.add(this_forum)
	else:
		user.forum_likes.remove(this_forum)

	if(this_forum in list_of_disliked):
		user.forum_dislikes.remove(this_forum)

	response = {
		"this_forum": serializers.serialize("json", [this_forum,]),
		"status_code": 200
	}
	return HttpResponse(json.dumps(response), content_type="application/json")

@deprecated(reason="Implemented as part of the view that serves the HTML page.")
def downvote_forum(request):
	if not request.is_ajax():
		response = {
			"status_code": 403,
			"message": "Bad Request"
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	if not request.user.is_authenticated:
		response = {
			"status_code": 401,
			"message": "Login to vote this community."
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	forum_id = request.GET.get('forum_id', None)
	user = User.objects.get(id=int(request.user.pk))
	this_forum = Forum.objects.get(id=int(forum_id))
	list_of_liked = Forum.objects.filter(forum_likes__id=user.pk)
	list_of_disliked = Forum.objects.filter(forum_dislikes__id=user.pk)

	if(this_forum not in list_of_disliked):
		user.forum_dislikes.add(this_forum)
	else:
		user.forum_dislikes.remove(this_forum)
		
	if(this_forum in list_of_liked):
		user.forum_likes.remove(this_forum)

	response = {
		"this_forum": serializers.serialize("json", [this_forum,]),
		"status_code": 200
	}
	return HttpResponse(json.dumps(response), content_type="application/json")

def vanilla_JS_date_conversion(python_date):
	date = python_date.strftime("%b. %d, %Y,")
	time = datetime.strptime( python_date.strftime("%H:%M"), "%H:%M")
	time = time.strftime("%I:%M %p").lower().replace("pm", "p.m.").replace("am", "a.m.")
	date_time = str(date + " " + time)
	return date_time