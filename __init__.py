from datetime import datetime
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
        self.answers_returned_id = str(uuid.uuid4())[0:28]
        self.user_id = None
        self.username = None
        self.registered = False
        self.questions_answers = {}
        self.answers = []

        self.ask_question = join(self.root_dir, 'daisy-scripts/cron.py')        
        self.update_gps = join(self.root_dir, 'daisy-scripts/update_gps.py')
        self.cred_file = join(self.root_dir, 'daisy-scripts/cred')
        self.questions_file = join(self.root_dir, 'daisy-scripts/questions')

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
                        self.start_question_check()
                        self.update_location()
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
            self.update_location()

    def check_user(self, code):
        LOG.info('CODE: {}'.format(code))
        url = "https://daisy-project.herokuapp.com/user/"
        response = requests.get(url)
        if response.status_code == 200:
            output = response.json()
            data_output = output["data"]
            for user in data_output:
                if user["pair_pin"] == code:
                    self.user_id = user["id"]
                    self.username = user["username"]
                    self.registered = True
                    return True
            self.registered = False
            return False
        else:
            self.registered = "ERROR"
            LOG.info('Check User Error Occured')

    def register_home_assist(self):
        data={
            "id": self.home_assistant_id,
            "serial_key": self.serial_key,
            "lat_long": "PLACEHOLDER",
            "user_ID": self.user_id
        }
        url = "https://daisy-project.herokuapp.com/home-assistant/"
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return "SUCCESS"
        else:
            return "ERROR"
            LOG.info('Register Home Assistant Error Occured')

    def start_question_check(self):
        os.system("python " + self.ask_question)
        LOG.info("Question cron job started...")

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
        self.add_event('question', self.handler_question)
    
    def handler_question(self, message):
        LOG.info('QUESTION RECEIVED!')
        self.speak("You have a new question!")
        with open(self.questions_file) as f:
            questions_dict = json.load(f)
            self.questions_answers = questions_dict
            self.ask_questions()

    def ask_questions(self):
        LOG.info(self.questions_answers)
        response = self.get_response("You have {} questions. Are you ready to answer?".format(len(self.questions_answers)))
        if response == "no":
            #send to phone
            self.speak("Question has been sent to your phone. Please respond when you are available")
            base_url = "https://daisy-project.herokuapp.com/user-details/user/"
            url = base_url + self.user_id
            headers = {"content-type": "application/json"}
            payload = {"ask_question": False, "device_to_use": "phone", "user_available": False}
            requests.put(url, json=payload, headers=headers)
        elif response == "yes":
            self.speak("Ok here are your questions")
            #save question
            for i, question in enumerate(self.questions_answers):
                self.speak("Question {} {}".format(i+1, self.questions_answers[question][0]))
                self.speak("Here are your responses")
                answers_index = []
                for i, answer in enumerate(self.questions_answers[question][1]):
                    self.speak("Response {} {}".format(i+1, self.questions_answers[question][1][answer]))
                    answers_index.append(answer)
                answer_number = self.get_response("Which answer do you pick? State a number")
                self.answers.append(answers_index[int(answer_number)-1])
            send_questions()
        else:
            self.speak("Could not understand please respond with yes or no")
            self.ask_question()

    def send_questions(self):
        url = "https://daisy-project.herokuapp.com/answer-returned/"
        for answer in self.answers:
            data = {
                "id": self.answers_returned_id,
                "user_ID": self.user_id,
                "answer_ID": answer,
                "answer_time": str(datetime.now()),
                "device_used": "home-assistant"
            }
            requests.post(url, json=data)
            if response.status_code == 200:
                LOG.info("Responses sent SUCCESS")
            else:
                LOG.info("Responses sending FAILED")

    def update_location(self):
        os.system("python " + self.update_gps)
        LOG.info("GPS updated")

def create_skill():
    return Daisy()
