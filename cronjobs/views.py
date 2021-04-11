from threading import Thread
import time

def executeDeleteCacheFromLogin(RUN_EVERY):
	time.sleep(RUN_EVERY)
	#
	#
	executeDeleteCacheFromLogin(RUN_EVERY)

def runTasks(functionName, wait_time):
	t1 = Thread(target = functionName, args=(wait_time,))
	t1.daemon = True
	t1.start()

def startCronJobs():
	runTasks(executeDeleteCacheFromLogin, 10)

startCronJobs()