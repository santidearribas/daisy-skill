from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler
from mycroft.skills.core import MycroftSkill
import requests
import os
import uuid

credentials = "cred"

class Daisy(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def getserial(self):
        # Extract serial from cpuinfo file
        cpuserial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo','r')
            for line in f:
                if line[0:6]=='Serial':
                    cpuserial = line[10:26]
            f.close()
        except:
            cpuserial = "ERROR000000000"
        return cpuserial
    
    @intent_file_handler("hi.daisy.intent")
    def handle_hi_daisy(self, message):
        credentials = self.check_cred()
        if credentials is None:
            response = self.get_response("have you registered on the daisy app")
            if response == "yes":
                code = self.get_response("whats your code")
                user = self.check_user(code)
                if user is None:
                    self.speak("user does not exist. please register on the daisy app and try pairing again with hi daisy")
                elif user is not None:
                    if self.register_home_assist(user[0]) is "SUCCESS":
                        self.write_cred(user[1])
                        self.speak("Welcome {}. You have been registered".format(user[1]))
                    else:
                        self.speak("There has been an error. Please wait and try pairing again with hi daisy later")
                else:
                    self.speak("There has been an error. Please wait and try pairing again with hi daisy later")
            elif response == "no":
                self.speak("please register on the daisy app and try pairing again with hi daisy")
            else:
                self.speak("invalid response use yes or no. try pairing again with hi daisy")        
        else:
            self.speak("Welcome {}".format(self.check_cred()))

    def check_user(self, code):
        url = "https://daisy-project.herokuapp.com/user/"
        response = requests.get(url)
        if response.status_code == 200:
            output = response.json()
            data_output = output["data"]
            for user in data_output:
                if user["pair_pin"] == code:
                    return [user["id"], user["username"]]
                else:
                    return None
        else:
            return "ERROR"

    def register_home_assist(self, user_id):
        rasp_pi_serial = getserial()
        home_assistant_id = str(uuid.uuid4())[0:28]
        data={
            "id": home_assistant_id,
            "serial_key": rasp_pi_serial,
            "lat_long": "TEST-GPS",
            "user_ID": user_id
        }
        url = "https://daisy-project.herokuapp.com/home-assistant/"
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return "SUCCESS"
        else:
            return "ERROR"    

    def check_cred(self):
        if os.stat(credentials).st_size == 0:
            return None
        else:
            with open(credentials) as f:
                name = f.read()
                return name

    def write_cred(username):
        with open(credentials, "w") as f:
            f.write(username)

def create_skill():
    return Daisy()