#!/usr/bin/python3
import eel
import main

BOT = main.BOT()

def init():
	BOT = main.BOT()

def run(*args, **kwargs):
	BOT.cfg = BOT.JSON()
	BOT.construct()
	BOT.start()

def film_have(film):
	db = main.utils.DATABASE(BOT.cfg['db_name'])
	for subscriber in db.read(table_name="subscribe_categories", where=" category = "+film[-1]):
		def download():
			main.utils.image_download(film[2])

		t = Thread(target=download)
		t.start()
		t.join()

		BOT.bot.send_photo(subscriber[0],
			photo=open(".image.jpg", "rb"),
			caption=BOT.cfg['category_nufic_message'],
			reply_markup=main.utils.inline_markup(BOT.film_view_markup)
		)

def upd():
	main.utils.update_DB(db_name=BOT.cfg["db_name"],
						fhh=function,
						fah=main.utils.call(film_have),
						categories=BOT.cfg['categories']
			)


run_fun = main.utils.call(run)

@eel.expose
def re_init():
	init()

@eel.expose
def start(send_message=True):
	try:
		th = main.Thread(target=run_fun, args=[send_message])
		th.start()
	except Exception as e:
		main.utils.log(e)
		return False


@eel.expose
def stop():
	try:
		BOT.stop()
		return True
	except Exception as e:
		main.utils.log(e)
		return False


@eel.expose
def send_message(msg, all=False, chat_id=None):
	try:
		if all:
			BOT.send_all(msg)
		else:
			BOT.bot.send_message(chat_id, msg)
	except Exception as e:
		main.utils.log(e)
		return False


@eel.expose
def get_chats():
	try:
		return main.utils.get_all_subscribers(db_name=BOT.cfg['db_name'])
	except Exception as e:
		main.utils.log(e)
		return False


@eel.expose
def read(path):
	try:
		f = open(path, 'r')
		content = f.read()
		f.close()

		return content
	except Exception as e:
		main.utils.log(e)
		return False


@eel.expose
def write(path, content):
	try:
		f = open(path, 'w+')
		f.write(content)
		f.close()
		return True
	except Exception as e:
		main.utils.log(e)
		return False


@eel.expose
def update(function):
	try:
		th = main.Thread(target=upd)
		th.start()
		return True
	except Exception as e:
		main.utils.log(e)
		return False


if __name__ == '__main__':
	init()
	eel.init("ui/")
	eel.start("index.html")
