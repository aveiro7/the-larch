class User(object):
	def __init__(self, login):
		self.login = login

	def change_login(self, new_login):
		self.login = new_login