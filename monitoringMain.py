"""Script to monitor an Instagram Groupchat using the TestBot class."""
import time

from testbotClass import TestBot
from testbotClass import c
from testbotClass import default_app
from testbotClass import logger

if __name__ == '__main__':
    
    with open("passwordFile.txt", "r") as passwordFile:
        password = passwordFile.readline()
        instaUsername = passwordFile.readline()
    
    
    group_chat_to_monitor = "Test"
    testBot = TestBot(instaUsername, password, group_chat_to_monitor)
    
    generic_message_class_list = ['_7UhW9', 'xLCgt', 'p1tLr', 'MMzan', 'KV-D4', 'hjZTB']
    generic_message_contains_string = testBot.make_xpath_contains_string(generic_message_class_list)
    last_element = ''
    while True: 
        
        
        message_elements = testBot.driver.find_elements_by_xpath("//div[" + generic_message_contains_string + "]")
        if last_element != message_elements[-1]:
            testBot.log_all_gc_messages() 
            
        last_element = message_elements[-1]
        
        if len(message_elements) > 200:
            testBot.refresh_insta_chat()
            last_element = testBot.driver.find_elements_by_xpath("//div[" + generic_message_contains_string + "]")[-1]
            
        time.sleep(3)