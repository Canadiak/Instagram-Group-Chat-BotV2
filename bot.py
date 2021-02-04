import time
import os
import sqlite3
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from unidecode import unidecode

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s : %(name)s : %(message)s')
file_handler = logging.FileHandler('bot.log', mode='w')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


conn = sqlite3.connect('groupchatDatabase.db')
c = conn.cursor()


class InstagramBot: 
    
    def __init__(self, username, password):
        """
        Initializes an instance of the InstagramBot class. 
        Call the login to authenticate a user with IG.
        
        Args:
            username:str: The Instagram username for an user
            password:str: The Instagram password for a user
            
        Attributes:
            driver:Selenium.webdriver.Chrome: The Chromedriver that is used to automate browser actions
            
        """     
        self.username = username
        self.password = password
        self.base_url = 'https://www.instagram.com/'
        self.driver = webdriver.Chrome('chromedriver.exe')
        self.login()    
        self.message_css_selector = "._7UhW9.xLCgt.MMzan.KV-D4.p1tLr.hjZTB" #
        # Message senders has the same css clases as the time stamps do for the bottom level div, 
        # so we're also specifying that it needs a parent div withspecific classes
        self.message_sender_css_selector = ".Igw0E.IwRSH.eGOV_._4EzTm.bkEs3.Qjx67.aGBdT > ._7UhW9.PIoXz.MMzan._0PwGv.fDxYl" 
        self.replies_css_selector = ".Igw0E.IwRSH.eGOV_._4EzTm.bkEs3.soMvl.JI_ht.DhRcB > ._7UhW9.PIoXz.MMzan._0PwGv.uL8Hv"
        self.likes_css_selector = "._7UhW9.PIoXz.MMzan.KV-D4.uL8Hv"
        self.actions = ActionChains(self.driver)  #Action chain for pressing space to scroll down chat    
        
    def login(self):
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
        except:
            logger.exception("Log in failed")
            #self.driver.quit()        
            

    def navigate_to_group_chat(self, group_to_monitor):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, group_to_monitor))
            )
        except:
            logger.exception("Error, unable to navigate to group chat")
            #self.driver.quit()
        group_chat = self.driver.find_element_by_partial_link_text(group_to_monitor)
        group_chat.click()
        
    
    def navigate_to_group_chat_directory(self, group_to_monitor):
        logger.info("Beginning navigation to group chat directory")
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'xWeGp')) #Button to click for group chat directory
            )
            groupchat_directory = self.driver.find_element_by_class_name('xWeGp') 
            groupchat_directory.click()
            logger.info("Complete navigation to group chat directory")
        except:
            logger.exception("Navigation to group chat directory failed")
            #self.driver.quit()
        
        
        logger.info("Clicking Not Now button")
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'HoLwm')) #Not now button
            )
            not_now = self.driver.find_element_by_class_name('HoLwm')
            not_now.click()
            logger.info("Not Now button clicked")
        except:
            logger.exception("Clicking Not Now button failed")
            #self.driver.quit()
        
        
        
        #aOOlW   HoLwm 
        
        logger.info("Begin navigating to group chat")
        self.navigate_to_group_chat(group_to_monitor)
          
    def monitor_group_chat(self):
        logger.info("Finding messages")
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.message_senders_css_selector))
            )
        except:
            pass
            
        #get the messages and message senders
        time.sleep(3)
        messages = self.driver.find_elements_by_css_selector(self.message_css_selector);
        message_senders = self.driver.find_elements_by_css_selector(self.message_sender_css_selector);
        message_sender_replies = self.driver.find_elements_by_css_selector(self.replies_css_selector);
        likes = self.driver.find_elements_by_css_selector(self.likes_css_selector);
        
        try:
            messages_dictionary_list = []      
            for message in messages:
               
                    message_dictionary = {
                        "element" : message,
                        "type" : "Message",
                        "text" : message.text,
                    }
                    messages_dictionary_list.append(message_dictionary)
               
                    
            for username in message_senders:
                sender_dictionary = {
                    "element" : username,
                    "type" : "Username",
                    "text" : username.text,
                }
                messages_dictionary_list.append(sender_dictionary)           
            #Change text in reply messages header to get first word, so it becomes effectively identical to regular message header
            for username in message_sender_replies:
                sender_dictionary = {
                    "element" : username,
                    "type" : "Username",
                    "text" : username.text.split()[0],
                }
                messages_dictionary_list.append(sender_dictionary)
                
            #Need seperate list for likes because likes are in their own order
            like_dictionary_list = []
            #Count index because finding the location of like in the html with xpath takes index
            for index, like in enumerate(likes):
                valid_num_of_likes = False
                if like.text[-1].isdigit():
                    if int(like.text[-1]) > 3:
                        valid_num_of_likes = True
                
                if "+" in like.text or valid_num_of_likes:              
                    like_contains_string = """contains(@class, '_7UhW9') and contains(@class, 'PIoXz') and contains(@class, 'MMzan')
                                and contains(@class, 'KV-D4') and contains(@class, 'uL8Hv')""" 
                 
                    #Index+1 because xpath starts counting at 1, not 0
                    like_xpath = "(//div[" + like_contains_string + "])[" + str(index+1) + "]"
                                
                    ancestor_of_like_contains_string = """contains(@class, 'Igw0E') and contains(@class, 'Xf6Yq') and contains(@class, 'eGOV_')
                                            and contains(@class, 'ybXk5') and contains(@class, '_4EzTm')"""             
                    
                    ancestor_of_like_xpath = "div[" + ancestor_of_like_contains_string + "]"
                    
                    #What the like is on, e.g a comment or picture
                    like_owner_xpath = like_xpath + "/ancestor::" + ancestor_of_like_xpath               
                    
                    actual_username_contains_string = """contains(@class, '_7UhW9') and contains(@class, 'PIoXz') and contains(@class, 'MMzan')
                                and contains(@class, '_0PwGv') and contains(@class, 'fDxYl')"""
                                
                    
                    
                    #Xpath to an username
                    generic_username_path = "//div[" + actual_username_contains_string + "]"
                    
                    #Expath to the div that contains the username we want
                    username_owner_xpath = "(" + like_owner_xpath + "/preceding-sibling::div[." + generic_username_path + "])[last()]"      
                                
                    #Xpath to the username we want
                    actual_username_path = username_owner_xpath + generic_username_path #[" + actual_username_contains_string + "]"              
                    #username_ancestor_xpath = "//div[" + actual_username_path
                    
                    
                    
                    #In case the username we want is in a reply
                    
                    actual_username_in_reply_contains_string = """contains(@class, '_7UhW9') and contains(@class, 'PIoXz') and contains(@class, 'MMzan')
                                and contains(@class, '_0PwGv') and contains(@class, 'uL8Hv')"""
                                
                    generic_username_in_reply_path = "//div[" + actual_username_in_reply_contains_string + "]"
                    
                    #Expath to the div that contains the username we want
                    username_in_reply_owner_xpath = "(" + like_owner_xpath + "/preceding-sibling::div[." + generic_username_in_reply_path + "])[last()]"      
                                
                    #Xpath to the username we want
                    actual_username_in_reply_path = username_in_reply_owner_xpath + generic_username_in_reply_path
                  
                    #username_owner_xpath = "(" + like_owner_xpath + "/preceding-sibling::div)[last()]" + actual_username_path                              
                    #test_xpath = self.driver.find_element_by_xpath(actual_username_path)
                    like_owner =  self.driver.find_element_by_xpath(like_owner_xpath)
                    username_owner = self.driver.find_element_by_xpath(actual_username_path)
                    
                    # I got the xpaths to the username in replies wrong, but I could probably fix at some point and it'd be better
                    # try:
                        # element = WebDriverWait(self.driver, 10).until(
                            # EC.presence_of_element_located((By.XPATH, self.actual_username_in_reply_path))
                        # )
                        # username_owner_in_reply = self.driver.find_element_by_xpath(actual_username_in_reply_path)
                        # if username_owner_in_reply.location["y"] > username_owner.location["y"]:
                            # username_owner = username_owner_in_reply
                        # logger.info("Username owner in reply text: ")
                        # logger.info(username_owner_in_reply.text)
                        # logger.info("Check1")
                        # logger.info(username_owner.text)
                    # except:
                        # logger.debug("actualy_username_in_reply_path isn't loading I think")
                        # pass
                        
                    #with open("filetest"+str(index)+".png", "wb") as f
                    #   f.write(username_owner.screenshot_as_png) 
                    like_dictionary = {
                        "element" : like,
                        "type" : "Like",
                        "text" : like.text.split()[-1],
                        "owner" : username_owner.text.split()[0],
                        "like_owner_text" : unidecode(str(like_owner.text)),
                    }
                    if " replied to " in like_dictionary["like_owner_text"]:
                        like_dictionary["owner"] = like_dictionary["like_owner_text"].split()[0]
                        
                    logger.info("Like dictionary: ")
                    logger.info(like_dictionary)
                    like_dictionary_list.append(like_dictionary) 
                    
        except:
                # logger.exception("Error, made a png log")
                # f = open("filetest.png", "wb")
                # f.write(message.screenshot_as_png)
                # f.close
                logger.error("Something went wrong in the dictionary making")
                return self.monitor_group_chat()
        try:
            messages_dictionary_list.sort(key=lambda x:x["element"].location["y"])
        except:
            logger.error("Something went wrong in the sorting")
            return self.monitor_group_chat()
        
        
        return [messages_dictionary_list, like_dictionary_list]
                  
    def nav_user(self, user):
        logger.info("Navigating to person")
        self.driver.get('{}{}/'.format(self.base_url, user))
        logger.info("Finished avigating to person")
             
    def follow_user(self, user):
        self.nav_user(user)
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, '_6VtSN'))
            )
        except:
            logger.exception("Following failed")
            self.driver.quit()
            
        follow_button = self.driver.find_element_by_class_name('_6VtSN')
        follow_button.click()
        logger.info("Follow complete")
        
    def get_info(self):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, '_6VtSN'))
            )
        except:
            self.driver.quit()
        
            
        info = self.driver.find_elements_by_class_name('g47SY')
        logger.info(info[0].text)
        logger.info(info[1].text)
        logger.info(info[2].text)
        
        info[0] = info[0].text.replace(',', '')
        info[1] = info[1].text.replace(',', '')
        info[2] = info[2].text.replace(',', '')
        
        # strippedInfoArray = []
        # strippedInfoArray.append(info[0].text)
        # strippedInfoArray.append(info[1].text)
        # strippedInfoArray.append(info[2].text)
        
        # strippedInfoArray[0] = strippedInfoArray[0].replace(',', '')
        # strippedInfoArray[1] = strippedInfoArray[1].replace(',', '')
        # strippedInfoArray[2] = strippedInfoArray[2].replace(',', '')
        return info
          
    def update_peoples_info(self, people_to_check):
        info_array = []
        for person in people_to_check:
            self.nav_user(person[0])
            logger.info(person[0])
            info = self.get_info()
            with conn:
                c.execute("UPDATE instagramData SET Posts = :Posts, Followers = :Followers, Following = :Following WHERE Username = :Username", 
                {'Posts': info[0], 'Followers': info[1], 'Following': info[2], 'Username':person[0]})
        logger.info("Done Updating")
            
    
    def update_insta_stats_in_database(self):
        insert_usernames_into_instagram_data()
        list_of_people_to_check = get_list_of_insta_usernames()
        self.update_peoples_info(list_of_people_to_check)
        
    def refresh_insta_chat(self, group_to_monitor):
        already_liked = []
        self.driver.refresh()
        self.navigate_to_group_chat(group_to_monitor)
        # return the last message on the refresh page as the point to start counting from
        return self.monitor_group_chat()[0][-1]["element"]
       
def insert_usernames_into_instagram_data():
    """
    Insert the usernames from the ricescoreData table into the instagramData table
    if they're not already present
    """
    with conn:
        c.execute("SELECT Username FROM ricescoreData WHERE Username IS NOT NULL") #Get everyone's usernames
        rice_usernames = c.fetchall()
        c.execute("SELECT Username FROM instagramData WHERE Username IS NOT NULL") #Get all the username's in instagramData
        insta_usernames =  c.fetchall()
        
        usernames_to_add_to_insta = list(set(rice_usernames) - set(insta_usernames))
        logger.info(usernames_to_add_to_insta)
        for username in usernames_to_add_to_insta: #, {'username': username}
            c.execute("INSERT INTO instagramData (Username) VALUES (:username)", {'username': username[0]})


def get_list_of_insta_usernames():
    """
    Returns the list of insta usernames as a list of tuples of one element
    """
    c.execute("SELECT Username FROM instagramData WHERE Username IS NOT NULL") #Get all the username's in instagramData
    print(c.fetchall)
    return c.fetchall()
    
    
def set_appearances_and_likes_to_zero():
    
    list_of_usernames = get_list_of_insta_usernames()
    for username in list_of_usernames:
        with conn:
            c.execute("UPDATE groupChatUsernameFrequency SET Appearances = :Appearances WHERE Username = :Username", 
                     {'Appearances': 0, 'Username':username[0]})
            c.execute("UPDATE groupChatUsernameFrequency SET Likes = :Likes WHERE Username = :Username", 
                     {'Likes': 0, 'Username':username[0]})
    
    
    
if __name__ == '__main__':
    
    #Uncomment to reset database
    set_appearances_and_likes_to_zero()
    
    #Getting the password
    with open("passwordFile.txt", "r") as passwordFile:
        password = passwordFile.readline()
        instaUsername = passwordFile.readline()
        
    bot = InstagramBot(instaUsername, password)
    
    group_to_monitor = 'UofTea'
    bot.navigate_to_group_chat_directory(group_to_monitor)
    last_messageIndex = 0
    #Get list of new messages
    #[("jeremy.downey",), ("catherinee.13",)]
    list_of_usernames = get_list_of_insta_usernames()
    new_new_messages_flag = False #Flag so !quit from old convos doesn't trigger bot to quit
    new_messages = ''  
    last_message = ''
    #List of like elements already noted into database
    already_liked = []
    
    # logger.info("Testing location of single element")
    # try:
        # element = WebDriverWait(bot.driver, 10).until(
            # EC.presence_of_element_located((By.CSS_SELECTOR, self.message_senders_css_selector))
        # )
    # except:
        # pass
        
    # messages = bot.driver.find_elements_by_css_selector(bot.message_css_selector);
    
    # message = messages[-1]
    # while True:
        # time.sleep(3)
        # logger.info("Messgae location: " + str(message.location["y"]))
        # logger.info("Message text: " + unidecode(str(message.text)))
        
    while True:
        all_convo_elements = bot.monitor_group_chat()
        convo_elements = all_convo_elements[0]
        likes_dictionary_list = all_convo_elements[1]
        if convo_elements[-1] != last_message:
            bot.actions.send_keys(Keys.SPACE).perform()
            if last_message in convo_elements: #If the last message is still visible in convo
                logger.info("Last message visible, should be on subsequent loads")
                new_messages = convo_elements[(convo_elements.index(last_message)+1):] #Gets all the messages beyond the last recorded message sent
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
                except:
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
                    except:
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
                    
            last_message = convo_elements[-1]
           
            for message in new_messages:
                if message["text"] == "!fuck_you_xi" and new_new_messages_flag:
                    logger.info("Exiting")
                    bot.driver.close()
                    quit()
                
            new_messages = []
        time.sleep(3)
        
        #Reload page if many messages are sent
        if len(convo_elements) > 200:
            logger.info("""
            
            Refreshing Insta
            
            """)
            last_message = bot.refresh_insta_chat(group_to_monitor)
        #For bug testing
        #input("Go again?")
    logger.info("All done")
    
    