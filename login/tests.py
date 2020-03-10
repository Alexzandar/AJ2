import time
 
from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from django.conf import settings

class TestLogin(TestCase):
	
    def setUp(self): 
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options )
        super(TestLogin, self).setUp()

    def test_login_success(self):
        self.driver.get(settings.BASE_URL+"/actionbot")
        uname = self.driver.find_element_by_name("username")
        passd = self.driver.find_element_by_name("password")
        uname.clear()
        passd.clear()
        uname.send_keys("system")
        passd.send_keys("system123")
        submit = self.driver.find_elements_by_xpath("//*[contains(text(), 'Proceed')]")
        submit[0].click()
        print(self.driver.current_url)
        self.assertEqual( settings.BASE_URL+"/actionbot/index/" , self.driver.current_url)
        self.driver.close()
        print("login successful")
    
    def test_login_failure(self):
        self.driver.get(settings.BASE_URL+"/actionbot")
        uname = self.driver.find_element_by_name("username")
        passd = self.driver.find_element_by_name("password")
        uname.clear()
        passd.clear()
        uname.send_keys("invalid user")
        passd.send_keys("invalid pass")
        submit = self.driver.find_elements_by_xpath("//*[contains(text(), 'Proceed')]")
        submit[0].click()
        print(self.driver.current_url)
        self.assertNotEqual(settings.BASE_URL+"/actionbot/index/" , self.driver.current_url)
        self.assertEqual(settings.BASE_URL+"/actionbot/login/" , self.driver.current_url)
        self.driver.close()
        print("login failure")

    def tearDown(self):
        self.driver.quit()