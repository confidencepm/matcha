from pymongo import MongoClient
from bson.objectid import ObjectId

class DB:

	def __init__(self):
		client = MongoClient('mongodb://mongo:27017/',connect=False,)
		db = client['matcha']
		self.__users = db['users']
		self.__posts = db['posts']
		self.__chats = db['chats']
	
	def get_user(self, query, fields=None):
		''' This function will get a single users information'''
		if not fields:
			user = self.__users.find_one(query)
		else:
			user = self.__users.find_one(query, fields)

		return user
	
	# Add the user the database
	def register_user(self, details):
		self.__users.insert_one(details)
		
	# Get all the users from the database
	def users(self, query={}):
		return self.__users.find(query)
	

	# This funtion is used to get all the users that are not blocked

	# Count all the users
	def count_users(self):
		return self.__users.count_documents({})

	# Update the users information
	def update_user(self, user_id, values):
		items = values.items()
		for key, value in items:
			if key == '_id':
				continue
			self.__users.update_one({'_id' : user_id}, {'$set': { key: value}})


	# Update the flirts and flirted
	def update_flirts(self, user_id, change):
		query = {'_id' : user_id}
		new_values = {'$set': change}

		self.__users.update_one(query, new_values)

	# Add a post to the posts table
	def add_post(self, post):
		self.__posts.insert_one(post)

	# Get all the posts from the table.
	def get_posts(self):
		return self.__posts.find()

	# Get a single post
	def get_post(self, post_id):
		post_id = ObjectId(post_id)

		return self.__posts.find_one({'_id': post_id})


	# Update a single post.
	def update_post(self, post):
		self.__posts.update_one({'_id' : post['_id']}, {'$set': post})

	# delete a single entry
	def delete_post(self, post):
		self.__posts.delete_one({'_id': post['_id']})

	# Create a rooms history.
	def create_history(self, room):
		history ={
			'_id': room,
			'chats': []
		}
		self.__chats.insert_one(history)

	# Add chat history to the database
	def insert_chat(self, sender, room, message):
		history = self.get_chat(room)
		data = {sender: message}
		history['chats'].append(data)

		self.__chats.update_one({'_id': history['_id']}, {'$set':history})
		

	# Get the history for a specific chat.
	def get_chat(self, room):
		return self.__chats.find_one({'_id': room})