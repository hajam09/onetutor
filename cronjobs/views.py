# from django.shortcuts import render

# # Create your views here.
# from django.contrib.auth.models import User
# import time
# from threading import Thread

# def getAllUsers():
# 	time.sleep(5)
# 	for i in User.objects.all():
# 		print(i.first_name)
# 	getAllUsers()

# def mainFunction():
# 	t1 = Thread(target = getAllUsers)
# 	t1.daemon = True
# 	t1.start()