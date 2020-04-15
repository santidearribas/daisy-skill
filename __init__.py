from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import LOG
import requests
import os
from os.path import join, exists
import uuid
import json

def getserial():
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

class Daisy(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.serial_key = getserial()
        self.home_assistant_id = str(uuid.uuid4())[0:28]
        self.user_id = None
        self.username = None
        self.registered = False

        self.cred_file = join(self.root_dir, 'cred')

    @intent_handler(IntentBuilder('HiDaisy').require('Hi').require('Daisy'))
    def handle_hi_daisy(self, Message):
        self.check_cred()
        if self.registered == False:
            response = self.get_response("have you registered on the daisy app")
            if response == "yes":
                code = self.get_response("whats your code")
                self.check_user(code)
                if self.registered == False:
                    self.speak("user does not exist. please register on the daisy app and try pairing again with hi daisy")
                elif self.registered == True:
                    if self.register_home_assist() is "SUCCESS":
                        self.save_cred()
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
        LOG.info('CODE: {}'.format(code))
        url = "https://daisy-project.herokuapp.com/user/"
        response = requests.get(url)
        if response.status_code == 200:
            output = response.json()
            data_output = output["data"]
            LOG.info('OUTPUT: {}'.format(data_output))
            for user in data_output:
                if user["pair_pin"] == code:
                    self.user_id = user["id"]
                    self.username = user["username"]
                    self.registered = True
                    LOG.info('USER EXISTS')                 
                else:
                    LOG.info('USER DOES NOT EXIST')
        else:
            self.registered = "ERROR"
            LOG.info('Check User Error Occured')

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
            LOG.info('Register Home Assistant Error Occured')  

    def check_cred(self):
        if os.stat(self.cred_file).st_size == 0:
            self.registered = False
        else:
            with open(self.cred_file) as f:
                cred_dict = json.load(f)
                self.user_id = cred_dict["id"]
                self.username = cred_dict["username"]
                self.registered = True

    def save_cred(self):
        cred_dict = {
            "id": self.user_id,
            "username": self.username
        }
        with open(self.cred_file, "w") as f:
            json.dump(cred_dict, f)
            self.registered = True

    def initialize(self):
        self.add_event('open',
                   self.handler_open)

    def handler_open(self, message):
        LOG.info('OPEN MESSAGE RECIEVED')  
    # code to excecute when open message detected...

def create_skill():
    return Daisy()
