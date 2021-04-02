"""TestBot is a class used to monitor an Instagram group chat."""

import time
import os
import sqlite3
import logging
import firebase_admin
import win32clipboard
import random
import time
import os
import traceback

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from unidecode import unidecode
from firebase_admin import db
from firebase_admin import credentials
from datetime import datetime
from io import BytesIO

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s : %(name)s : %(lineno)s : %(message)s ', datefmt='%m/%d/%Y %I:%M:%S %p')
file_handler = logging.FileHandler('bot.log', mode='w')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)




cred = credentials.Certificate("fir-hosting-test-78ed2-firebase-adminsdk-ojcxp-e2e3a882ed.json")
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://fir-hosting-test-78ed2-default-rtdb.firebaseio.com/'
})

class Error_True_Username_Element_Class():
    
    def __init__(self):
        self.text = "Error_1"

class TestBot: 
    
    def __init__(self, username: str, password: str, group_chat_to_monitor: str, database_to_connect: str):
        """
        Initializes an instance of the TestBot class. 
        
        Logs in to Instagram and Navigates to a group chat.
        
        Args:
            username (str): The Instagram username for the account TestBot is to use.
            password (str): The Instagram password for the account TestBot is to use.
            group_chat_to_monitor (str): group_chat_to_monitor is a substring of the name of the group chat to be monitored, so it can be identified with xpath.
            
        Attributes:
            driver (Selenium.webdriver.Chrome): The Chromedriver that is used to automate browser actions
            base_url (str): The base instgram URL. Not really that useful instead of just hard coding, but it's how the OG tutorial guy 
                            set up a couple functions.
            actions (ActionsChains): Action chain. I do not believe it's actually used for anything at the moment. Might be used later, 
                                     might as well keep it.
            last_message (str): Starts off as an empty string as a filler, but will be a selenium element so TestBot knows any messages 
                                below it must be new.
            last_message_and_username_tuple (str): Starts off as an empty string as a filler, but will be a tuple so TestBot knows any
                                                   messages below the message with that username and text pair must be new. Is not perfect 
                                                   but is close enough as a solution.
        """ 
        
        self.database_name = database_to_connect
        self.conn = sqlite3.connect(database_to_connect + ".db")
        self.c = self.conn.cursor()
        
        self.list_of_usernames = self.get_list_of_insta_usernames()
        
        
        
        self.username = username
        self.password = password
        self.group_chat_to_monitor = group_chat_to_monitor       
        self.driver = webdriver.Chrome('chromedriver.exe')
        self.base_url = 'https://www.instagram.com/'       
        self.actions = ActionChains(self.driver) 
        self.last_message = ''
        self.last_message_and_username_tuple = ''
        self.new_messages_flag = False
        self.loop_counter = 0
        self.login()
        self.navigate_to_insta_inbox()
        self.navigate_to_group_chat()
        
        
        self.set_comments_to_zero()
        #Track the number of comments
        with self.conn:
            self.c.execute("SELECT * FROM comments")
            comment_list = self.c.fetchall()
        self.num_of_comments = max(len(comment_list), 1)
        
        #Insert start time stamp
        start_time = datetime.now()
        start_timestamp = start_time.strftime("%d/%m/%Y %H:%M:%S")
        # It's a list because insert_username_and_timestamp_into_firebase() takes a list as an argument.
        testbot_activity_to_insert = [("Testbot", "Start_Time", start_timestamp)] 
        with self.conn:
            self.c.execute("INSERT INTO comments(Username,Comment,Timestamp) VALUES(?,?,?)", 
                    testbot_activity_to_insert[0]) 
                    
        self.insert_username_and_timestamp_into_firebase(testbot_activity_to_insert)
        self.num_of_comments += 1
                
    def login(self):
        """Navigates to Instagram and logs in."""      
        
        logger.info("Log in start")
        self.driver.get('{}accounts/login/'.format(self.base_url))
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.NAME, 'username'))
            )
            
            self.driver.find_element_by_name('username').send_keys(self.username)
            self.driver.find_element_by_name('password').send_keys(self.password)
            self.driver.find_element_by_css_selector('.Igw0E.IwRSH.eGOV_._4EzTm').click() #Log in button  
            logger.info("Log in complete")
        except Exception as e:
            logger.error(e)
            logger.exception("Log in failed")
            #self.driver.quit()              
    def navigate_to_group_chat(self): 
        """Navigates to a group chat from the Instagram inbox."""
        
        logger.info("Clicking Not Now button")
        #self.driver.maximize_window()
        
        not_now_button_class = 'HoLwm'
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, not_now_button_class)) #Not now button
            )
            not_now = self.driver.find_element_by_class_name(not_now_button_class)
            not_now.click()
            logger.info("Not Now button clicked")
        except Exception as e:
            logger.error(e)
            logger.exception("Clicking Not Now button failed")
            
        try:
            time.sleep(5)
            group_chat = self.driver.find_element_by_partial_link_text(self.group_chat_to_monitor)
            group_chat.click()
        except Exception as e:
            logger.error(e)
            logger.exception("Error, unable to navigate to group chat")
            self.navigate_to_insta_inbox()
            self.navigate_to_group_chat()
            self.loop_counter += 1
            if self.loop_counter > 3:
                self.quit_process()
            
        time.sleep(1)
        
    def navigate_to_insta_inbox(self):
        """
        Navigates to Instagram inbox after being logged in. 
        
        It is simplest to wait 10 seconds to ensure log in then navigate by URL instead of using WebDriverWait.
        """
        
        logger.info("Beginning navigation to Instagram inbox.")
        
        time.sleep(10)
        self.driver.get('https://www.instagram.com/direct/inbox/')
        
    def make_xpath_contains_string(self, list_of_classes: list[str]):
        """
        Makes a contains string from a list of classes(string) for xpath. 
        
        Uses a list and .append instead of just += strings to avoidquadratric run time.        
        Note: Will fall apart if passed argument has <1 classes
        
        Args:
            list_of_classes (list[str]): The list of classes to be put into the contains string.
        
        Returns:
            return_string (str): A string to be used inside the [] of an xpath string.
           
        Example:
        >>> class_list = ['_7UhW9', 'xLCgt']
        >>> make_xpath_contains_string(class_list)
        contains(@class, '_7UhW9') and @class, 'xLCgt')
        """
        
        contains_list = []
        for stringer in list_of_classes[:-1]:
            contains_list.append("contains(@class, '" + stringer + "') and ")
            
        contains_list.append("contains(@class, '" + list_of_classes[-1] + "')")
         
        return_string =  ''.join(contains_list)
        return return_string
        
    def remove_quotes_for_xpath(self, string):
        """
        Splits up a string around the " and return a string that'll work with xpath. 
        
        If there is no ", it puts "" around the string to return so the xpath it's placed in works properly.
        
        Easiest to understand with example.
        
        Args:
            string (str): String that will split around the ".
        Returns:
            return_string (str): String that has been split up.
            
        Example:
        >>> string = "This's a \"sample\" string."
        >>> string2 = remove_quotes_for_xpath(string)
        >>> print(string2)
        concat("This's a ", '"', "sample", '"', " string.")
        
        """
        if '"' in string:
            listed_string = string.split('"')
            
            return_string = "concat(\"" + listed_string[0] + "\", '\"', " 
            for stringer in listed_string[1:-1]:
                return_string += "\"" + stringer + "\", '\"', "
                
            return_string += "\"" + listed_string[-1] + "\")"
            
            return return_string.replace("Æ", "’")
            
            
        string = string.replace("Æ", "’")
        return_string = ('"' + string + '"')
        return return_string
        
    def get_sender_username_from_element_xpath(self, sent_message_xpath):
        """
        Uses the xpath of a sent message to get the username to get the username of the person who sent the message.
        
        Args:
            sent_message_xpath (str): The xpath of the message that we want to know who sent.
        
        Returns:
            actual_username_xpath (str): The xpath to the username we want.
        """
        
        generic_username_class_list = ['_7UhW9', 'PIoXz', 'MMzan', '_0PwGv']
        generic_username_contains_string = self.make_xpath_contains_string(generic_username_class_list)
        generic_username_xpath = "//div[" + generic_username_contains_string + "]"      
        
        capture_span_ancestor_class_list = ['Igw0E', 'Xf6Yq', 'eGOV_', 'ybXk5', '_4EzTm']
        capture_span_ancestor_contains_string = self.make_xpath_contains_string(capture_span_ancestor_class_list)                            
        span_ancestor_xpath = "div[" + capture_span_ancestor_contains_string + "]"        
        username_ancestor_xpath = "(" + sent_message_xpath + "/ancestor::" + span_ancestor_xpath + "/preceding-sibling::div[." + generic_username_xpath + "])[last()]"      
        actual_username_xpath = "(" + username_ancestor_xpath + generic_username_xpath + ")[last()]" 
        
        return actual_username_xpath
        
    def get_sender_username_in_reply_from_element_xpath(self, sent_message_xpath):
        """
        Uses the xpath of a sent message to get the username to get the username of the person who sent the message, but for replies.
        
        Args:
            sent_message_xpath (str): The xpath of the message that we want to know who sent.
        
        Returns:
            actual_reply_username_xpath (str): The xpath to the username we want.
        """
        
        generic_username_class_list = ['_7UhW9', 'PIoXz', 'MMzan', '_0PwGv']
        generic_username_contains_string = self.make_xpath_contains_string(generic_username_class_list)
        generic_username_xpath = "//div[" + generic_username_contains_string + "]"    
        
        message_span_ancestor_that_is_sibling_to_reply_class_list = ['e9_tN', 'JRTzd']
        message_span_ancestor_that_is_sibling_to_reply_contains_string = self.make_xpath_contains_string(message_span_ancestor_that_is_sibling_to_reply_class_list)                          
        span_ancestor_that_is_sibling_to_reply_xpath = "div[" + message_span_ancestor_that_is_sibling_to_reply_contains_string + "]/.."       
        ancestor_of_reply_xpath =  span_ancestor_that_is_sibling_to_reply_xpath + "/preceding-sibling::div"    
        ancestor_of_specific_reply_xpath = sent_message_xpath + "/ancestor::" + ancestor_of_reply_xpath        
        actual_reply_username_xpath = "(" + ancestor_of_specific_reply_xpath + generic_username_xpath + ")[last()]" 
        
        return actual_reply_username_xpath
            
    def find_username_from_message(self, message):
        """
        Returns the string username of the person who sent the message.
        
        Args:
            message (selenium.element): The element of the message sent.
            
        Returns:
            usernamer: The string username of the person who sent the message.
        """
        generic_message_class_list = ['_7UhW9', 'xLCgt', 'p1tLr', 'MMzan', 'KV-D4', 'hjZTB']
        generic_message_contains_string = self.make_xpath_contains_string(generic_message_class_list)
        generic_message_xpath = "//div[" + generic_message_contains_string + "]" 
        
         
        string_to_avoid_quotes = self.remove_quotes_for_xpath(message.text)
        xpath_to_message_spans = """(//span[contains(text(), {})])""".format(string_to_avoid_quotes)   
        message_span_list = self.driver.find_elements_by_xpath(xpath_to_message_spans)
        # Get the most recent message, to exclude messages with same text that appear earlier
        for index, message_span in enumerate(message_span_list):
            if message_span.location["y"] <= message.location["y"]:
                target_message_span_xpath = xpath_to_message_spans + "[" +  str(index+1) + "]" #Already has () around xpath_to_message_spans
                
                username_xpath = self.get_sender_username_from_element_xpath(target_message_span_xpath)
                username_reply_xpath = self.get_sender_username_in_reply_from_element_xpath(target_message_span_xpath)
        
        
        #time.sleep(1) #Maybe just wait for it to load?
        weird_error = False
        username_element_exists = False
        username_reply_element_exists = False
        
        try:
            username_element = self.driver.find_element_by_xpath(username_xpath)
            username_element_exists = True
        except Exception as e:
            #logger.debug(e) #this is annoying, since about half the time it will appear
            #logger.info("username_element does not exist")
            pass
            
        try:
            username_reply_element = self.driver.find_element_by_xpath(username_reply_xpath)
            username_reply_element_exists = True
        except Exception as e:
            #logger.debug(e) #this is annoying, since about half the time it will appear
            #logger.info("username_reply_element does not exist")  
            pass
            
        
            
        
        true_username_containing_element = ''
        if not username_element_exists and not username_reply_element_exists:
            logger.info("Message that could not be found: ")
            logger.info(message.text)
            logger.error("This should not happen, but sometimes does anyways. Problem with how insta displays names.")
            true_username_element = Error_True_Username_Element_Class()
        elif not username_element_exists:
            true_username_element = username_reply_element
        elif not username_reply_element_exists: 
            true_username_element = username_element            
        else:
            if username_element.location["y"] > username_reply_element.location["y"]:
                true_username_element = username_element
            else:
                true_username_element = username_reply_element
                
             
        if " replied to " in true_username_element.text:         
            usernamer = true_username_element.text.split()[0]
        else:    
            usernamer = true_username_element.text
        
        return usernamer

    def get_changed_gc_name(self):
        """Changes self.group_chat_to_monitor to the new name if the gc name is changed."""
        name_change_class_list = ["_7UhW9", "PIoXz", "qyrsm","_0PwGv", "se6yk"]
        name_change_contains_string = self.make_xpath_contains_string(name_change_class_list)
        name_change_xpath = "//span[" + name_change_contains_string + "]"
        
        try:
            name_changes = self.driver.find_elements_by_xpath(name_change_xpath);
            if 8 > len(name_changes[-1].text):
                new_name = name_changes[-1].text
            else:
                new_name = name_changes[-1].text[0:9]
                
            logger.info("New name: ")
            logger.info(new_name)
            self.group_chat_to_monitor = new_name
        except:
            pass
        
    def log_all_gc_messages(self):
        """Actually gets all the elements in the groupchat and logs the new messages."""
        logger.info("Finding messages")
        
        message_class_list = ['_7UhW9', 'xLCgt', 'p1tLr', 'MMzan', 'KV-D4', 'hjZTB']
        message_contains_string = self.make_xpath_contains_string(message_class_list)
        message_xpath = "//div[" + message_contains_string + "]"
        
        excluding_reply_headers_ancestor_xpath = "//div[contains(@class, 'ZyFrc')]"
        
        messages_excluding_reply_headers_xpath = excluding_reply_headers_ancestor_xpath + message_xpath
        messages = self.driver.find_elements_by_xpath(messages_excluding_reply_headers_xpath);
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
        list_of_messages_and_usernames_and_timestamp = []
               
        for message in messages:    
            try:
                username = self.find_username_from_message(message)
                list_of_messages_and_usernames_and_timestamp.append((username, message.text, timestamp))
            except Exception as e: 
                logger.error(e)
                logger.info("Probably someone unsent a message")
            
        if self.last_message_and_username_tuple == '':
            message_list = list_of_messages_and_usernames_and_timestamp
        else:
            logger.debug("list_of_messages_and_usernames_and_timestamp: ")
            logger.debug(list_of_messages_and_usernames_and_timestamp)
            logger.debug("self.last_message_and_username_tuple: ")
            logger.debug(self.last_message_and_username_tuple)
            # Cannot include timestamp, because timestamp will be different each new round
            # Gets index so only messages after that index in the message/username/timestamp list are uploaded
            
            try:
                index = self.return_index_of_value_in_list_of_tuples(list_of_messages_and_usernames_and_timestamp, self.last_message_and_username_tuple)
            except Exception as e: 
                logger.error(e)
                logger.info("Probably someone unsent a message") # Make index the last message to be careful to avoid repeat logging
                index = -1
            message_list = list_of_messages_and_usernames_and_timestamp[index+1:]
            
        logger.info("Message_list: " )
        try:
            logger.info(message_list)
        except Exception as e:
            logger.error(e)
            logger.info("Probably an emoji in a message")

            
        if message_list != []:
            self.last_message_and_username_tuple = (message_list[-1][0], message_list[-1][1])
        
        if self.new_messages_flag:
            for message in message_list:
                #Quit sequence
                if message[1] == "!quit" and message[0] == "jeremy.downey" and self.new_messages_flag:
                    self.quit_process()
                
        self.new_messages_flag = True
        
        with self.conn:
            self.c.executemany("INSERT INTO comments(Username,Comment,Timestamp) VALUES(?,?,?)", 
                message_list) # The other method of python->sqlite requires a dictionary, I don't think it needs to be bothered with here.
            self.num_of_comments += len(message_list)
        
        print("Message list:")
        try:
            print(message_list)          
        except Exception as e:
            logger.error(e)
        
        try:
            self.insert_username_and_timestamp_into_firebase(message_list)
        except Exception as e:
            logger.info("Something went wrong with inserting")
            logger.error(e)
        
        #Count of messages
        logger.info("Check1")
        usernames_and_message_counts = []
        for username in self.list_of_usernames: #Get each username from the list of usernames retrieved from database. Note: it'll be a tuple of one element
            #logger.info("Username: " + username[0])
            #logger.info("Count: ")
            #logger.info(self.count_num_messages(message_list, username[0]))
            username_and_message_count = {
                "Username" : username[0],
                "Messages" : self.count_num_messages(message_list, username[0])            
            }
            usernames_and_message_counts.append(username_and_message_count)
             
        
        username_and_message_count_tuple = tuple(usernames_and_message_counts)
        
        
        with self.conn:
            self.c.executemany("UPDATE numberOfComments SET NumOfComments = NumOfComments + :Messages WHERE Username = :Username", 
                username_and_message_count_tuple)
                 
        self.set_RTDB_match_sql_comment_count()
        try:
            self.get_changed_gc_name()
        except Exception as e:
            pass
        
    def insert_username_and_timestamp_into_firebase(self, username_timestamp_tuple_list):
        """
        Inserts into firebase the list of usernames and timestamps.
        
        Args:
            username_timestamp_tuple_list (list[(str, str)]: The list of usernames and timestamps to be inserted.
        """
         # Get the number of comments already. TODO: 
        #logger.info('Making JSON')
        recordsDict = {}
        try:
            for index, record in enumerate(username_timestamp_tuple_list):
                # The comment number is the index plus the number of comments in the SQL subtract the number of comments we're adding in
                # This way the entire comment database doesn't need to be upload to the firebase Database each time
                recordsDict["comment_num_" + str(index+self.num_of_comments+1-len(username_timestamp_tuple_list))] = {
                   'Username' : record[0],
                   'Timestamp' : record[2],
                   
                }
        except Exception as e:
            logger.info('Something went wrong with making JSON for comments')
            logger.info(e)
        
        comments_ref = db.reference(self.database_name + "/CommentTimestampLog")
        #comments_ref.push(recordsDict)
        #logger.info(recordsDict)
        # May want to use Push() instead, idk
        comments_ref.update(recordsDict)

    def set_comments_to_zero(self):
        """Sets the comments in the sqlite and the firebase databases to empty."""
        
        with self.conn:
                self.c.execute("DELETE FROM comments;")   
                
        for username in self.list_of_usernames:
            with self.conn:
                self.c.execute("UPDATE numberOfComments SET NumOfComments = :zero WHERE Username = :Username", 
                         {'zero': 0, 'Username':username[0]}) 

        recordsDict = {"CommentTimestampLog" : {}}
                
        
        comments_ref = db.reference(self.database_name + "/Members")
        comments_ref.set(recordsDict)
        comments_ref = db.reference(self.database_name + "/CommentTimestampLog")
        comments_ref.set({
                    'comment_num_1': {
                        'filler': 'filler',
                        
                    },
                })
        
    def return_index_of_value_in_list_of_tuples(self, list_of_tuples, tuple_of_values):
        """
        Returns an index in the list of tuples where the first tuple whose [0] and [1] values are the same as the tuple of values.
        
        Args:
            list_of_tuples (list[(str, str, str)]): This is used for the comment/username/timestamp list.
            tuple_of_values (tuple[str, str]): This is used as the last username/message combo.
        Returns:
            index (int): The index of where the tuple of values is found in the list.
        """
        for index, tuple in enumerate(list_of_tuples):
            if tuple[0] == tuple_of_values[0] and tuple[1] == tuple_of_values[1]:
                return index
    
        # Matches behavior of list.index
        raise ValueError("list.index(x): x not in list")
    
    def count_num_messages(self, list_of_messages, username):
        """
        Returns the count of how many times username is in list of messages.
        
        Args:
            list_of_messages (list[(str, str, str)]): This is used for the comment/username/timestamp list.
            username (str): The username we're looking for.
        Returns:
            count (int): The number of times the username is in the list.
        """
        count = 0
        for tuple in list_of_messages:
            if tuple[0] == username:
                count += 1
        
        return count
    
    def refresh_insta_chat(self):
        """Refreshes Instagram and navigates back to the group chat."""
        logger.info("Refreshing")
        self.driver.refresh()
        self.navigate_to_group_chat()
        # return the last message on the refresh page as the point to start counting from
        self.driver.switch_to.window(self.driver.current_window_handle)
        
    def get_list_of_insta_usernames(self):
        """
        Returns the list of insta usernames as a list of tuples of one element
        """
        self.c.execute("SELECT Username FROM numberOfComments WHERE Username IS NOT NULL") #Get all the username's in instagramData
        #print(c.fetchall())
        return self.c.fetchall()
        
    def set_RTDB_match_sql_comment_count(self):
        self.c.execute("SELECT Username, NumOfComments FROM numberOfComments") 
        wholeInstaTable = self.c.fetchall()
        
        recordsDict = {}
        try:
            for record in wholeInstaTable:
                recordsDict[record[0].replace('.', ',')] = {
                   'Message_Count' : record[1],
                   'Username' : record[0].replace('.', ','),\
                }
        except Exception as e:
            logger.info('Something went wrong with making JSON')
            logger.info(e)
        
        members_ref = db.reference(self.database_name + "/Members")
        #logger.info(recordsDict)
        members_ref.set(recordsDict)
        
    def quit_process(self):
        logger.info("Quitting!")
        quit_time = datetime.now()
        quit_timestamp = quit_time.strftime("%d/%m/%Y %H:%M:%S")
        # It's a list because insert_username_and_timestamp_into_firebase() takes a list as an argument.
        testbot_activity_to_insert = [("Testbot", "Quit_Time", quit_timestamp)] 
        with self.conn:
            self.c.execute("INSERT INTO comments(Username,Comment,Timestamp) VALUES(?,?,?)", 
                    testbot_activity_to_insert[0]) 
                    
        self.insert_username_and_timestamp_into_firebase(testbot_activity_to_insert)
        self.driver.close()
        quit()
               