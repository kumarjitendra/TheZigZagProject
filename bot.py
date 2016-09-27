import datetime
import os
import telebot
import logging
import sys
import urllib
import re
import redis
from shutil import copyfile
from telebot import types

### CONFIG AND LOCALE CHECK
if not os.path.exists("config.py"):
  copyfile("config.py.new", "config.py")
if not os.path.exists("locale.py"):
  copyfile("locale.py.new", "locale.py")
  
# REDIS SERVER. IF ITS DIFFRENT, CONFIG IT!
redisserver = redis.StrictRedis(host='localhost', port=6379, db=0)

reload(sys)  
sys.setdefaultencoding("utf-8")

execfile("locale.py")
execfile("config.py")

############################################################################
# START OF CODES. DO NOT EDIT ANYTHING IF YOU DONT KNOW WHAT ARE YOU DOING!#
############################################################################

bot = telebot.TeleBot(TOKEN)
# LOGFILE
logfile = open("bot.log", "a")
time = datetime.datetime.now()
for plugin in enabled_plugins:
  try:
    execfile("plugins/" + plugin + ".py")
    print("Enabled plugin " + plugin)
  except:
    print("Error enabling " + plugin)
logfile.write("Bot Started: " + str(time) + ". Enabled plugins:" + str(enabled_plugins) + ". ")
print("Bot started: " + str(time))
messanger_list = []
contacter_list = []
def message_replier(messages):
  for message in messages:
    userid = message.from_user.id
    banlist = redisserver.sismember('zigzag_banlist', '{}'.format(userid))
    if banlist:
      return
    if userid in messanger_list:
      bot.reply_to(message, MESSANGER_LEAVE_MSG, parse_mode="Markdown")
      messanger_list.remove(userid)
      bot.forward_message("-" + str(SUPPORT_GP), message.chat.id, message.message_id)
      return
    if REPLIER:
      if message.text in reply_message_list:
        bot.reply_to(message, reply_message_list.get(message.text), parse_mode="Markdown")
    if message.text == "Send feedback":
      bot.reply_to(message, MESSANGER_JOIN_MSG, parse_mode="Markdown")
      messanger_list.append(userid)
      return
logger = telebot.logger
if DEEP_LOGGING:
  print("Debugging enabled.")
  logfile.write("Debugging enabled. \n")
  telebot.logger.setLevel(logging.DEBUG)
else:
  logfile.write("Debugging disabled. \n")
  print("Debugging disabled.")
bot.set_update_listener(message_replier)
logfile.close()
bot.polling(none_stop=True, interval=0, timeout=3)
