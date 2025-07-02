import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from typing import Iterable
import os
import pathlib
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil

sys.path.append('.')
from src.file_finder.finder import DirectoryWatcher
from src.logger import logger
from src.downloader.schemas import DownloadResult, DownloadScheme


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

#Python3
class Downloader(metaclass=Singleton):
    def __init__(self):
        pass

    def init_by_download_scheme(self, download_scheme:DownloadScheme):
        self.download_scheme = download_scheme
        self.__init_driver()
        

    def __init_driver(self):
        self.download_dir = pathlib.Path(self.download_scheme.download_path).joinpath('./tmp')

        # Создаем объект Options для Firefox
        options = webdriver.FirefoxOptions()

        # Настройки профиля через set_preference
        options.set_preference("browser.download.folderList", 2)  # 2 - custom location
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", str(self.download_dir))
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream,application/pdf")
        options.set_preference("pdfjs.disabled", True)  # Отключить просмотр PDF
        options.add_argument("--headless")
        # Запуск драйвера с опциями
        self.driver = webdriver.Firefox(options=options)

        try:
            shutil.rmtree(self.download_dir)
            print(f"Директория {self.download_dir} успешно удалена")
        except OSError as e:
            print(f"Ошибка при удалении {self.download_dir}: {e.strerror}")

        os.makedirs(self.download_dir, exist_ok=True)

        self.directory_watcher = DirectoryWatcher(self.download_dir)
        files = self.directory_watcher.get_new_files()
        print(files, self.download_dir)

    
    #TODO Крайне сомнительно реализованный метод и все его задействованные методы
    def do_full_logic(self, download_scheme=None) -> DownloadResult:
        try:
            files = self.directory_watcher.get_new_files()
            print(files)
            if(download_scheme!=None):
                self.__init_by_download_scheme(download_scheme)
            # получаем страничку
            self.driver.get('https://rosstat.gov.ru/dbscripts/munst/')
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            logger.info('start step 2')
            self.do_step_2()     
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            logger.info('start step 3')
            self.do_step_3()
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            logger.info('start step 4')
            self.do_step_4()
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            logger.info('start step 5')
            time.sleep(8)
            self.do_step_5()


            time.sleep(2)
            new_files = self.directory_watcher.get_new_files()
            if(len(new_files)!=1):
                print(new_files)
                logger.error("Что-то пошло не так с количеством файлов")
            old_path = ""
            new_path = ""
            if(len(new_files)==1):
                old_path = pathlib.Path(self.download_dir).joinpath('./'+new_files[0])
                name = self.download_scheme.city+'_'+self.download_scheme.theme+'_'+self.download_scheme.year+pathlib.Path(old_path).suffix
                name = name.replace(' ', '_')
                new_path = pathlib.Path(self.download_scheme.download_path).joinpath('./'+name)
                #[название региона]_[блок отчета]_[название отчета]_[год].
            os.rename(old_path, new_path)
            self.directory_watcher.clear_known_files()
            return DownloadResult(success=True, path=str(new_path))
        except Exception as ex:
            print(str(ex))
            self.directory_watcher.clear_known_files()
            raise ex
            # return DownloadResult(success=False, path=None)

    def do_step_2(self):
        # получаем страничку области/региона и т.д., игнорируем ssl предупреждение... Костыль
        cities = self.get_all_cities()
        target_city = [el for el in filter(lambda x: self.download_scheme.city in x[1], cities)][0]
        while True:
            self.driver.get(target_city[0])
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            if not ('ssl' in self.driver.current_url):
                break
    
    def do_step_3(self):
        self.make_all_children_elements_visible()
        checkboxes = self.get_all_clickable_checkboxes_stage_1()
        result_checkbox = None
        for checkbox in checkboxes:
            text = checkbox.find_element(By.XPATH, "../../..").find_elements(By.TAG_NAME, 'td')[-1].get_attribute('innerText')
            if(self.download_scheme.theme in text):
                result_checkbox = checkbox
        if(not result_checkbox):
            raise Exception(f"there is no target theme {self.download_scheme.theme}")
        result_checkbox.click()

        element = self.driver.find_element(By.ID, 'Knopka')
        element.click()
    
    def do_step_4(self):
        driver = self.driver
        year = self.download_scheme.year

        checkboxes = driver.find_elements(By.TAG_NAME, 'input')
        god_checkbox = None
        for checkbox in checkboxes:
            if(checkbox.get_attribute('type')!='checkbox'):
                continue
            
            if( checkbox.get_attribute('name')!='god_chk' and 
            checkbox.get_attribute('checked')==None):
                driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                checkbox.click()
            # Снимем выделение со всех годов путём перевыделения 
            if(checkbox.get_attribute('name')=='god_chk'):
                driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                checkbox.click()
                driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                checkbox.click()

        god_select = driver.find_element(By.NAME, 'god')
        god_options = god_select.find_elements(By.TAG_NAME, 'option')
    



        for god_option in god_options:
            if(str(god_option.get_attribute('innerText'))==year):
                driver.execute_script("arguments[0].scrollIntoView(true);", god_option)
                # driver.execute_script("arguments[0].setAttribute('selected', '1')", god_option)
                god_option.click()
            # else:
                # driver.execute_script("arguments[0].setAttribute('selected', '0')", god_option)
        
        #Открываем таблицу и открываем вкладку
        old_url = driver.current_url
        inputs = driver.find_elements(By.TAG_NAME, 'input')
        btn = [elem for elem in filter(lambda x: x.get_attribute('value')=='Показать таблицу', inputs)][0]
        btn.click()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        if(old_url==driver.current_url):
            # У нас открыто новое окно. Старое уже не нужно, поэтому переходим на новое. 
            original_window = driver.current_window_handle
            for window_handle in driver.window_handles:
                if window_handle != original_window:
                    driver.switch_to.window(window_handle)
                    break

    def do_step_5(self):
        driver= self.driver

        format_element = driver.find_element(By.NAME,'Format')
        year_from_element = driver.find_element(By.NAME,'YearFrom')
        year_to_element = driver.find_element(By.NAME,'YearTo')
        def choose_option(driver, container_element, option):
            options = container_element.find_elements(By.TAG_NAME, 'option')
            option = [elem for elem in filter(lambda x: option in x.get_attribute('innerText'), options)][0]
            driver.execute_script("arguments[0].scrollIntoView(true);", option)
            option.click()
        choose_option(driver, format_element, self.download_scheme.document_type)
        choose_option(driver, year_from_element, self.download_scheme.year_from)
        choose_option(driver, year_to_element, self.download_scheme.year_to)
        btn = driver.find_element(By.NAME, 'showtbl')
        btn.click()


        
    def get_all_cities(self):
        '''
        Получаем все элементы <a> на странице с заданным регулярным выражением pattern
        driver должен находиться на необходимой странице сразу
        '''
        links = self.driver.find_elements(By.TAG_NAME,"a")
        
        # Регулярное выражение для нужного URL-паттерна
        pattern = r"http://rosstat\.gov\.ru/dbscripts/munst/munst.*/DBInet\.cgi"
        matching_urls = []

        for link in links:
            href = link.get_attribute("href")
            text = link.get_attribute('innerText')
            if href and re.match(pattern, href):
                matching_urls.append((href, text))
        return matching_urls

    def make_all_children_elements_visible(self, parent_element=None):
        # Скрипт для изменения стиля элемента
        script = """
        if (arguments[0].style.display === 'none') {
            arguments[0].style.display = 'block';  // Можно использовать 'inline', 'inline-block' и т.д.
        }
        """

        # Находим все элементы на странице
        if(parent_element==None):
            parent_element = self.driver
        elements = parent_element.find_elements("xpath", "//*")

        for element in elements:
            style = element.get_attribute("style")
            if style and 'display: none' in style.lower():
                self.driver.execute_script(script, element)

    def get_all_clickable_checkboxes_stage_1(self):
        '''Ищет все checkboxts на первом этапе'''
        tree = self.driver.find_element(By.ID, 'g0').parent
        imgs = tree.find_elements(By.TAG_NAME, "img")

        result_imgs = []
        for img in imgs:
            # TODO убрать хардкод. 
            if(img.get_attribute('src')=='https://rosstat.gov.ru/dbimages/toS.jpg'):
                result_imgs.append(img)
        return result_imgs


if __name__=="__main__":
    ds = DownloadScheme(download_path=str(pathlib.Path(os.getcwd()).joinpath('./download_path')), 
                        city="Республика Татарстан",
                        theme="Численность всего населения по полу и возрасту на 1 января текущего года",
                        year="2024",
                        year_from="2024",
                        year_to="2024",
                        document_type="CSV")
    downloader = Downloader()
    downloader = Downloader()
    downloader = Downloader()
    downloader.init_by_download_scheme(ds)
    downloader.do_full_logic()