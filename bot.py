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
			
		senders_dictionary_list = []
		for username in message_senders:
			sender_dictionary = {
				"element" : username,
				"type" : "Username",
				"text" : username.text,
			}
			senders_dictionary_list.append(sender_dictionary)
			
		#Change text in reply messages to get first word, so it becomes effectively identical to regular username tag
		for username in message_sender_replies:
			sender_dictionary = {
				"element" : username,
				"type" : "Username",
				"text" : username.text.split()[0],
			}
			senders_dictionary_list.append(sender_dictionary)
		
		#Puts the senders dictionary list into messages dictionary list so one long list can be sorted and returned
		messages_dictionary_list.extend(senders_dictionary_list)
		all_chat_convo_elements = messages_dictionary_list
		 #All of group chat does not load immeadiately
		#for convo_element in all_chat_convo_elements:
		#	print("Convo element: ", convo_element.text)
		
		all_chat_convo_elements.sort(key=lambda x:x["element"].location["y"])
		# print("All chat convo elements: ")
		# print(all_chat_convo_elements)
		
		# print("Printing messages")
		# for messageNum in range(len(all_chat_convo_elements)):
			# print(all_chat_convo_elements[messageNum].text)
		
		return all_chat_convo_elements
		
		
		
			
			
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
	
	
if __name__ == '__main__':
	#Getting the password
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
	
	while True:
		convo_elements = bot.monitor_group_chat(group_to_monitor)
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
			list_of_usernames_appeared = []
			for message in newMessages:
				try:
					print("Message Text: ", message["element"].text) #Could use message["text"], but want replies to show up differently
				except:
					print("Error: Emoji message")
				
				if (message["text"],) in list_of_usernames and message["type"] == "Username": #Checks if the message is an username, for recording purposes
					#I split the message text to get the first word in case the message is a reply
					list_of_usernames_appeared.append(message["text"])
				
						
			for username in list_of_usernames: #Get each username from the list of usernames retrieved from database. Note: it'll be a tuple of one element
				#print("Check two")
				appearances = list_of_usernames_appeared.count(username[0])
				#print(newMessages)
				
				with conn:
					c.execute("UPDATE groupChatUsernameFrequency SET Appearances = Appearances + :Appearances WHERE Username = :Username", 
					{'Appearances': appearances, 'Username':username[0]})
					#print(username[0])
					#print(appearances)
					
			lastMessage = convo_elements[-1]
			#lastMessageText = lastMessage.text
			
			#Checking if someone typed !snowmobile
			print("newNewMessageFlag: ", newNewMessagesFlag)
			for message in newMessages:
				if message["text"] == "!exit" and newNewMessagesFlag:
					print("Exiting")
					bot.driver.close()
					quit()
					# lastMessageFile = open("lastMessage.txt", "w")
					# lastMessageFile.write(lastMessage)
					# lastMessageFile.close()
				
			newMessages = []
		time.sleep(3)
		#input("Go again?")

		
	print("All done")
	
	