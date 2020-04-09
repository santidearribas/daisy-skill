from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import LOG
import requests
import os
from os.path import join, exists
import uuid

class Daisy(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.serial_key = ""
        self.home_assistant_id = str(uuid.uuid4())[0:28]
        self.user_id = ""
        self.username = ""

        self.root_dir = join(self.root_dir)
        self.cred_file = join(self.file_system.path, 'cred')

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
        self.serial_key = cpuserial
    
    @intent_file_handler("hi.daisy.intent")
    def handle_hi_daisy(self, message):
        self.check_cred()
        if self.username is None:
            response = self.get_response("have you registered on the daisy app")
            if response == "yes":
                code = self.get_response("whats your code")
                self.check_user(code)
                if self.username is None:
                    self.speak("user does not exist. please register on the daisy app and try pairing again with hi daisy")
                elif self.username is not None:
                    if self.register_home_assist() is "SUCCESS":
                        self.write_cred()
                        self.speak("Welcome {}. You have been registered".format(self.username))
                    else:
                        self.speak("There has been an error. Please wait and try pairing again with hi daisy later")
                else:
                    self.speak("There has been an error. Please wait and try pairing again with hi daisy later")
            elif response == "no":
                self.speak("please register on the daisy app and try pairing again with hi daisy")
            else:
                self.speak("invalid response use yes or no. try pairing again with hi daisy")        
        else:
            self.speak("Welcome {}".format(self.username))

    def check_user(self, code):
        url = "https://daisy-project.herokuapp.com/user/"
        response = requests.get(url)
        if response.status_code == 200:
            output = response.json()
            data_output = output["data"]
            for user in data_output:
                if user["pair_pin"] == code:
                    self.user_id = user["id"]
                    self.username = user["username"]
                else:
                    self.username is None
        else:
            return "ERROR"

    def register_home_assist(self):
        data={
            "id": self.home_assistant_id,
            "serial_key": self.serial_key,
            "lat_long": "TEST-GPS",
            "user_ID": self.user_id
        }
        url = "https://daisy-project.herokuapp.com/home-assistant/"
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return "SUCCESS"
        else:
            return "ERROR"    

    def check_cred(self):
        LOG.info(self.root_dir)
        if os.stat(self.cred_file).st_size == 0:
            self.username is None
        else:
            with open(self.cred_file) as f:
                username = f.read()
                self.username = username

    def write_cred(self):
        with open(self.cred_file, "w") as f:
            f.write(self.username)

def create_skill():
    return Daisy()