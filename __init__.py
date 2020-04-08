from mycroft import MycroftSkill, intent_file_handler


class Daisy(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('daisy.intent')
    def handle_daisy(self, message):
        self.speak_dialog('daisy')


def create_skill():
    return Daisy()

