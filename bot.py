from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import sqlite3

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
		self.message_css_selector = "._7UhW9.xLCgt.MMzan.KV-D4.p1tLr.hjZTB" #"._7UhW9.xLCgt.MMzan.KV-D4.p1tLr.hjZTB" #.JdNBm
		#Message senders has the same css clases as the time stamps do for the bottom level div, so we're also specifying that it needs a parent div with
		#specific classes
		self.message_sender_css_selector = ".Igw0E.IwRSH.eGOV_._4EzTm.bkEs3.Qjx67.aGBdT > ._7UhW9.PIoXz.MMzan._0PwGv.fDxYl" #"._7UhW9.PIoXz.MMzan._0PwGv.fDxYl"
		self.replies_css_selector = ".Igw0E.IwRSH.eGOV_._4EzTm.bkEs3.soMvl.JI_ht.DhRcB > ._7UhW9.PIoXz.MMzan._0PwGv.uL8Hv"
		#self.reply_likes_css_selector = ".Xn4Qt"
		self.likes_css_selector = "._7UhW9.PIoXz.MMzan.KV-D4.uL8Hv"
		self.actions = ActionChains(self.driver)				
		 
		
	def login(self):
		print("Log in start")
		self.driver.get('{}accounts/login/'.format(self.base_url))
		try:
			element = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.NAME, 'username'))
			)
			
			self.driver.find_element_by_name('username').send_keys(self.username)
			self.driver.find_element_by_name('password').send_keys(self.password)
			self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button').click() #Log in button
			print("Log in complete")
		except:
			print("Log in failed")
			self.driver.quit()
		
				
	def navigate_to_group_chat(self, group_to_monitor):
		#time.sleep(5)
		print("Beginning monitoring")
		try:
			element = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.CLASS_NAME, 'xWeGp')) #KdEwV
			)
			print("Monitoring found complete")
		except:
			print("Monitoring failed failed")
			#self.driver.quit()
		groupchat_directory = self.driver.find_element_by_class_name('xWeGp') #KdEwV
		groupchat_directory.click()
		print("Complete navigation to group chat directory")
		
		print("Clicking Not Now button")
		try:
			element = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.CLASS_NAME, 'HoLwm'))
			)
		except:
			print("Clicking Not Now button failed")
			#self.driver.quit()
		notNow = self.driver.find_element_by_class_name('HoLwm')
		notNow.click()
		
		print("Not Now button clicked")
		#aOOlW   HoLwm 
		
		print("Begin navigating to group chat")
		try:
			element = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, group_to_monitor))
			)
		except:
			print("Error, unable to navigate to group chat")
			#self.driver.quit()
		group_chat = self.driver.find_element_by_partial_link_text(group_to_monitor)
		group_chat.click()
		
	
	def monitor_group_chat(self, group_to_monitor):
		print("Finding messages")
		try:
			element = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, self.message_senders_css_selector))
			)
		except:
			pass
			#This may not actually work
			#print("Error, unable to find messages")
			
		#get the messages and message senders
		time.sleep(3)
		messages = self.driver.find_elements_by_css_selector(self.message_css_selector);
		message_senders = self.driver.find_elements_by_css_selector(self.message_sender_css_selector);
		message_sender_replies = self.driver.find_elements_by_css_selector(self.replies_css_selector);
		likes = self.driver.find_elements_by_css_selector(self.likes_css_selector);
		#messages.extend(message_senders)
		
		
		messages_dictionary_list = []
		for message in messages:
			#print("Message text bug test: ", message.text)
			try:
				message_dictionary = {
					"element" : message,
					"type" : "Message",
					"text" : message.text,
				}
				messages_dictionary_list.append(message_dictionary)
			except:
				print("Message text bug test: ", message.text)
				self.driver.close() 
			
		#senders_dictionary_list = []
		for username in message_senders:
			sender_dictionary = {
				"element" : username,
				"type" : "Username",
				"text" : username.text,
			}
			#senders_dictionary_list.append(sender_dictionary)
			messages_dictionary_list.append(sender_dictionary)
			
		#Change text in reply messages to get first word, so it becomes effectively identical to regular username tag
		for username in message_sender_replies:
			sender_dictionary = {
				"element" : username,
				"type" : "Username",
				"text" : username.text.split()[0],
			}
			#senders_dictionary_list.append(sender_dictionary)
			messages_dictionary_list.append(sender_dictionary)
			
		#Need seperate list for likes because likes are in their own order
		like_dictionary_list = []
		for like in likes:
			print(like.text)
			valid_num_of_likes = False
			if like.text[-1].isdigit():
				if int(like.text[-1]) > 3:
					valid_num_of_likes = True
			
			if "+" in like.text or valid_num_of_likes:
				#Different classes for text, photos, etc. 
				#Index of the like, to find which like it is
				index = likes.index(like)
				#print("Like text: ", like.text)
				like_contains_string = """contains(@class, '_7UhW9') and contains(@class, 'PIoXz') and contains(@class, 'MMzan')
							and contains(@class, 'KV-D4') and contains(@class, 'uL8Hv')""" 
				
				#The xpath to the what contains the +1
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
															
				
				
				#username_owner_xpath = "(" + like_owner_xpath + "/preceding-sibling::div)[last()]" + actual_username_path
				
				
				#test_xpath = self.driver.find_element_by_xpath(actual_username_path)
				#print("Test xpath: ", test_xpath.text)
				like_owner =  self.driver.find_element_by_xpath(like_owner_xpath)
				username_owner = self.driver.find_element_by_xpath(actual_username_path)
				#username_owner.location_once_scrolled_into_view()
				#username_owner.click()
				
				#f = open("filetest"+str(index)+".png", "wb")
				#f.write(username_owner.screenshot_as_png)
				#f.close()
				#print("Username: ", username_owner.text)
				like_dictionary = {
					"element" : like,
					"type" : "Like",
					"text" : like.text.split()[-1],
					"owner" : username_owner.text,
					"like_owner_text" : like_owner.text,
				}
				#print("Like owner: ", username_owner.text)
				#print("Like text: ", like.text)
				like_dictionary_list.append(like_dictionary)
		
		#NOTE: no longer using all_chat_convo_elements, just using messages_dictionary_list
		
		#Puts the senders dictionary list into messages dictionary list so one long list can be sorted and returned
		#messages_dictionary_list.extend(senders_dictionary_list)
		#all_chat_convo_elements = messages_dictionary_list
		 #All of group chat does not load immeadiately
		#for convo_element in all_chat_convo_elements:
		#	print("Convo element: ", convo_element.text)
		
		messages_dictionary_list.sort(key=lambda x:x["element"].location["y"])
		# print("All chat convo elements: ")
		# print(all_chat_convo_elements)
		
		# print("Printing messages")
		# for messageNum in range(len(all_chat_convo_elements)):
			# print(all_chat_convo_elements[messageNum].text)
		
		return [messages_dictionary_list, like_dictionary_list]
		
		
		
			
			
	def nav_user(self, user):
		print("Navigating to person")
		self.driver.get('{}{}/'.format(self.base_url, user))
		print("Finished avigating to person")
		
		
	def follow_user(self, user):
		print("Follow begin")
		self.nav_user(user)
		try:
			element = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.CLASS_NAME, '_6VtSN'))
			)
			print("Monitoring found complete")
		except:
			print("Monitoring failed failed")
			self.driver.quit()
			
		follow_button = self.driver.find_element_by_class_name('_6VtSN')
		#time.sleep(4)
		follow_button.click()
		print("Follow complete")


	def get_info(self):
		try:
			element = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.CLASS_NAME, '_6VtSN'))
			)
		except:
			self.driver.quit()
		
			
		info = self.driver.find_elements_by_class_name('g47SY')
		print(info[0].text)
		print(info[1].text)
		print(info[2].text)
		
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
			print(person[0])
			info = self.get_info()
			with conn:
				c.execute("UPDATE instagramData SET Posts = :Posts, Followers = :Followers, Following = :Following WHERE Username = :Username", 
				{'Posts': info[0], 'Followers': info[1], 'Following': info[2], 'Username':person[0]})
		print("Done Updating")
			
			
def insert_usernames_into_instagram_data():
	"""
	Insert the usernames from the ricescoreData table into the instagramData table
	if they're not already present
	"""
	with conn:
		c.execute("SELECT Username FROM ricescoreData WHERE Username IS NOT NULL") #Get everyone's usernames
		riceUsernames = c.fetchall()
		c.execute("SELECT Username FROM instagramData WHERE Username IS NOT NULL") #Get all the username's in instagramData
		instaUsernames =  c.fetchall()
		
		usernamesToAddToInsta = list(set(riceUsernames) - set(instaUsernames))
		print(usernamesToAddToInsta)
		for username in usernamesToAddToInsta: #, {'username': username}
			#print(username[0])
			#c.execute("INSERT INTO employees VALUES (:first, :last, :pay)", {'first': emp.first, 'last': emp.last, 'pay': emp.pay})
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
	#Getting the password
	
	#Uncomment to reset database
	set_appearances_and_likes_to_zero()
	#quit()
	
	#set_appearances_and_likes_to_zero()
	passwordFile = open("passwordFile.txt", "r")
	password = passwordFile.read()
	passwordFile.close()

	bot = InstagramBot('testbottesting', password)
	#insert_usernames_into_instagram_data()
	#list_of_people_to_check = [['itsniqqi']]
	#list_of_people_to_check = get_list_of_insta_usernames()
	#bot.update_peoples_info(list_of_people_to_check)
	group_to_monitor = 'UofTea'
	bot.navigate_to_group_chat(group_to_monitor)
	lastMessageIndex = 0
	#Get list of new messages
	#[("jeremy.downey",), ("catherinee.13",)]
	list_of_usernames = get_list_of_insta_usernames()
	newNewMessagesFlag = False #Flag so !quit from old convos doesn't trigger bot to quit
	newMessages = ''
	
	lastMessage = ''
	# try:
		# element = WebDriverWait(bot.driver, 10).until(
			# EC.presence_of_element_located((By.CSS_SELECTOR, '.frMpI.-sxBV'))
		# )
	# except:
		# pass
	
	# background_to_click = bot.driver.find_element_by_css_selector('.frMpI.-sxBV')
	#List of like elements already noted into database
	already_liked = []
	while True:
		all_convo_elements = bot.monitor_group_chat(group_to_monitor)
		convo_elements = all_convo_elements[0]
		likes_dictionary_list = all_convo_elements[1]
		if convo_elements[-1] != lastMessage:
			#background_to_click.click()#scroll down
			bot.actions.send_keys(Keys.SPACE).perform()
			if lastMessage in convo_elements: #If the last message is still visible in convo
				print("Last message visible, should be on subsequent loads")
				newMessages = convo_elements[(convo_elements.index(lastMessage)+1):] #Gets all the messages beyond the last recorded message sent
				newNewMessagesFlag = True
			else:
				print("Last message not visible, should be on first load")
				newMessages = convo_elements
				newNewMessagesFlag = False
				
			#Makes a string list of usernames that have spoken
			lastUsername = ''
			list_of_usernames_appeared = []
			list_of_usernames_liked = []
			for message in newMessages:
				try:
					print("Message Text: ", message["element"].text) #Could use message["text"], but want replies to show up differently
				except:
					print("Error: Emoji message")
				
				if (message["text"],) in list_of_usernames and message["type"] == "Username": #Checks if the message is an username, for recording purposes
					#I split the message text to get the first word in case the message is a reply
					list_of_usernames_appeared.append(message["text"])
					lastUsername = message["text"]
					
				
			#Incrementing the count of times someone had a comment with 4+ likes
			#print("likes_dictionary_list: ")
			#print(likes_dictionary_list)
			for like in likes_dictionary_list:
				#print("Like in likes_dictionary_list check")
				if like["element"] not in already_liked:
					#print("Like element: ", like)
					#print("Already liked: ", like)
					#print("if like not in already_liked check")
					list_of_usernames_liked.append(like["owner"])
					already_liked.append(like["element"]) 
					try:
						print("Like owner message text: ", like["like_owner_text"])
					except:
						print("picture")
						
					
			username_and_likes_dictionary_list = []
			for username in list_of_usernames: #Get each username from the list of usernames retrieved from database. Note: it'll be a tuple of one element
				#print("Check two")
				username_and_likes_dictionary = {
					"Likes" : list_of_usernames_liked.count(username[0]),
					"Username" : username[0],
					"Appearances" : list_of_usernames_appeared.count(username[0]),
				
				}
				username_and_likes_dictionary_list.append(username_and_likes_dictionary)
				#Old code, from before executemany()
				#appearances = list_of_usernames_appeared.count(username[0])
				#likesAppeared = list_of_usernames_liked.count(username[0])
				#print(newMessages)
				
				# with conn:
					# c.execute("UPDATE groupChatUsernameFrequency SET Appearances = Appearances + :Appearances WHERE Username = :Username", 
					# {'Appearances': appearances, 'Username':username[0]})
					# #print(username[0])
					# #print(appearances)
			
			username_and_likes_dictionary_tuple = tuple(username_and_likes_dictionary_list)
			with conn:
				c.executemany("UPDATE groupChatUsernameFrequency SET Appearances = Appearances + :Appearances WHERE Username = :Username", 
					username_and_likes_dictionary_tuple)
				c.executemany("UPDATE groupChatUsernameFrequency SET Likes = Likes + :Likes WHERE Username = :Username", 
					username_and_likes_dictionary_tuple)
					
			lastMessage = convo_elements[-1]
			#lastMessageText = lastMessage.text
			
			#Checking if someone typed !snowmobile
			#print("newNewMessageFlag: ", newNewMessagesFlag)
			for message in newMessages:
				if message["text"] == "!love_you_all" and newNewMessagesFlag:
					print("Exiting")
					bot.driver.close()
					quit()
					# lastMessageFile = open("lastMessage.txt", "w")
					# lastMessageFile.write(lastMessage)
					# lastMessageFile.close()
				
			newMessages = []
		time.sleep(3)
		
		#For bug testing
		#input("Go again?")

		
	print("All done")
	
	