import sys
import time
import telepot
import requests
from time import localtime, strftime
from telepot.loop import MessageLoop
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from DBManager import DBManager
from pyproj import Proj, transform


chrome = webdriver.Chrome("chromedriver.exe")
bot = telepot.Bot("592470508:AAENRFAi4mqw3OcVtYphyLDfSpuX51flsDg")
url = "https://api.data.gov.sg/v1/transport/carpark-availability"
db = DBManager('db.sqlite3')
inProj = Proj(init='epsg:3414')
outProj = Proj(init='epsg:4326')

    
def handle(msg):#a function to tell the bot what to do when users answer with text

    recent_search = []
    #using glance function to take the necessary info.
    content_type, chat_type, chat_id = telepot.glance(msg)
    try:
        if msg['text'] == '/start':
            bot.sendMessage(chat_id, "Hi %s, where do you want to park your car?" % msg['chat']['first_name'])
            return
        print(content_type, chat_type, chat_id)
    except:
        bot.sendMessage(chat_id, 'Please input text!')
        return

    if content_type == 'text' : #check if what user sends is a text 
        
        if not db.is_existed(chat_id) : #check if it is a new user
            matched_carparks = db.search_carpark(msg['text'].upper())
            if matched_carparks == False or matched_carparks == []:
                bot.sendMessage(chat_id, 'Unable to find a carpark for this address!')
            else:
                response = requests.get(url)
                carpark_list_api = response.json()['items'][0]['carpark_data']
                bot.sendMessage(chat_id,"Okay here is what I found:")
                for matched_carpark in matched_carparks:
                    for carpark in carpark_list_api:
                        if (matched_carpark[0] == carpark['carpark_number']):
                            bot.sendMessage(chat_id, 'Carpark number: %s \nAddress: %s \nLots available: %s' %(matched_carpark[0], matched_carpark[1], carpark['carpark_info'][0]['lots_available']))
                            lon, lat = transform(inProj, outProj, float(matched_carpark[2]), float(matched_carpark[3]))
                            bot.sendLocation(chat_id, lat, lon)
                db.add(chat_id, msg['text'].upper())
                recent_search = db.recent_search(chat_id).split(',')
                if len(recent_search) == 1 :
                    rec_search = recent_search[0]
                    keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=rec_search, callback_data=rec_search)]])
                elif len(recent_search) == 2:
                    rec_search1 = recent_search[1]
                    rec_search2 = recent_search[0]
                    keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=rec_search1, callback_data=rec_search1)],
                        [InlineKeyboardButton(text=rec_search2, callback_data=rec_search2)]])
                    
                
                else:
                    rec_search1 = recent_search[2]
                    rec_search2 = recent_search[1]
                    rec_search3 = recent_search[0]
                    keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=rec_search1, callback_data=rec_search1)],
                        [InlineKeyboardButton(text=rec_search2, callback_data=rec_search2)],
                        [InlineKeyboardButton(text=rec_search3, callback_data=rec_search3)]])

                bot.sendMessage(chat_id, "Also here are your recent searches. You may choose one of the following:",reply_markup=keyboard1)
                bot.sendMessage(chat_id, "Or where else do you want to park?")
            
            
        else:
            matched_carparks = db.search_carpark(msg['text'].upper())
            if matched_carparks == False or matched_carparks == []:
                bot.sendMessage(chat_id, 'Unable to find a carpark for this address!')
            else:
                response = requests.get(url)
                carpark_list_api = response.json()['items'][0]['carpark_data']
                bot.sendMessage(chat_id,"Okay here is what I found:")
                for matched_carpark in matched_carparks:
                    for carpark in carpark_list_api:
                        if (matched_carpark[0] == carpark['carpark_number']):
                            bot.sendMessage(chat_id, 'Carpark number: %s \nAddress: %s \nLots available: %s' %(matched_carpark[0], matched_carpark[1], carpark['carpark_info'][0]['lots_available']))
                            lon, lat = transform(inProj, outProj, float(matched_carpark[2]), float(matched_carpark[3]))
                            bot.sendLocation(chat_id, lat, lon)
                recent_search = db.recent_search(chat_id).split(',')
                if msg['text'].upper() not in recent_search:
                    db.add(chat_id, msg['text'].upper())

            recent_search = db.recent_search(chat_id).split(',')
            if len(recent_search) == 1 :
                rec_search = recent_search[0]
                keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=rec_search, callback_data=rec_search)]])
                
               
            elif len(recent_search) == 2:
                rec_search1 = recent_search[1]
                rec_search2 = recent_search[0]
                keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=rec_search1, callback_data=rec_search1)],
                    [InlineKeyboardButton(text=rec_search2, callback_data=rec_search2)]])
            else:
                rec_search1 = recent_search[2]
                rec_search2 = recent_search[1]
                rec_search3 = recent_search[0]
                keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=rec_search1, callback_data=rec_search1)],
                    [InlineKeyboardButton(text=rec_search2, callback_data=rec_search2)],
                    [InlineKeyboardButton(text=rec_search3, callback_data=rec_search3)]])
               
            
            bot.sendMessage(chat_id, "Also here are your recent searches. You may choose one of the following:" ,reply_markup=keyboard1)
            bot.sendMessage(chat_id, "Or where else do you want to park?")
    else:
        bot.sendMessage(chat_id, 'Please input text!')        
                    
def bot_continue(msg) : #a function to tell the bot what to do when users answer with custom keyboard
    query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
    key = query_data.upper()
    matched_carparks = db.search_carpark(key)
    if matched_carparks == False or matched_carparks == []:
        bot.sendMessage(chat_id, 'Unable to find a carpark for this address!')
    else:
        response = requests.get(url)
        carpark_list_api = response.json()['items'][0]['carpark_data']
        bot.sendMessage(chat_id,"Okay here is what I found")
        for matched_carpark in matched_carparks:
            for carpark in carpark_list_api:
                if (matched_carpark[0] == carpark['carpark_number']):
                    bot.sendMessage(chat_id, 'Carpark number: %s \nAddress: %s \nLots available: %s' %(matched_carpark[0], matched_carpark[1], carpark['carpark_info'][0]['lots_available']))
                    lon, lat = transform(inProj, outProj, float(matched_carpark[2]), float(matched_carpark[3]))
                    bot.sendLocation(chat_id, lat, lon)

    recent_search = db.recent_search(chat_id).split(',')
    
    if len(recent_search) == 1 :
        rec_search = recent_search[0]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=rec_search, callback_data=rec_search)]])
    elif len(recent_search) == 2:
        rec_search1 = recent_search[1]
        rec_search2 = recent_search[0]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=rec_search1, callback_data=rec_search1)],
            [InlineKeyboardButton(text=rec_search2, callback_data=rec_search2)]])
        
    
    else:
        rec_search1 = recent_search[2]
        rec_search2 = recent_search[1]
        rec_search3 = recent_search[0]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=rec_search1, callback_data=rec_search1)],
            [InlineKeyboardButton(text=rec_search2, callback_data=rec_search2)],
            [InlineKeyboardButton(text=rec_search3, callback_data=rec_search3)]])

    bot.sendMessage(chat_id, "Also here is your recent searches. You may choose one of the following:" ,reply_markup=keyboard1)
    bot.sendMessage(chat_id, "Or where else do you want to park?")

#tell the bot how to handle messages
MessageLoop(bot, {'chat': handle,
                  'callback_query': bot_continue}).run_as_thread()
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)