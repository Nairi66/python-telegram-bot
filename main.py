#!/usr/bin/python3
import utils
from telebot import TeleBot
from threading import Thread

class BOT:
	index = 0
	count_films = utils.STEP
	config_file_name = 'config.json'

	def __init__(self):
		self.cfg = self.JSON()
		self.construct()

	def construct(self):
		self.bot = TeleBot(self.cfg['token'])
		self.commands = {
			"List films" : utils.call(self.manage),
			"Unsubscribe": utils.call(self.del_user),
		}
		self.film_view_markup = {
			"back": utils.call(self.revert),
			"open": utils.call(lambda *x, **b:...),
		}
		self.markup = {
			"1":    utils.call(self.film, 0),
			"2":    utils.call(self.film, 1),
			"3":    utils.call(self.film, 2),
			"4":    utils.call(self.film, 3),
			"5":    utils.call(self.film, 4),
			"6":    utils.call(self.film, 5),
			"7":    utils.call(self.film, 6),
			"8":    utils.call(self.film, 7),
			"9":    utils.call(self.film, 8),
			"10":   utils.call(self.film, 9),
			"prev": utils.call(self.prev),
			"next": utils.call(self.next),
		}

		@self.bot.message_handler(commands=['subscribe', 'unsubscribe', 'categories', 'find'])
		def subscribe_detector(message):
			try:
				if "/subscribe" in message.text:
					category = message.text.split("/subscribe")[-1].strip()
					if category in list(self.cfg['categories'].keys()):
						uinfo = (
							message.chat.id,
							category
						)
						db = utils.DATABASE(self.cfg["db_name"])
						db.insert(table_name="subscribe_categories", args=uinfo)
						self.bot.reply_to(message, self.cfg["subscribe_category"].replace("{}", category))
					else:
						self.bot.send_message(message.chat.id, self.cfg["category_not_found"])

				elif "/unsubscribe" in message.text:
					category = message.text.split("/unsubscribe")[-1].strip()
					if category in self.cfg['categories']:
						db = utils.DATABASE(self.cfg["db_name"])
						db.delete(table_name="subscribe_categories", where=" chat_id =  "+str(message.chat.id))
						self.bot.reply_to(message, self.cfg["unsibscribe_category"].replace("{}", category))
					else:
						self.bot.send_message(message.chat.id, self.cfg["category_not_found"])

				elif "/find" in message.text:
					film_name = message.text.split("/find")[-1].strip()
					finded = utils.load_films(db_name=self.cfg['db_name'], find_perc=[film_name, self.cfg['film_perc']])
					finded.extend(utils.load_films(db_name=self.cfg['db_name'], find=film_name))

					message_ = ""
					for i, film in enumerate(finded):
						message_ += "{}. {}\n{}\n\n".format(i+1, film[1], film[3])

					messages_ = []

					if len(message_) > 2800:
						count = int(len(message_)/2800)
						s = 0
						for i in range(count):
							ns = s+2800
							if len(message_) < ns:
								ns = -1
							msg = message_[s:ns]
							messages_.append(msg)
							s = ns
							if not ns:
								break
					else:
						messages_.append(message_)

					for msg in messages_:
						if len(msg) > 2:
							self.bot.send_message(message.chat.id, msg)
						else:
							self.bot.send_message(message.chat.id, self.cgf['no_film_error'])

				elif "/categories" in message.text:
					msg = ""
					for i, key in enumerate(list(self.cfg["categories"])):
						msg+="{} : {}\n".format(i, key)

					self.bot.send_message(message.chat.id, self.cfg['categories_text'].replace("{}", msg))

			except Exception as e:
				# utils.log(e)
				raise

		@self.bot.callback_query_handler(func=lambda call: True)
		def callback_query(call):
			try:
				if call.data in self.markup.keys():
					self.markup[call.data](call)
				elif call.data in self.film_view_markup.keys():
					self.film_view_markup[call.data](call)
			except Exception as e:
				utils.log(e)


		@self.bot.message_handler(func=lambda x:True)
		def main(message):
			try:
				utils.add_user(message=message, db_name=self.cfg['db_name'])
				if message.text in self.commands:
					self.commands[message.text](message)
				else:
					self.bot.send_message(
									message.chat.id,
									text=self.cfg['base_message'], 
									reply_markup=utils.repl_markup(list(self.commands.keys()))
								)
			except Exception as e:
				utils.log(e)


	def JSON(self):
		return utils.loads(open(self.config_file_name).read())


	def del_user(self, message):
		self.bot.send_message(message.chat.id, self.cfg["global_unsubscribe"])
		utils.delete_subscriber(message.chat.id, db_name=self.cfg['db_name'])


	def manage(self, message, text=None):
		self.bot.send_message(
						message.chat.id,
						text=utils.new_message(msg=text if text else self.cfg['default_message'],
											db_name=self.cfg["db_name"],
											repl=self.cfg['message_repl']
										), 
						reply_markup=utils.inline_markup(self.markup)
					)


	def revert(self, call):
		id = call.message.chat.id
		messages = utils.new_message(index=self.index, 
								msg=self.cfg['default_message'],
								repl=self.cfg['message_repl'],
								db_name=self.cfg["db_name"]
							)
		self.bot.delete_message(id, call.message.message_id)
		self.bot.send_message(id,
						text=messages,
						reply_markup=utils.inline_markup(self.markup)
					)
		self.bot.answer_callback_query(call.id, "Success")


	def send_all(self, msg):
		mkp = utils.repl_markup(utils.START_MARKUP)
		for id in utils.get_all_subscribers_id(db_name=self.cfg["db_name"]):
			try:
				self.bot.send_message(id, msg, reply_markup=mkp)
			except Exception as e:
				utils.delete_subscriber(id, db_name=self.cfg["db_name"])


	def film(self, call, id=0):
		id_ = call.message.chat.id

		db = utils.DATABASE(self.cfg['db_name'])
		film_info = db.read(table_name="films", where=" id = '{}'".format(utils.class_db.film_list[id][1]))[0]
		db.close()

		def download():
			utils.image_download(film_info[2])

		t = Thread(target=download)
		t.start()
		t.join()

		self.bot.delete_message(id_, call.message.message_id)

		self.bot.send_photo( chat_id = id_,
						photo = open(".image.jpg", "rb"),
						reply_markup=utils.inline_markup(self.film_view_markup),
						caption=utils.render_film_info(film_info[0], db_name=self.cfg["db_name"])
					)

	def next(self, call):
		utils.class_db.index+=utils.STEP
		
		messages = utils.new_message(msg=self.cfg['default_message'],
									repl=self.cfg['message_repl'],
									index=utils.class_db.index,
									db_name=self.cfg["db_name"]
							)
		self.bot.edit_message_text(
							text=messages, 
							chat_id=call.message.chat.id, 
							message_id=call.message.message_id, 
							reply_markup=utils.inline_markup(self.markup), 
							inline_message_id = call.inline_message_id
						)


	def prev(self, call):
		utils.class_db.index-=utils.STEP
		if utils.class_db.index < 0:
			utils.class_db.index = 0
			self.bot.answer_callback_query(call.id, self.cfg['no_films_error'])
			return True
		
		message = utils.new_message(msg=self.cfg['default_message'],
								repl=self.cfg['message_repl'],
								index=utils.class_db.index,
								db_name=self.cfg["db_name"]
							)
		self.bot.edit_message_text(
								text=message, 
								chat_id=call.message.chat.id, 
								message_id=call.message.message_id, 
								reply_markup=utils.inline_markup(self.markup), 
								inline_message_id = call.inline_message_id
							)


	def start(self, msg=True):
		if msg:
			self.send_all(self.cfg["start_message"])
		utils.new_message(msg=self.cfg['default_message'],
								repl=self.cfg['message_repl'],
								db_name=self.cfg["db_name"]
							)
		self.bot.polling()


	def stop(self):
		self.bot.stop_polling()


if __name__ == '__main__':
	app=BOT()
	app.start()
