import logging

class Bot(object):
	def __init__(self, send_callback, users_dao, tree):
		self.send_callback = send_callback
		self.users_dao = users_dao
		self.tree = tree

	def handle(self, user_id, user_message, is_admin=False):
		logging.info("Se invocó el método handle")
