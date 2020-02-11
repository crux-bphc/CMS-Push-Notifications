import requests
import time
import sqlite3
from apns import APNs, Frame, Payload

# urls
base_url = "https://td.bits-hyderabad.ac.in/moodle/webservice/rest/server.php?"
login_user = base_url + "wsfunction=core_webservice_get_site_info&moodlewsrestformat=json"
get_user_courses = base_url + "wsfunction=core_enrol_get_users_courses&moodlewsrestformat=json"
get_course_modules = base_url + "wsfunction=core_course_get_contents&moodlewsrestformat=json"

# other variables
token = ""
user_id = 0
device_token = ""
cert_file = ""
key_file = ""
repeat_after = 30

# database variables
conn = sqlite3.connect('coursedata.db')
c = conn.cursor()

def getDeviceDetails():
	global device_token
	global cert_file
	global key_file
	global repeat_after
	device_token = raw_input("Enter your device token from Xcode: ")
	cert_file = raw_input("Enter the name of the certificate file(must contain .pem): ")
	key_file = raw_input("Enter the name of the key file(must contain .pem): ")
	repeat_after = raw_input("How often to repeat fetch(in seconds): ")


def loginUserAndGetToken():
	global token
	global user_id
	token = raw_input("Enter your moodle token: ")
	url = login_user + "&wstoken=" + token
	data = requests.get(url = url).json()
	user_id = data["userid"]


def getUserCourses():
	global token
	global user_id
	print "Downloading modules..."
	url = get_user_courses + "&wstoken=" + token + "&userid=" + str(user_id)
	courses = requests.get(url = url).json()
	for course in courses:
		enterCourseInDB(course["id"], course["fullname"])
		# get modules of this course
		getModulesForCourse(course["id"], course["fullname"])
	# c.close()
	# conn.close()
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
				current_module_id = module["id"]
				# check if module with this id exists
				c.execute('SELECT * FROM modules WHERE moduleid=(?)',
					(current_module_id,))
				if len(c.fetchall()) == 0:
					# new module
					# send notification or whatever
					sendNotification(current_module_id, module["name"], courseid, coursename)
					print "Found New Module " + module["name"] + " in course " + str(coursename)
					enterModuleInDB(current_module_id, module["name"], courseid)



def sendNotification(moduleid, modulename, courseid, coursename):
	apns = APNs(use_sandbox=True, cert_file=cert_file, key_file=key_file)
	token_hex = device_token
	message = "New module " + modulename + " in course " + coursename
	payload = Payload(alert=message, sound="default", badge=1)
	apns.gateway_server.send_notification(token_hex, payload)


def main():
	getDeviceDetails()
	loginUserAndGetToken()
	getUserCourses()


if __name__== "__main__":
  main()
