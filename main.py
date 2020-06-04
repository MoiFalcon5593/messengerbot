# encoding: utf-8
import webapp2
import json
import logging
from google.appengine.api import urlfetch
from bot import Bot
import yaml
from user_events import UserEventsDao

VERIFY_TOKEN = "facebook_verification_token"
ACCESS_TOKEN = "EAAKASDPk4TgBAIA6M5ctZA4HFrZBF0zuRtRpZAKqRIG9VGZBlqadVW5mmrzBSxCmNBxTZCb5zZA5zxky5NO3WXF1iTY7zCQdfrsuQNdOs7FrTzhdiRlVXusYUPSrrKZAuMX3DUxYMPS1BQLGAb1X9EhJCa4VyNwiudG56GQZC5YDrwZDZD"

class MainPage(webapp2.RequestHandler):
    def __init__(self, request=None, response=None):
        super(MainPage, self).__init__(request, response)
        logging.info("Instanciando bot")
        tree = yaml.load(open('tree.yaml'))
        logging.info("tree: %r", tree)
        self.bot = Bot(send_message, None, tree)
        dao = UserEventsDao()
        # dao.add_user_event("123", "user", "abc")
        # dao.add_user_event("123", "bot", "def")
        # dao.add_user_event("123", "user", "ghi")
        # dao.add_user_event("123", "bot", "jkl")
        # dao.add_user_event("123", "user", "mnñ")
        # data = dao.get_user_events("123")
        # logging.info("eventos: %r", data)
        dao.remove_user_events("123")


    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        # self.response.write('Pronto esto sera un webhook')
        mode = self.request.get("hub.mode")
        if mode == "subscribe":
            challenge = self.request.get("hub.challenge")
            verify_token = self.request.get("hub.verify_token")
            if verify_token == VERIFY_TOKEN:
                self.response.write(challenge)
        else:
            self.response.write("Ok")
            #self.bot.handle(0, "message_text")

    def post(self):
        data = json.loads(self.request.body)
        logging.info("Data obtenida desde Messenger: %s", data)

        if data ["object"] == "page":

            for entry in data ["entry"]:
                for messaging_event in entry["messaging"]:
                    sender_id = messaging_event["sender"]["id"]

                    if messaging_event.get("message"):
                        message = messaging_event['message']
                        message_text = message.get('text','')
                        logging.info("Mensaje obtenido desde msgr: %s", message_text)
                        # bot handle
                        self.bot.handle(sender_id, message_text)
                        #send_message(sender_id, "hola, soy un bot") 

                    if messaging_event.get("postback"):
                        logging.info("Post-back")
#conocida tambien como la funcion send_callback de bot.py
def send_message(recipient_id, message_text, possible_answers):
    #logging.info("Enviando mensaje a %r: %s", recipient_id, message_text)
    headers = {
        "Content-Type": "application/json"
    }
    #message = {"text": message_text}
    # max buttons quantity :3 
    # max recommended answer length: 20 
    #possible_answers = ["Opcion A", "Opcion B", "Opcion C"]
    #menesaje de la funcion get_postback
    message = get_postback_buttons_message(message_text, possible_answers)
    if message is None:
        message = {"text": message_text}

    raw_data = {
        "recipient": {
            "id": recipient_id
        },
        "message": message
    }
    data = json.dumps(raw_data)

    logging.info("Enviando mensaje a %r: %s", recipient_id, message_text)
    #bot envia informacion a la API de facebook messenger validando (se puede trabajar con dev_appserver.py ./ o glocud app deploy)
    r = urlfetch.fetch("https://graph.facebook.com/v2.6/me/messages?access_token=%s" % ACCESS_TOKEN,
                       method=urlfetch.POST, headers=headers, payload=data)
    if r.status_code != 200:
        logging.error("Error %r enviando mensaje: %s", r.status_code, r.content) 

def get_postback_buttons_message(message_text, possible_answers):
    if possible_answers is None or len(possible_answers) > 3:
        return None
    #if len(possible_answers) > 3:
    #    return None    

    buttons = []
    for answer in possible_answers:
        buttons.append({
            "type": "postback",
            "title": answer,
            "payload": answer
        })

    return {
            "attachment":{
                "type":"template",
                "payload": {
                    "template_type": "button",
                    "text": message_text,
                    "buttons": buttons
                }
            }
        }
app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
