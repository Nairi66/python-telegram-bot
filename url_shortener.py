import telebot, requests                                                        

bot = telebot.TeleBot("1292521216:AAFG73G8bmWVEsSVM8JRqEyGNuZsfz23Cig")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Howdy, how are you doing?")

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "With this bot you can short your long urls. ❤️")
    bot.send_message(message.chat.id, "Use @short <url> to short.")

@bot.message_handler(content_types=['text'])
def url_shortener(message):
    command = message.text[:7]
    if command == "@short ":
        link_to_short = message.text.replace(command, '')
        post_url = 'http://api.xn--y9aua5byc.xn--y9a3aq/urls'
        data = {'url': link_to_short}
        x = requests.post(post_url, data = data)
        print(x.text[:7])
        short_key = x.text[:7]
        short_url = "նա.հայ/?id=" + short_key
        text = "Your short url is there. Thank you!!! ❤️❤️\n"
        bot.send_message(message.chat.id, text+short_url)

bot.polling()
