from db import DATABASE
from film_parser import load, forep, load_film_info
import datetime as d
from random import sample
from json import dumps, loads
from fuzzywuzzy.fuzz import ratio
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import os
from urllib.parse import urlparse
import requests
from config import *
from json import loads

class_db = class_db()

# loging in terminal
def log(message, type='LOG'):
	print('[ {} ] - {} '.format(type, message))


# uypdate database for adding films new films if films is not exist in database
def update_DB(db_name, categories, table_name="films", fah=EMPTY_FUNCTION, fhh=EMPTY_FUNCTION):
	try:
		db = DATABASE(db_name)
		tm = d.datetime.now()

		upd = db.read(table_name="updates")
		read = db.read(table_name=table_name)

		try:
			start_index = read[-1][0]+1
		except:
			start_index = 0

		try:
			film_info_index = db.read(table_name="film_info")[-1][0]+1
		except:
			film_info_index = 0

		try:
			id = upd[-1][0]
		except:
			id = 0

		try:
			lmfi = upd[-1][1]
		except:
			lmfi = int(str(tm.year)+str(tm.month)+str(tm.day)+str(tm.hour)+str(tm.minute))

		if lmfi > int(str(tm.year)+str(tm.month)+str(tm.day+UPDATE_TIME)+str(tm.hour)+str(tm.minute)):
			return "db is up to date"

		have_films = [x[1] for x in read]
		cat_keys = list(categories.keys())
		urls = forep("https://armfilm.co/hy/CTG/page/ID/", repl="CTG", count=cat_keys)

		for i, url in enumerate(urls):
			films = load(url=url, repl="ID", count=categories[cat_keys[i]])
			for film in films:
				if not film['name'] in have_films:
					args = [
						start_index,
						film['name'],
						film['image'],
						film['link'],
						film['categori']
					]
					film_info = (
						film_info_index,
						start_index,
						dumps(load_film_info(film['link']))
					)

					db.insert(table_name="film_info", args=film_info)
					db.insert(table_name=table_name, args=args)
					
					start_index+=1
					film_info_index+=1
					have_films.append(film["name"])
					fah(film)
				else:
					fhh(film)

		db.insert("updates", args=(id+1, int(str(tm.year)+str(tm.month)+str(tm.day)+str(tm.hour)+str(tm.minute))))
		
		db.close()
	except Exception as e:
		log(str(e), type="ERROR")


# Utility for spliting films to category
def split_by_category(read):
	categories = {}
	for r in read:
		if not r[-1] in categories:
			categories[r[-1]] = []

		if r[-1] in categories:
			categories[r[-1]].append(r)

	return categories


# utility for searching films from db
def load_films(db_name, table_name="films", only_load=False, count=10, find=None, find_perc=None, random=False, category=None):
	try:
		db = DATABASE(db_name)

		read = db.read(table_name=table_name)
		try:
			len_db = read[-1][0]
		except:
			len_db = 0

		have_films = [(x[1], x[0]) for x in read]
		cats = split_by_category(read)

		if random:
			if category:
				return sample(cats[category], count)
			else:
				return sample(have_films, count)

		if only_load:
			if len_db > (only_load + count) and len_db > only_load:
				return have_films[only_load : only_load + count]
			elif len_db > only_load:
				return have_films[only_load:None]

		if find:
			return db.read(table_name=table_name, where="name LIKE '%{}%'".format(find))

		if find_perc:
			finded = []
			for film in read:
				if ratio(find_perc[0], film[1]) > int(find_perc[1]):
					if not category:
						finded.append(film)
						continue
					elif category == film[-1]:
						finded.append(film)

			return finded

		db.close()

		return have_films[0:count]

	except Exception as e:
		log(str(e), type="ERROR")


####################
# Utility for crud #
#      Users       #
#   for sending    #
#     messages     #
####################
# USERS :: Start <- line
def user_exist(db_name, table_name="users", chat_id=None):
	db = DATABASE(db_name)
	user = db.read(table_name=table_name, where=" chat_id = '{}'".format(chat_id))[0]
	db.close()
	return (len(user) > 0)


def get_all_subscribers(db_name, table_name="users"):
	db = DATABASE(db_name)
	users = db.read(table_name=table_name)
	db.close()
	return users

def get_all_subscribers_id(db_name, table_name="users"):
	db = DATABASE(db_name)
	users = db.read(table_name=table_name)	
	db.close()
	return tuple([user[1] for user in users])


def add_user(db_name, table_name="users", message=None):
	if not table_name and not message:
		raise AttributeError("send too function table_name and bot message instance")

	db = DATABASE(db_name)
	read = db.read(table_name=table_name)
	try:
		new_id = read[-1][0]+1
	except:
		new_id = 0

	uids = get_all_subscribers_id(db_name, table_name)

	data = (
		new_id,
		message.chat.id, 
		message.from_user.username, 
		message.from_user.first_name, 
		message.from_user.last_name
	)

	if not str(data[1]) in uids:
		db.insert(table_name=table_name, args=data)


def delete_subscriber(chat, db_name, table_name="users"):
	if not chat:
		raise AttributeError("params id and chat is none")

	db = DATABASE(db_name)
	db.delete(table_name=table_name, where=" chatid = {}".format(chat))
	db.close()
	return True

#  USERS <= END

# Bot Utils
def inline_markup(arr:dict, rw:int=5):
	keys = list(arr.keys())

	markup = InlineKeyboardMarkup()
	markup.row_width = rw

	for i, key in enumerate(keys.copy()):
		keys[i] = InlineKeyboardButton(key, callback_data=key)

	markup.add(*keys)

	return markup


def repl_markup(arr, rw=5, rh=20):
	markup = ReplyKeyboardMarkup()
	markup.row_width = rw
	markup.resize_keyboard = 20

	for i, buttons in enumerate(arr.copy()):
		arr[i] = KeyboardButton(buttons)

	markup.add(*arr)

	return markup
# End of bot utils


# Class of executing with args for call as function to class
class call:
	def __init__(self, fun, *args):
		self.args = list(args)
		self.fun = fun

	def __call__(self, *args, **kwargs):
		args = list(args)
		args.extend(self.args)
		self.fun(*args, **kwargs)


# Media utility
def image_download(url, type="jpg"):
	r = requests.get(url)
	
	open(".image."+type.strip(), "wb").write(r.content)

	return ".image."+type.strip()


# Message Generators and other utils for messaging
def new_message(msg, repl, db_name, index=0):
	films = load_films(only_load=index, db_name=db_name)
	fnames = [i for i,k in films]
	x = "\n"

	for i, film in enumerate(fnames):
		x += "{0} : {1} \n".format(i+1, film)

	msg = msg.replace(repl, x)
	class_db.film_list = films

	return msg

def render_film_info(id, db_name):
	db = DATABASE(db_name)
	base_info = db.read(table_name="films", where=" id = '{}'".format(id))[0]
	more_info = db.read(table_name="film_info", where=" film_id = '{}'".format(id))[0]
	MESSAGE = ""
	MESSAGE+=base_info[1]+"\n"
	for c,v in loads(more_info[-1]).items():
		MESSAGE += "{0} : {1}\n".format(c,v)

	MESSAGE+=base_info[3]

	return MESSAGE
