from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from http import HTTPStatus
from .models import Room, Message
import json
from django.db.models import Count
from django.http import JsonResponse


def chatpage(request):

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "fetch_participants":

			user_rooms = Room.objects.filter(participant__in=[request.user])
			user_json = []

			for r in user_rooms:
				user_json.append({
					'full_name': r.participant.all()[1].get_full_name() if r.participant.all()[0] == request.user else r.participant.all()[0].get_full_name()
				})

			response = {
				"status_code": HTTPStatus.OK,
				"user_json": user_json
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == 'new_message':
			message, room = request.GET.get('message', None), request.GET.get('room', None)
			
			new_msg_obj = Message.objects.create(
				room = Room.objects.get(id=room),
				creator = request.user,
				message = message,
			)

			response = {
				"status_code": HTTPStatus.OK,
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == 'fetch_chat':
			
			"""
			For each room, get other participant's online status.
			For each room's message container, receive the latest message object pk.
			Use the pk to get other message objects that belongs to this room and have greater pk.
			"""

			data = request.GET.getlist('lst_msg_room[]', [])

			render_msg = []

			for item in data:
				e_room = json.loads(item)
				room_id =  e_room['room_id']
				latest_msg = e_room['msg_id']

				this_room = Room.objects.get(id=room_id)
				new_msg_objs = Message.objects.filter(room=this_room, pk__gt=latest_msg).values()


				render_msg.append({
					"room": room_id,
					"new_msg_objs": list(new_msg_objs),
				})

			response = {
				"status_code": HTTPStatus.OK,
				"new_msg_all_room": render_msg,
			}
			return JsonResponse(response)
			
	user_rooms = Room.objects.filter(participant__in=[request.user])
	return render(request, "chat/chatpage.html", {'room': user_rooms})

def startmessage(request):
	if request.is_ajax():
		if not request.user.is_authenticated:
			response = {
				"status_code": 401,
				"message": "Login to message this user."
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		functionality = request.GET.get('functionality', None)

		if functionality == "start_message":
			participant_id = request.GET.get('participant_id', None)

			this_user = request.user
			that_user = User.objects.get(id=int(participant_id))
			user_list = [this_user, that_user]

			name = this_user.get_full_name() + '|' + that_user.get_full_name()
			
			if not Room.objects.filter(participant__in=user_list).annotate(num_attr=Count('participant')).filter(num_attr=len(user_list)).exists():
				new_room = Room.objects.create(
					name = name
				)
				print("New Room")
				new_room.participant.add(this_user, that_user)

			response = {
				"status_code": HTTPStatus.OK
			}

			return HttpResponse(json.dumps(response), content_type="application/json")

	response = {
		"status_code": HTTPStatus.BAD_REQUEST,
		"message": "Bad Request"
	}
	return HttpResponse(json.dumps(response), content_type="application/json")