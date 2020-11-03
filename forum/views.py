from django.shortcuts import render, redirect
from .models import Forum, SubForum#, Comment
from datetime import datetime
from django.core import serializers
from django.http import HttpResponse
import json, random
from essential_generators import DocumentGenerator
from django.contrib.auth.models import User

def mainpage(request):
	if request.method == "POST" and "createForum" in request.POST:
		if not request.user.is_authenticated:
			return redirect('accounts:login')

		forum_title = request.POST["forum_title"]
		forum_url = ''.join(e for e in forum_title if e.isalnum())
		forum_description = request.POST["description"]
		anonymous = request.POST.get('anonymise_me', False) == 'on'

		if Forum.objects.filter(forum_url=forum_url).exists():
			context = {
				"message": "Hey we think a similar forum already exists to what you're creating.",
				"url": "forum_url",
				"alert": "alert-info"
			}
			return render(request, "forum/mainpage.html", context)

		Forum.objects.create(
			creator = request.user,
			forum_title = forum_url,
			forum_url = forum_url,
			forum_description = forum_description,
			anonymous=anonymous
		)

	sub_forums = SubForum.objects.all().order_by('-id')
	return render(request, "forum/mainpage.html", {"sub_forums": sub_forums})

def forumpage(request, forum_url):
	print("ssss")
	# for i in range(100):
	# 	gen = DocumentGenerator()
	# 	random_parent_forum = random.choice(Forum.objects.all())
	# 	random_creator = random.choice(User.objects.all())
	# 	random_forum_title = gen.sentence()
	# 	random_forum_url = ''.join(e for e in random_forum_title if e.isalnum())
	# 	random_forum_description = gen.paragraph()
	# 	random_anonymous = False

	# 	SubForum.objects.create(
	# 		parent_forum=random_parent_forum,
	# 		creator=random_creator,
	# 		forum_title=random_forum_title,
	# 		forum_url=random_forum_url,
	# 		forum_description=random_forum_description,
	# 		anonymous=random_anonymous
	# 	)
	return render(request, "forum/forumpage.html", {})

def upvote_sub_forum(request):
	if not request.is_ajax():
		response = {
			"status_code": 403,
			"message": "Bad Request"
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	if not request.user.is_authenticated:
		response = {
			"status_code": 401,
			"message": "Login to dislike the question and answer. "
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	sub_forum_id = request.GET.get('sub_forum_id', None)
	user = User.objects.get(id=int(request.user.pk))
	this_sub_forum = SubForum.objects.get(id=int(sub_forum_id))
	list_of_liked = SubForum.objects.filter(sub_forum_likes__id=user.pk)
	list_of_disliked = SubForum.objects.filter(sub_forum_dislikes__id=user.pk)

	if(this_sub_forum not in list_of_liked):
		user.sub_forum_likes.add(this_sub_forum)
	else:
		user.sub_forum_likes.remove(this_sub_forum)

	if(this_sub_forum in list_of_disliked):
		user.sub_forum_dislikes.remove(this_sub_forum)

	response = {
		"this_sub_forum": serializers.serialize("json", [this_sub_forum,]),
		"status_code": 200
	}
	return HttpResponse(json.dumps(response), content_type="application/json")

def downvote_sub_forum(request):
	if not request.is_ajax():
		response = {
			"status_code": 403,
			"message": "Bad Request"
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	if not request.user.is_authenticated:
		response = {
			"status_code": 401,
			"message": "Login to dislike the question and answer. "
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	sub_forum_id = request.GET.get('sub_forum_id', None)
	user = User.objects.get(id=int(request.user.pk))
	this_sub_forum = SubForum.objects.get(id=int(sub_forum_id))
	list_of_liked = SubForum.objects.filter(sub_forum_likes__id=user.pk)
	list_of_disliked = SubForum.objects.filter(sub_forum_dislikes__id=user.pk)

	if(this_sub_forum not in list_of_disliked):
		user.sub_forum_dislikes.add(this_sub_forum)
	else:
		user.sub_forum_dislikes.remove(this_sub_forum)
		
	if(this_sub_forum in list_of_liked):
		user.sub_forum_likes.remove(this_sub_forum)

	response = {
		"this_sub_forum": serializers.serialize("json", [this_sub_forum,]),
		"status_code": 200
	}
	return HttpResponse(json.dumps(response), content_type="application/json")