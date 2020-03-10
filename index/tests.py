import time

from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

class Login():

    def setUp(self): 
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")


        chrome_driver = os.getcwd() + "\\chromedriver.exe"
        chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options )
        return self.driver

    def login_succes(self):
        self.driver.get("http://127.0.0.1:8000/actionbot")
        uname = self.driver.find_element_by_name("username")
        passd = self.driver.find_element_by_name("password")
        uname.clear()
        passd.clear()

        uname.send_keys("system")
        passd.send_keys("system123")
        submit = self.driver.find_elements_by_xpath("//*[contains(text(), 'Proceed')]")
        submit[0].click()
        print(self.driver.current_url)
        assert( "http://127.0.0.1:8000/actionbot/index/" == self.driver.current_url)
        
    def tearDown(self):
        self.driver.quit()



class ExtractorSettings(TestCase,Login):

    def setUp(self):
        self.driver = Login.setUp(Login)


    def test01_add_extractor_settings(self):
        Login().login_succes()
        wait = WebDriverWait(self.driver,15)
        extractor_settings_a_tag = wait.until(EC.presence_of_element_located((By.XPATH,'//a[text()="Client-Extractor Settings"]')))
        if extractor_settings_a_tag.is_displayed():
           extractor_settings_a_tag.click()
        else:
            administration_btn = wait.until(EC.presence_of_element_located((By.XPATH,
                "//*[contains(text(), 'Administration')]")))
            administration_btn.click()
            extractor_settings_a_tag.click()
            time.sleep(2)
        extractor_settings_table = wait.until(EC.presence_of_all_elements_located((By.XPATH,
            '/html/body/section/aside/div/ul/li[2]/ul/li[2]/a')))
        extractor_settings_table_len = len(extractor_settings_table)
        select_client = self.driver.find_element_by_xpath('//*[@id="client"]').click()
        select_client = wait.until(EC.presence_of_element_located((By.XPATH,
                "//*[contains(text(), 'Kellogs')]")))
        select_client.click()
        time.sleep(1)
        select_erp = self.driver.find_element_by_xpath('//*[@id="erp"]').click()
        select_erp = wait.until(EC.presence_of_element_located((By.XPATH,
                "//*[contains(text(), 'SAP')]")))
        select_erp .click()
        select_dest_tool = self.driver.find_element_by_xpath('//*[@id="toolid"]').click()
        select_dest_tool = wait.until(EC.presence_of_element_located((By.XPATH,
                "//*[contains(text(), 'Cadency')]")))
        select_dest_tool .click()
        extractor_type = self.driver.find_element_by_xpath('//*[@id="extract"]').click()
        extractor_type = wait.until(EC.presence_of_element_located((By.XPATH,
                "//*[contains(text(), 'GL Transactions')]")))
        extractor_type .click()
        time.sleep(1)
        file_upload = self.driver.find_element_by_xpath('/html/body/section/section/section/div[1]/section/div/div/div[5]/form/div[1]/div/input')
        file_loc = os.getcwd()+ "\\GLTRAN_NYC_GLT3APR01_20190403181057.txt"
        file_upload.send_keys(file_loc)
        time.sleep(1)
        load_btn = self.driver.find_element_by_xpath('//*[@id="btnLoad"]')
        load_btn.click()
        time.sleep(1)
        select_ruleset = self.driver.find_element_by_xpath('//*[@id="cboRuleset"]').click()
        select_ruleset = wait.until(EC.presence_of_element_located((By.XPATH,
                "//*[contains(text(), 'GLTRANS')]")))
        select_ruleset .click()
        time.sleep(1)  
        data_format = self.driver.find_element_by_xpath('//*[@id="optionsRadios1"]')
        data_format .click()
        time.sleep(1)  
        self.driver.execute_script("window.scrollTo(0, window.scrollY + 200)")
        colo_deli_n_file = self.driver.find_element_by_xpath('//*[@id="cboColDelimiter"]').click()
        colo_deli_n_file = wait.until(EC.presence_of_element_located((By.XPATH,
                "//*[contains(text(), 'Pipe')]")))
        colo_deli_n_file .click()
        time.sleep(1)
        name_format = self.driver.find_element_by_xpath('//*[@id="FNameFormat"]')
        name_format.send_keys("text1")
        time.sleep(1)
        submit_btn = self.driver.find_elements_by_xpath(
            "//*[contains(text(), 'Save')]")
        submit_btn[0].click()
        time.sleep(10)
        print("Saved Extractor Settings")


    def tearDown(self):
        self.driver.quit()