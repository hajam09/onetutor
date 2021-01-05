from django.shortcuts import render, redirect
from .models import Category, Community, Forum, ForumComment
from datetime import datetime
from django.core import serializers
from django.http import HttpResponse
import json, random
from django.contrib.auth.models import User

def mainpage(request):
	Category.objects.all().delete()
	Community.objects.all().delete()
	Forum.objects.all().delete()
	ForumComment.objects.all().delete()
	# communities = Community.objects.all().order_by('-community_likes')

	# if not communities:
	# 	context = {
	# 		"message": "Looks like you have to create a new community!.",
	# 		"alert": "alert-info"
	# 	}
	# 	return render(request, "forum/mainpage.html", context)

	# sub_communities = [communities[i:i + 10] for i in range(0, len(communities), 10)]

	# if int(page_number)<1:
	# 	return redirect('forum:mainpage', page_number=1)

	# if int(page_number) > len(sub_communities):
	# 	return redirect('forum:mainpage', page_number=len(sub_communities))

	# if request.method == "POST" and "create_community" in request.POST:
	# 	if not request.user.is_authenticated:
	# 		return redirect('accounts:login')

	# 	community_title = request.POST["community_title"]
	# 	community_url = ''.join(e for e in community_title if e.isalnum())
	# 	community_description = request.POST["community_description"]
	# 	anonymous = request.POST.get('anonymise_me', False) == 'on'

	# 	if Community.objects.filter(community_url=community_url).exists():
	# 		context = {
	# 			"sub_communities": sub_communities[int(page_number)-1],
	# 			"pages": len(sub_communities),
	# 			"current_page": page_number,
	# 			"message": "Hey we think a similar forum already exists to what you're creating.",
	# 			"url": community_url,
	# 			"alert": "alert-info"
	# 		}
	# 		return render(request, "forum/mainpage.html", context)

	# 	Community.objects.create(
	# 		creator = request.user,
	# 		community_title = community_title,
	# 		community_url = community_url,
	# 		community_description = community_description,
	# 		anonymous=anonymous
	# 	)
	# 	request.session['new_community_message'] = "WOW! It's a new community. Create a sub-forum, upload stuff or do what ever you want. Sky's the limit!"
	# 	return redirect('forum:communitypage', community_url=community_url, page_number=1)

	context = {
		# "sub_communities": sub_communities[int(page_number)-1],
		# "pages": len(sub_communities),
		# "current_page": page_number
	}
	return render(request, "forum/mainpage.html", context)

def communitypage(request, community_url, page_number):
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