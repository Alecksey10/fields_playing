from src.meta.singleton import Singleton
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver

class Driver(metaclass=Singleton):
    def __init__(self):
        self.options = Options()
        # firefox_profile = FirefoxProfile()
        # firefox_profile.set_preference("javascript.enabled", False)
        # options.profile = firefox_profile
        self.driver = None
    
    def start(self):
        if(self.driver):
            try:
                self.driver.close()
            except:
                pass
        self.driver = webdriver.Firefox(options=self.options)
    
    def shutdown(self):
        self.driver.close()
    
