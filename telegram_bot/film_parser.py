from requests import get
from bs4 import BeautifulSoup as bs


def parse(url):
	url_ = url.split("/")
	host = "http://"+str(url_[2])
	categori = url_[4]
	response = get(url)
	result = []
	film_names = []

	if response.status_code == 200:
		parser = bs(response.content, 'html.parser')
		films = parser.select(".shortstory")

		for film in films:
			try:
				film_name = str(film.find("a", class_="short-title").find("span").text)

				if film_name in film_names:
					continue

				result.append({
					"link":str(film.find("a").get("href")),
					"image": host + str(film.find("img").get("src")),
					"name":film_name,
					"categori":categori
					})

				film_names.append(film_name)
			except Exception as e:
				return str(e)
	else:
		log("Status code error : {} ".format(response.status_code))

	return result


def load_film_info(url):
	result = {}
	response = get(url)

	if response.status_code == 200:
		try:
			parser = bs(response.content, 'html.parser')

			for line in parser.select(".f-fields li"):
				result[line.find("small").text] = line.find("span").text

		except Exception as e:
			log(str(e))

	else:
		log("Status code error : {} ".format(response.status_code))

	return result

def load(url, repl=None, count=1):
	if count < 1:
		return False

	value = []
	
	for i in range(count):
		get_ = ""
		if repl:
			get_ = url.replace(repl, str(i))
			value.extend(parse(get_))

	return value


def forep(text, repl, count=None):
	if type(count) == int:
		count = range(count)

	result = []
	for c in count:
		if repl:
			result.append(text.replace(repl, c))

	return result
