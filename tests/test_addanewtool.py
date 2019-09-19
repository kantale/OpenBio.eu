# Generated by Selenium IDE
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

class TestAddanewtool():
  def setup_method(self, method):
    binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')

    self.driver = webdriver.Firefox(executable_path= r'E:\openbioc\OpenBioC\tests\geckodriver.exe', firefox_binary=binary)
    self.driver.maximize_window() #For maximizing window
    self.driver.implicitly_wait(5) #gives an implicit wait for 5 seconds
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_addanewtool(self):
    # Test name: add a new tool
    # Step # | name | target | value | comment
	
    ####	SIGN IN		####
    # 1 | open | http://localhost:8200/platform/ |  | 
    self.driver.get("http://localhost:8200/platform/")
    # 2 | setWindowSize | 1554x938 |  | 
    self.driver.set_window_size(1554, 938)
    # 3 | click | id=signInBtn |  | 
    self.driver.find_element(By.ID, "signInBtn").click()
    # 4 | click | css=.ng-pristine > .col > .input-field:nth-child(1) > label |  | 
    self.driver.find_element(By.CSS_SELECTOR, ".ng-pristine > .col > .input-field:nth-child(1) > label").click()
    # 5 | type | id=signInUsername | gala | 
    self.driver.find_element(By.ID, "signInUsername").send_keys("gala")
    # 6 | click | css=.ng-dirty > .row > .input-field:nth-child(2) > label |  | 
    self.driver.find_element(By.CSS_SELECTOR, ".ng-dirty > .row > .input-field:nth-child(2) > label").click()
    # 7 | mouseOver | name=action |  | 
    element = self.driver.find_element(By.NAME, "action")
    actions = ActionChains(self.driver)
    actions.move_to_element(element).perform()
    # 8 | type | id=signInPassword | galagala | 
    self.driver.find_element(By.ID, "signInPassword").send_keys("galagala")
    # 9 | click | name=action |  | 
    self.driver.find_element(By.NAME, "action").click()
    # 10 | mouseOut | name=action |  | 
    element = self.driver.find_element(By.CSS_SELECTOR, "body")
    actions = ActionChains(self.driver)
    actions.move_to_element(element).perform()
	
	
	
    ####	ADD GENERAL INFORMATION FOR TOOL	#### 
    time.sleep(5)
    # 11 | click | css=#toolsDataPlusBtn > .material-icons |  | 
    self.driver.find_element(By.CSS_SELECTOR, "#toolsDataPlusBtn > .material-icons").click()
    # 12 | click | css=.row:nth-child(1) > .m4:nth-child(1) > label |  | 
    self.driver.find_element(By.CSS_SELECTOR, ".row:nth-child(1) > .m4:nth-child(1) > label").click()
    # 13 | type | id=generalName | plink | 
    self.driver.find_element(By.ID, "generalName").send_keys("plinkTest")
    # 14 | click | css=.row:nth-child(1) > .m4:nth-child(2) > label |  | 
    self.driver.find_element(By.CSS_SELECTOR, ".row:nth-child(1) > .m4:nth-child(2) > label").click()
    # 15 | type | id=generalVersion | 1 | 
    self.driver.find_element(By.ID, "generalVersion").send_keys("1")
    # 16 | mouseDown | id=generalDescription |  | 
    element = self.driver.find_element(By.ID, "generalDescription")
    actions = ActionChains(self.driver)
    actions.move_to_element(element).click_and_hold().perform()
    time.sleep(10)
    # 17 | mouseUp | css=.grid-s12-m12-l12 > .active |  | 
    element = self.driver.find_element_by_xpath("//span[contains(text(),'Installation')]")    
	#element = self.driver.find_element(By.CSS_SELECTOR, ".grid-s12-m12-l12 > .active")
    actions = ActionChains(self.driver)
    actions.move_to_element(element).release().perform()
    # 18 | click | css=.ng-dirty .input-field:nth-child(4) |  | 
    self.driver.find_element(By.CSS_SELECTOR, ".ng-dirty .input-field:nth-child(4)").click()
    # 19 | type | id=generalDescription | this is a test | 
    self.driver.find_element(By.ID, "generalDescription").send_keys("this is a test")
    
    ####	ADD INSTALLATION INFORMATION FOR TOOL	#### 	
    # 20 | click | css=#toolsDataInstallation .arrow |  | 
    self.driver.find_element(By.CSS_SELECTOR, "#toolsDataInstallation .arrow").click()
    time.sleep(2)
	# 21 | click | css=.select-dropdown:nth-child(1) |  | 
    self.driver.find_element(By.CSS_SELECTOR, ".select-dropdown:nth-child(1)").click()
    time.sleep(2)
    # 22 | click | css=#select-options-7adcc257-80f9-70bd-fdaf-8c79240153572 > span span |  | 
    self.driver.find_element_by_xpath("//div[@class='select-wrapper']").click()
    #self.driver.find_element(By.CSS_SELECTOR, "#select-options-7adcc257-80f9-70bd-fdaf-8c79240153572 > span span").click()
    
	####	ADD INSTALLATION COMMANDS FOR TOOL	#### 
    # 29 | click | css=#toolsDataInstallation > .collapsible-body |  | 
    self.driver.find_element(By.CSS_SELECTOR, "#toolsDataInstallation > .collapsible-body").click()
    # 30 | click | css=#tool_installation_editor .ace_content |  | 
    self.driver.find_element(By.CSS_SELECTOR, "#tool_installation_editor .ace_content").click()
    # 31 | runScript | window.scrollTo(0,0) |  | 
    self.driver.execute_script("window.scrollTo(0,0)")
    # 32 | runScript | window.scrollTo(0,0) |  | 
    self.driver.execute_script("window.scrollTo(0,0)")
    # 33 | type | css=#tool_installation_editor > .ace_text-input | exit 0\n\n | 
    self.driver.find_element(By.CSS_SELECTOR, "#tool_installation_editor > .ace_text-input").send_keys("exit 0\\n\\n")
    
    ####	ADD VALIDATION COMMANDS FOR TOOL	#### 
	# 34 | click | css=#tool_validation_editor .ace_content |  | 
    self.driver.find_element(By.CSS_SELECTOR, "#tool_validation_editor .ace_content").click()
    # 35 | runScript | window.scrollTo(0,0) |  | 
    self.driver.execute_script("window.scrollTo(0,0)")
    # 36 | runScript | window.scrollTo(0,0) |  | 
    self.driver.execute_script("window.scrollTo(0,0)")
    # 37 | type | css=#tool_validation_editor > .ace_text-input | exit 0\n\n | 
    self.driver.find_element(By.CSS_SELECTOR, "#tool_validation_editor > .ace_text-input").send_keys("exit 0\\n\\n")
    # 38 | click | linkText=save |  | 
    self.driver.find_element(By.LINK_TEXT, "save").click()
  
