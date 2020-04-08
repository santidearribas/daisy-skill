from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler

from mycroft.skills.core import MycroftSkill
import requests

class Daisy(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler("hi.daisy.intent")
    def handle_hi_daisy(self, message):
        self.speak_dialog("hi.daisy")
        code = self.get_response("whats.your.code")
        self.speak(code)


def create_skill():
    return Daisy()