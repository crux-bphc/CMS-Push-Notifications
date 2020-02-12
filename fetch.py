import requests
import time
import sqlite3
from apns import APNs, Frame, Payload, PayloadAlert
from os.path import isfile

# urls
base_url = "https://td.bits-hyderabad.ac.in/moodle/webservice/rest/server.php?"
login_user = base_url + "wsfunction=core_webservice_get_site_info&moodlewsrestformat=json"
get_user_courses = base_url + "wsfunction=core_enrol_get_users_courses&moodlewsrestformat=json"
get_course_modules = base_url + "wsfunction=core_course_get_contents&moodlewsrestformat=json"
get_discussions = base_url + "wsfunction=mod_forum_get_forum_discussions_paginated&moodlewsrestformat=json&sortby=timemodified&sortdirection=DESC"

# other variables
token = ""
user_id = 0
device_token = ""
cert_file = ""
key_file = ""
repeat_after = 0

# database variables
conn = sqlite3.connect('coursedata.db')
c = conn.cursor()
dbEmpty = False

def getInput():
	global device_token
	global cert_file
	global key_file
	global repeat_after
	global token
	device_token = raw_input("Enter your device token from Xcode: ")
	cert_file = raw_input("Enter the name of the certificate file(must contain .pem): ")
	key_file = raw_input("Enter the name of the key file(must contain .pem): ")
	repeat_after = raw_input("How often to repeat fetch(in seconds): ")
	token = raw_input("Enter your moodle token: ")



def loginUserAndGetToken():
	global user_id
	url = login_user + "&wstoken=" + token
	data = requests.get(url = url).json()
	user_id = data["userid"]

def getDatabaseDetails():
	global dbEmpty
	c.execute('SELECT name FROM sqlite_master WHERE type="table"')
	if len(c.fetchall()) == 0:
		dbEmpty = True
		print("Database is empty, not sending any notifications...")
	else:
		dbEmpty = False

def getUserCourses():
	global token
	global user_id
	print "Downloading modules and discussions..."
	url = get_user_courses + "&wstoken=" + token + "&userid=" + str(user_id)
	courses = requests.get(url = url).json()
	for course in courses:
		enterCourseInDB(course["id"], course["fullname"])
		# get modules of this course
		getModulesForCourse(course["id"], course["fullname"])
	# c.close()
	# conn.close()
	getDatabaseDetails()
	print "Finished execution, repeating after " + str(repeat_after) + " seconds..."
	time.sleep(float(repeat_after))
	getUserCourses()



def enterCourseInDB(courseid, coursename):
	c.execute('CREATE TABLE IF NOT EXISTS courses(courseid INT PRIMARY KEY, coursename TEXT)')
	c.execute('INSERT OR IGNORE INTO courses VALUES(?,?)',
		(courseid, coursename,))
	conn.commit()



def enterModuleInDB(moduleid, modulename, courseid):
	c.execute('CREATE TABLE IF NOT EXISTS modules(moduleid INT PRIMARY KEY, modulename TEXT, courseid INT)')
	c.execute('INSERT OR IGNORE INTO modules VALUES(?,?,?)',
		(moduleid, modulename, courseid,))
	conn.commit()



def getModulesForCourse(courseid, coursename):
	global token
	c.execute('CREATE TABLE IF NOT EXISTS modules(moduleid INT PRIMARY KEY, modulename TEXT, courseid INT)')
	url = get_course_modules + "&wstoken=" + token + "&courseid=" + str(courseid)
	data = requests.get(url = url).json()
	for section in data:
		if len(section["modules"]) != 0:
			for module in section["modules"]:
				if module["modname"] == "forum":
					getAnnouncementsForModule(module["instance"], courseid, coursename)
				else:
					current_module_id = module["id"]
					# check if module with this id exists
					c.execute('SELECT * FROM modules WHERE moduleid=(?)',
						(current_module_id,))
					if len(c.fetchall()) == 0:
						# new module
						# send notification or whatever
						if not dbEmpty:
							sendNotificationForModule(module["name"], coursename)
						print "Found New Module " + module["name"] + " in course " + str(coursename)
						enterModuleInDB(current_module_id, module["name"], courseid)
				


def getAnnouncementsForModule(moduleid, courseid, coursename):
	# make request for announcements
	global token
	c.execute('CREATE TABLE IF NOT EXISTS discussions(discussionid INT PRIMARY KEY, moduleid INT, title TEXT, coursename TEXT)')
	url = get_discussions + "&wstoken=" + token + "&forumid=" + str(moduleid)
	data = requests.get(url = url).json()
	for discussion in data["discussions"]:
		c.execute('SELECT * FROM discussions WHERE discussionid=(?)',
			(discussion["id"],))
		if len(c.fetchall()) == 0:
			# new discussion
			# send notification or whatever
			if not dbEmpty:
				sendNotificationForDiscussion(discussion["name"], coursename)
			print "Found New Discussion " + discussion["name"] + " in course " + str(coursename)
			enterAnnouncementInDB(discussion["id"], moduleid, discussion["name"], coursename)

	



def enterAnnouncementInDB(discussionid, moduleid, title, coursename):
	c.execute('CREATE TABLE IF NOT EXISTS discussions(discussionid INT PRIMARY KEY, moduleid INT, title TEXT, coursename TEXT)')
	c.execute('INSERT OR IGNORE INTO discussions VALUES(?,?,?,?)',
		(discussionid, moduleid, title, coursename,))




def sendNotificationForModule(modulename, coursename):
	global device_token
	apns = APNs(use_sandbox=True, cert_file=cert_file, key_file=key_file)
	message = "New Module " + modulename + " in course " + coursename
	alert = PayloadAlert(title=modulename, body=("New module in " + coursename))
	payload = Payload(alert=alert)
	apns.gateway_server.send_notification(device_token, payload)

def sendNotificationForDiscussion(discussionname, coursename):
	global device_token
	apns = APNs(use_sandbox=True, cert_file=cert_file, key_file=key_file)
	alert = PayloadAlert(title=discussionname, body=("New Announcement in " + coursename))
	payload = Payload(alert=alert)
	apns.gateway_server.send_notification(device_token, payload)

def main():
	getInput()
	getDatabaseDetails()
	loginUserAndGetToken()
	getUserCourses()


if __name__== "__main__":
  main()
