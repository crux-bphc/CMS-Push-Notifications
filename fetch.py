import requests
import time
import sqlite3

# urls
base_url = "https://td.bits-hyderabad.ac.in/moodle/webservice/rest/server.php?"
login_user = base_url + "wsfunction=core_webservice_get_site_info&moodlewsrestformat=json"
get_user_courses = base_url + "wsfunction=core_enrol_get_users_courses&moodlewsrestformat=json"
get_course_modules = base_url + "wsfunction=core_course_get_contents&moodlewsrestformat=json"

# other variables
token = ""
user_id = 0
persisted_data = ""

# database variables
conn = sqlite3.connect('coursedata.db')
c = conn.cursor()


def loginUserAndGetToken():
	global token
	global user_id
	token = raw_input("Enter a token: ")
	url = login_user + "&wstoken=" + token
	data = requests.get(url = url).json()
	user_id = data["userid"]


def getUserCourses():
	global token
	global user_id
	global persisted_data
	url = get_user_courses + "&wstoken=" + token + "&userid=" + str(user_id)
	courses = requests.get(url = url).json()
	for course in courses:
		enterCourseInDB(course["id"])
		# get modules of this course
		getModulesForCourse(course["id"])
	c.close()
	conn.close()



def enterCourseInDB(courseid):
	c.execute('CREATE TABLE IF NOT EXISTS courses(courseid INT PRIMARY KEY)')
	c.execute('INSERT OR IGNORE INTO courses VALUES(?)',
		(courseid,))
	conn.commit()



def enterModuleInDB(moduleid, courseid):
	c.execute('CREATE TABLE IF NOT EXISTS modules(moduleid INT PRIMARY KEY, courseid INT)')
	c.execute('INSERT OR IGNORE INTO modules VALUES(?, ?)',
		(moduleid, courseid,))
	conn.commit()	



def getModulesForCourse(courseid):
	global token
	c.execute('CREATE TABLE IF NOT EXISTS modules(moduleid INT PRIMARY KEY, courseid INT)')
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

					print "Found New Module ", str(current_module_id), " in course ", str(courseid)
					enterModuleInDB(current_module_id, courseid)

				else:
					print "Already exists Module ", str(current_module_id), " in course ", str(courseid)




def main():

	loginUserAndGetToken()
	getUserCourses()







if __name__== "__main__":
  main()
