import pymongo
import requests
import time

base_url = "https://td.bits-hyderabad.ac.in/moodle/webservice/rest/server.php?"
login_user = base_url + "wsfunction=core_webservice_get_site_info&moodlewsrestformat=json"
get_user_courses = base_url + "wsfunction=core_enrol_get_users_courses&moodlewsrestformat=json"

token = ""
user_id = 0
persisted_data = ""

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
	data = requests.get(url = url).json()
	if persisted_data == "":
		persisted_data = data
	if data != persisted_data:
		print("Found new data")
		persisted_data = data
	else:
		print("No new data")
	time.sleep(5)
	getUserCourses()



def createDatabase():
	client = pymongo.MongoClient("mongodb://localhost:27017/")
	db = client["courses"]




def main():

	loginUserAndGetToken()
	getUserCourses()







if __name__== "__main__":
  main()
