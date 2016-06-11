from datetime import datetime

class Post(object):
	def __init__(self, content, author):
		self.author = author
		self.content = content
		self.date = datetime.now()

	def edit(self, new_content):
		self.content = new_content

	def change_date(self, new_date):
		self.date = new_date

	def __str__(self):
		return "@" + self.author.login + ": " + self.content