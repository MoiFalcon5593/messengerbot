from google.appengine.ext import ndb
import logging 

class UserEvent(ndb.Model):
	"""docstring for UserEvent"""
	user_id = ndb.StringProperty()
	author = ndb.StringProperty()
	message = ndb.StringProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)

class UserEventsDao(object):
	"""docstring for UserEventDao"""
	def add_user_event(self, user_id, author, message):
		event = UserEvent()
		event.user_id = user_id
		event.author = author
		event.message = message
		event.put()
		logging.info("evento registrado: %r", event)

	def get_user_events(self, user_id):
		events = UserEvent.query(UserEvent.user_id == user_id).order(UserEvent.date)
		return [(event.message, event.author) for event in events]

	def remove_user_events(self, user_id):
		events = UserEvent.query(UserEvent.user_id == user_id)
		quantity = events.count()
		for event in events:
			event.key.delete()
		logging.info("Se eliminaron %r eventos", quantity)
		
		
