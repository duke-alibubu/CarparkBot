import time
import telepot
import requests
from telepot.loop import MessageLoop
from selenium import webdriver
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from DBManager import DBManager
from pyproj import Proj, transform

# Chrome driver for Selenium
chrome = webdriver.Chrome("chromedriver.exe")
# CarparkBot Token on Telegram
bot = telepot.Bot("592470508:AAENRFAi4mqw3OcVtYphyLDfSpuX51flsDg")
# API for Carpark Availability dataset
url = "https://api.data.gov.sg/v1/transport/carpark-availability"
# Establish connection to the database
db = DBManager('db.sqlite3')
# EPSG for SVY21 coordinates (Singapore) 
# to convert XY Coordinates to Longitude and Latitude
inProj = Proj(init='epsg:3414')
outProj = Proj(init='epsg:4326')

# Inform the bot what to do when users answer with text
def handle(msg):

    # Use glance function to take the necessary info
    content_type, chat_type, chat_id = telepot.glance(msg)
    try:
        # Interact with users at first usage
        if msg['text'] == '/start':
            bot.sendMessage(chat_id, "Hi %s, where do you want to park your car?" % msg['chat']['first_name'])
            return
    except:
        # Handle invalid input (e.g. images, etc.)
        bot.sendMessage(chat_id, 'Please input text!')
        return

    # Check whether user input is a text
    if content_type == 'text' :  
        
        # Handle requests for new users
        if not db.is_existed(chat_id):
            # Search in the DATABASE for carparks matched with users' input (address)
            matched_carparks = db.search_carpark(msg['text'].upper())

            # Return message if there is no matched location found or an error happened in the DATABASE
            if matched_carparks == False or matched_carparks == []:
                bot.sendMessage(chat_id, 'Unable to find a carpark for this address!')
            # Matched location found in the DATABASE
            else:
                # GET current data for Carpark Availability from the API
                response = requests.get(url)
                # Retrive carpark availability information
                carpark_list_api = response.json()['items'][0]['carpark_data']
                bot.sendMessage(chat_id,"Okay here is what I found:")
                for matched_carpark in matched_carparks:
                    for carpark in carpark_list_api:
                        if (matched_carpark[0] == carpark['carpark_number']):
                            bot.sendMessage(chat_id, 'Carpark number: %s \nAddress: %s \nLots available: %s' %(matched_carpark[0], matched_carpark[1], carpark['carpark_info'][0]['lots_available']))
                            lon, lat = transform(inProj, outProj, float(matched_carpark[2]), float(matched_carpark[3]))
                            bot.sendLocation(chat_id, lat, lon)
                # Update the DATABASE with search results
                db.add(chat_id, msg['text'].upper())
                # Display buttons for recent searches of a specific users if they wish to continue searching
                recent_search = db.recent_search(chat_id).split(',')
                if len(recent_search) == 1: # 1 button 
                    rec_search = recent_search[0]
                    keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=rec_search, callback_data=rec_search)]])
                elif len(recent_search) == 2: # 2 buttons
                    rec_search1 = recent_search[1]
                    rec_search2 = recent_search[0]
                    keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=rec_search1, callback_data=rec_search1)],
                        [InlineKeyboardButton(text=rec_search2, callback_data=rec_search2)]])
                else: # 3 buttons
                    rec_search1 = recent_search[2]
                    rec_search2 = recent_search[1]
                    rec_search3 = recent_search[0]
                    keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=rec_search1, callback_data=rec_search1)],
                        [InlineKeyboardButton(text=rec_search2, callback_data=rec_search2)],
                        [InlineKeyboardButton(text=rec_search3, callback_data=rec_search3)]])

                bot.sendMessage(chat_id, "Also here are your recent searches. You may choose one of the following:",reply_markup=keyboard1)
                bot.sendMessage(chat_id, "Or where else do you want to park? Please input!")
        # Handle requests for existed users
        else:
            # Search in the DATABASE for carparks matched with users' input (address)
            matched_carparks = db.search_carpark(msg['text'].upper())

            # Return message if there is no matched location found or an error happened in the DATABASE
            if matched_carparks == False or matched_carparks == []:
                bot.sendMessage(chat_id, 'Unable to find a carpark for this address!')
            # Matched location found in the DATABASE
            else:
                # GET current data for Carpark Availability from the API
                response = requests.get(url)
                # Retrive carpark availability information
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
                    # Update the DATABASE with new search results
                    db.add(chat_id, msg['text'].upper())

            # Display buttons for recent searches of a specific users if they wish to continue searching 
            recent_search = db.recent_search(chat_id).split(',')
            if len(recent_search) == 1: # 1 button
                rec_search = recent_search[0]
                keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=rec_search, callback_data=rec_search)]])
            elif len(recent_search) == 2: # 2 buttons
                rec_search1 = recent_search[1]
                rec_search2 = recent_search[0]
                keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=rec_search1, callback_data=rec_search1)],
                    [InlineKeyboardButton(text=rec_search2, callback_data=rec_search2)]])
            else: # 3 buttons
                rec_search1 = recent_search[2]
                rec_search2 = recent_search[1]
                rec_search3 = recent_search[0]
                keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=rec_search1, callback_data=rec_search1)],
                    [InlineKeyboardButton(text=rec_search2, callback_data=rec_search2)],
                    [InlineKeyboardButton(text=rec_search3, callback_data=rec_search3)]])

            bot.sendMessage(chat_id, "Also here are your recent searches. You may choose one of the following:" ,reply_markup=keyboard1)
            bot.sendMessage(chat_id, "Or where else do you want to park? Please input!")
    # Error message for invalid input
    else:
        bot.sendMessage(chat_id, 'Please input text!')        

# Inform the bot what to do when users answer with custom keyboard            
def bot_continue(msg): 
    query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
    # Obtain users' input (address)
    key = query_data.upper()
    # Search in the DATABASE for carparks matched with users' input (address)
    matched_carparks = db.search_carpark(key)
    # Return message if there is no matched location found or an error happened in the DATABASE
    if matched_carparks == False or matched_carparks == []:
        bot.sendMessage(chat_id, 'Unable to find a carpark for this address!')
    # Matched location found in the DATABASE
    else:
        # GET current data for Carpark Availability from the API
        response = requests.get(url)
        # Retrive carpark availability information
        carpark_list_api = response.json()['items'][0]['carpark_data']
        bot.sendMessage(chat_id,"Okay here is what I found")
        for matched_carpark in matched_carparks:
            for carpark in carpark_list_api:
                if (matched_carpark[0] == carpark['carpark_number']):
                    bot.sendMessage(chat_id, 'Carpark number: %s \nAddress: %s \nLots available: %s' %(matched_carpark[0], matched_carpark[1], carpark['carpark_info'][0]['lots_available']))
                    lon, lat = transform(inProj, outProj, float(matched_carpark[2]), float(matched_carpark[3]))
                    bot.sendLocation(chat_id, lat, lon)
    
    # Update the DATABASE with new search results
    recent_search = db.recent_search(chat_id).split(',')
    
    # Display buttons for recent searches of a specific users if they wish to continue searching 
    if len(recent_search) == 1: # 1 button
        rec_search = recent_search[0]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=rec_search, callback_data=rec_search)]])
    elif len(recent_search) == 2: # 2 buttons
        rec_search1 = recent_search[1]
        rec_search2 = recent_search[0]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=rec_search1, callback_data=rec_search1)],
            [InlineKeyboardButton(text=rec_search2, callback_data=rec_search2)]])
    else: # 3 buttons
        rec_search1 = recent_search[2]
        rec_search2 = recent_search[1]
        rec_search3 = recent_search[0]
        keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=rec_search1, callback_data=rec_search1)],
            [InlineKeyboardButton(text=rec_search2, callback_data=rec_search2)],
            [InlineKeyboardButton(text=rec_search3, callback_data=rec_search3)]])

    bot.sendMessage(chat_id, "Also here is your recent searches. You may choose one of the following:" ,reply_markup=keyboard1)
    bot.sendMessage(chat_id, "Or where else do you want to park? Please input!")

# Inform the bot how to handle messages
MessageLoop(bot, {'chat': handle,
                  'callback_query': bot_continue}).run_as_thread()
print ('Listening ...')

# Keep the program running
while 1:
    time.sleep(10)