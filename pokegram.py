import time
import win32clipboard
import os
import random
import time
import os
import sqlite3
import logging
import firebase_admin
import traceback

from datetime import datetime
from bot import InstagramBot
from bot import c
from bot import default_app
from bot import logger
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from unidecode import unidecode
#from firebase_admin import firestore 
from firebase_admin import db
from firebase_admin import credentials

#Note: No Mr Mime or Nidoran purple because of name weirdness

conn = sqlite3.connect('groupchatDatabase.db')
c = conn.cursor()

#For the error when the username isn't logged properly
class Error_true_username_element():
    
    def __init__(self):
        self.text = "Error_1"

class PokegramBot(InstagramBot): 

    def __init__(self, username, password):
        InstagramBot.__init__(self, username, password)
        self.pokemonCaught = True
        self.counter_between_sending_pokemon = 0
        self.pokemon_flee_counter = 0
        self.last_message_and_username_tuple = ''
    
    def send_image(self, image_path):
        data = fileToData(image_path)
        send_to_clipboard(win32clipboard.CF_DIB, data)
        message_box.click()
        self.perform_paste()
        send_button = self.driver.find_element_by_xpath("//button[text()='Send']")
        send_button.click()
    
    def log_all_gc_messages(self):
        print("Finding messages")
        
        message_xpath = """//div[contains(@class, '_7UhW9') and contains(@class, 'xLCgt') and contains(@class, 'p1tLr') and
                                        contains(@class, 'MMzan') and contains(@class, 'KV-D4') and  contains(@class, 'hjZTB')]"""
        
        excluding_reply_headers_ancestor_xpath = """//div[contains(@class, 'ZyFrc')]"""
        
        messages_excluding_reply_headers_xpath = excluding_reply_headers_ancestor_xpath + message_xpath
        messages = self.driver.find_elements_by_xpath(messages_excluding_reply_headers_xpath);
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
        list_of_messages_and_usernames_and_timestamp = []
        
        
        for message in messages:
            logger.info("Message text: " + message.text)                    
            username = self.find_username_from_message(message)
            list_of_messages_and_usernames_and_timestamp.append((username, message.text, timestamp))
        
        if self.last_message_and_username_tuple == '':
            message_list = list_of_messages_and_usernames_and_timestamp
        else:
            index = self.return_index_of_value_in_list_of_tuples(list_of_messages_and_usernames_and_timestamp, self.last_message_and_username_tuple)
            message_list = list_of_messages_and_usernames_and_timestamp[index+1:]
            
        logger.info("Message_list: " )
        logger.info(message_list)
        self.last_message_and_username_tuple = (message_list[-1][0], message_list[-1][1])
        with conn:
            c.executemany("INSERT INTO comments VALUES(?,?,?);", 
                message_list)    
        
        self.insert_username_and_timestamp_into_firebase(message_list)
        
    def remove_quotes_for_xpath(self, string):
        if '"' in string:
            listed_string = string.split('"')
            
            return_string = "concat('" + listed_string[0] + "', '\"', " 
            for stringer in listed_string[1:-1]:
                return_string += "'" + stringer + "', '\"', "
                
            return_string += "'" + listed_string[-1] + "')"
            
            return return_string.replace("Æ", "’")
            
            
        string = string.replace("Æ", "’")
        return ('"' + string + '"')

    def find_username_from_message(self, message):
        xpath_to_generic_message = """//div[contains(@class, '_7UhW9') and contains(@class, 'xLCgt') and contains(@class, 'p1tLr') and
                                        contains(@class, 'MMzan') and contains(@class, 'KV-D4') and  contains(@class, 'hjZTB')]"""
         
        string_to_avoid_quotes = self.remove_quotes_for_xpath(message.text)
        xpath_to_message_spans = """(//span[contains(text(), {})])""".format(string_to_avoid_quotes)   
        logger.info("Message text: " + message.text)
        message_span_list = self.driver.find_elements_by_xpath(xpath_to_message_spans)
        logger.info("Check 3, xpath_to_message_spans: " + xpath_to_message_spans)
        # Get the most recent message, to exclude messages with same text that appear earlier
        for index, message_span in enumerate(message_span_list):
            logger.info("Check 4, for loop")
            if message_span.location["y"] <= message.location["y"]:
                logger.info("Check 5, span.location")
                target_message_span_xpath = xpath_to_message_spans + "[" +  str(index+1) + "]" #Already has () around xpath_to_capture_spans
                logger.info("Target_message_span_xpath: " + target_message_span_xpath)
                username_path = self.get_sender_username_from_element_xpath(target_message_span_xpath)
                username_reply_path = self.get_sender_username_in_reply_from_element_xpath(target_message_span_xpath)
        
        logger.info("Check 6, if self.pokemoncaught")
        #time.sleep(1) #Maybe just wait for it to load?
        weird_error = False
        username_element_exists = False
        username_reply_element_exists = False
        try:
            try:
                username_element = self.driver.find_element_by_xpath(username_path)
                username_element_exists = True
            except Exception as e:
                logger.error(e)
                logger.info("username_element does not exist")
                
            try:
                username_reply_element = self.driver.find_element_by_xpath(username_reply_path)
                username_reply_element_exists = True
            except Exception as e:
                logger.error(e)
                logger.info("username_reply_element does not exist")    
            
        except Exception as e:
            logger.info("The weird bug")
            weird_error = True
            logger.error(e)
            
        
        if weird_error: #act like no one submitted it correctly if the weird error occurs
            print( 'Error with xpath finding')
            quit()
        
        true_username_containing_element = ''
        if not username_element_exists and not username_reply_element_exists:
            logger.error("This should not happen")
            # quit()
            true_username_element = Error_true_username_element()
        elif not username_element_exists:
            true_username_element = username_reply_element
        elif not username_reply_element_exists: 
            true_username_element = username_element            
        else:
            if username_element.location["y"] > username_reply_element.location["y"]:
                logger.info("Check11")
                true_username_element = username_element
            else:
                logger.info("Check12")
                true_username_element = username_reply_element
                
        logger.info("Check 7: true_username_element text: " + true_username_element.text)            
        if " replied to " in true_username_element.text:         
            usernamer = true_username_element.text.split()[0]
        else:    
            usernamer = true_username_element.text
        
        return usernamer
    
    def monitor_gc_for_captures(self, pokemonName):
        print("Finding messages")
        messages = self.driver.find_elements_by_css_selector(self.message_css_selector);
        message_senders = self.driver.find_elements_by_css_selector(self.message_sender_css_selector);
        message_sender_replies = self.driver.find_elements_by_css_selector(self.replies_css_selector);
        
        for message in messages:
            logger.info("Message text: " + message.text)
            if 'p!c' in message.text:
                logger.info("Pokemon name: " + pokemonName)
                logger.info("Message lower case: " + message.text.lower())
                if pokemonName in message.text.lower():
                    logger.info("Check2")
                    
                    username = self.find_username_of_pokemon_capture(pokemonName)
                    if username: # Will be non-empty, and therefore True, if there's a correct answer
                        print("Sending congrats message")
                        message_box.click()
                        self.actions.send_keys('Congrats, you caught ', pokemonName.capitalize(), " ", username, "!")
                        self.actions.send_keys(Keys.RETURN)
                        self.actions.perform()
                        self.actions = 4 #Most hacky way to reset action chain
                        self.actions = ActionChains(self.driver)
                        logger.info("Username of catcher: " + username)
                        with conn:
                            c.execute("UPDATE groupChatUsernameFrequency SET Pokemon = Pokemon || :pokemonName WHERE Username = :Username", 
                            {'pokemonName': " " +pokemonName.capitalize(), 'Username':username})
                        notYetFound = False
                        pokeBot.pokemon_flee_counter
                        break

    def insert_username_and_timestamp_into_firebase(self, username_timestamp_tuple_list):
        logger.info("Update database for comments")
        #try:
        c.execute("SELECT * FROM comments")
        comment_list = c.fetchall()
        num_of_comments = len(comment_list)
        #logger.info('Making JSON')
        recordsDict = {}
        try:
            for index, record in enumerate(username_timestamp_tuple_list):
                recordsDict["comment_num_" + str(index+num_of_comments+1-len(username_timestamp_tuple_list))] = {
                   'Username' : record[0],
                   'Timestamp' : record[2],
                   
                }
        except Exception as e:
            logger.info('Something went wrong with making JSON for comments')
            logger.info(e)
        
        comments_ref = db.reference("CommentTimestampLog")
        #comments_ref.push(recordsDict)
        #logger.info(recordsDict)
        # May want to use Push() instead, idk
        comments_ref.update(recordsDict)
    
    def find_username_of_pokemon_capture(self, pokemonName):
        xpath_to_generic_message = """//div[contains(@class, '_7UhW9') and contains(@class, 'xLCgt') and contains(@class, 'p1tLr') and
                                        contains(@class, 'MMzan') and contains(@class, 'KV-D4') and  contains(@class, 'hjZTB')]"""
                                        
        xpath_to_capture_spans = """(//span[contains(text(), 'p!c') and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{}')])""".format(pokemonName.lower())   
        logger.info("Lower pokename: " + pokemonName.lower())
        logger.info("Check 3, username function")
        capture_span_list = self.driver.find_elements_by_xpath(xpath_to_capture_spans)
       
        pokemon_pictures_xpath = "//div[contains(@class, 'VdURK') and contains(@class, 'e9_tN') and contains(@class, 'JRTzd')]//img[@style='min-height: 100%; min-width: 100%;']"
        pokemon_picture = self.driver.find_elements_by_xpath(pokemon_pictures_xpath)[-1]
        for index, capture_span in enumerate(capture_span_list):
            logger.info("Check 4, for loop")
            if capture_span.location["y"] > pokemon_picture.location["y"]:
                logger.info("Check 5, span.location")
                target_capture_span_xpath = xpath_to_capture_spans + "[" +  str(index+1) + "]" #Already has () around xpath_to_capture_spans
                logger.info("Target_capture_span_xpath: " + target_capture_span_xpath)
                username_path = self.get_sender_username_from_element_xpath(target_capture_span_xpath)               
                self.pokemonCaught = True
                break
                
        if self.pokemonCaught:
            logger.info("Check 6, if self.pokemoncaught")
            time.sleep(4) #Maybe just wait for it to load?
            weird_error = False
            try:
                username_element = self.driver.find_element_by_xpath(username_path)
            except Exception as e:
                logger.info("The weird bug")
                weird_error = True
                logger.error(e)
                
            
            if weird_error: #act like no one submitted it correctly if the weird error occurs
                return ''
            
            logger.info("Check 7: Username element text: " + username_element.text)            
            if " replied to " in username_element.text:         
                usernamer = username_element.text.split()[0]
            else:    
                usernamer = username_element.text
            
            return usernamer
                
        return ''
        
    def set_comments_to_zero(self):
        
        list_of_usernames = self.get_list_of_insta_usernames()
        for username in list_of_usernames:
            with conn:
                c.execute("DELETE FROM comments;")                                    
     
    def return_index_of_value_in_list_of_tuples(self, list_of_tuples, tuple_of_values):
    
        
        for index, tuple in enumerate(list_of_tuples):
            if tuple[0] == tuple_of_values[0] and tuple[1] == tuple_of_values[1]:
                return index
    
        logger.info("List of tuples: ")
        logger.info(list_of_tuples)
        logger.info("Tuple_of_values: ")
        logger.info(tuple_of_values)
        # Matches behavior of list.index
        raise ValueError("list.index(x): x not in list")
        
def send_to_clipboard(clip_type, data):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()    
    
def fileToData(filepath):
    image = Image.open(filepath)
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close
    return data

notYetFound = True

if __name__ == '__main__':

    with open("passwordFile.txt", "r") as passwordFile:
            password = passwordFile.readline()
            instaUsername = passwordFile.readline()

    already_liked = []
    
    pokeBot = PokegramBot(instaUsername, password)
    group_to_monitor = 'happy birthday'
    pokeBot.navigate_to_group_chat_directory(group_to_monitor)
    
    #pokeBot.set_appearances_and_likes_to_zero()
    #pokeBot.set_comments_to_zero()
    # filepath = "protoMegaman.jpg"
    # data = fileToData(filepath)
    # send_to_clipboard(win32clipboard.CF_DIB, data)
    
    message_box = pokeBot.get_message_box()
    message_box.click()
    
    
    list_of_usernames = pokeBot.get_list_of_insta_usernames()
    while True:
        # if not pokeBot.pokemonCaught:
            # pokeBot.monitor_gc_for_captures(pokemonName)
            
        # pokeBot.counter_between_sending_pokemon += 1 
        # if pokeBot.pokemonCaught and pokeBot.counter_between_sending_pokemon > 25:
            # pokeBot.counter_between_sending_pokemon = 0
            # pokeBot.pokemonCaught = False
            # fileToPaste = random.choice(os.listdir("Pokemon Images"))
            # logger.info("Sending new pokemon")
            # pokeBot.send_image("Pokemon Images/" + fileToPaste)
            # pokemonName = fileToPaste.partition('.')[0]
            # time.sleep(3)
            
        
        
        # if pokeBot.pokemon_flee_counter > 30:
            # message_box.click()
            # pokeBot.actions.send_keys(pokemonName.capitalize(), " has fled!")
            # pokeBot.actions.send_keys(Keys.RETURN)
            # pokeBot.actions.perform()
            # pokeBot.actions = 4 #Most hacky way to reset action chain
            # pokeBot.actions = ActionChains(pokeBot.driver)
            # pokeBot.pokemonCaught = True
            # pokeBot.pokemon_flee_counter = 0
        
        all_convo_elements = pokeBot.monitor_group_chat()
        
        convo_elements = all_convo_elements[0]
        likes_dictionary_list = all_convo_elements[1]
        try:
            if convo_elements[-1] != pokeBot.last_message:
                #bot.actions.send_keys(Keys.SPACE).perform()
                #pokeBot.pokemon_flee_counter += 1
                if pokeBot.last_message in convo_elements: #If the last message is still visible in convo
                    logger.info("Last message visible, should be on subsequent loads")
                    new_messages = convo_elements[(convo_elements.index(pokeBot.last_message)+1):] #Gets all the messages beyond the last recorded message sent
                    new_new_messages_flag = True
                else:
                    logger.info("Last message not visible, should be on first load")
                    new_messages = convo_elements
                    new_new_messages_flag = False
                    
                #Makes a list of usernames, type:str, that have spoken
                last_username = ''
                list_of_usernames_appeared = []
                list_of_usernames_liked = []
                for message in new_messages:
                    try:
                    #Could use message["text"], but want reply headers to show up differently from usernames
                    #unidecode(str()) strips out the emojis
                        logger.info("Message Text: " + unidecode(str(message["element"].text))) 
                    except Exception as e:
                        logger.error(e)
                        logger.exception("Error: Emoji message")
                    
                    if (message["text"],) in list_of_usernames and message["type"] == "Username": 
                        #Split the message text to get the first word in case the message is a reply
                        list_of_usernames_appeared.append(message["text"])
                        last_username = message["text"]
                                   
                #Incrementing the count of times someone had a comment with 4+ likes
                for like in likes_dictionary_list:
                    if like["element"] not in already_liked:
                        list_of_usernames_liked.append(like["owner"])
                        already_liked.append(like["element"]) 
                        try:
                            logger.info("Like owner message text: " + unidecode(str(like["like_owner_text"]))) 
                        except Exception as e:
                            logger.error(e)
                            logger.exception("Error, picture")
                                            
                username_and_likes_dictionary_list = []
                for username in list_of_usernames: #Get each username from the list of usernames retrieved from database. Note: it'll be a tuple of one element
                    username_and_likes_dictionary = {
                        "Likes" : list_of_usernames_liked.count(username[0]),
                        "Username" : username[0],
                        "Appearances" : list_of_usernames_appeared.count(username[0]),            
                    }
                    username_and_likes_dictionary_list.append(username_and_likes_dictionary)
                     
                
                #logger.info("List_of_usernames_liked: ")
                #logger.info(list_of_usernames_liked)
                username_and_likes_dictionary_tuple = tuple(username_and_likes_dictionary_list)
                with conn:
                    c.executemany("UPDATE groupChatUsernameFrequency SET Appearances = Appearances + :Appearances WHERE Username = :Username", 
                        username_and_likes_dictionary_tuple)
                    c.executemany("UPDATE groupChatUsernameFrequency SET Likes = Likes + :Likes WHERE Username = :Username", 
                        username_and_likes_dictionary_tuple)
                    
                pokeBot.log_all_gc_messages()        
                pokeBot.last_message = convo_elements[-1]
               
                for message in new_messages:
                    if message["text"] == "good evening everyoNe" and new_new_messages_flag:
                        logger.info("Exiting")
                        pokeBot.driver.close()
                        quit()
                    
                new_messages = []
        except Exception as e:
            logger.info("another weird bug")
            logger.exception(e)
        
        
        #Update web page 
        pokeBot.set_realtime_database_to_match_sql()
        
        
        #Reload page if many messages are sent
        if len(convo_elements) > 400:
            logger.info("""
            
            Refreshing Insta
            
            """)
            pokeBot.last_message = pokeBot.refresh_insta_chat(group_to_monitor)
            
        time.sleep(3)
        #For bug testing
        #input("Go again?")
    logger.info("All done")
    
    