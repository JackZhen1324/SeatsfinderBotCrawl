# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from argparse import ArgumentParser
from urllib2 import Request, urlopen
from urllib2 import URLError, HTTPError
from selenium.webdriver.chrome.options import Options
import logging
import pickle
import time
import logging
import datetime
import threading
import sys
import unicodedata
import pyrebase
import os
import traceback
from apns2.client import APNsClient
from apns2.payload import Payload

count = 1
isDuo = 0
class SeatsfinderbotsSpider(scrapy.Spider):

    name = 'seatsfinderbots'
    allowed_domains = ['asu.edu']
    config = {
    'apiKey': "AIzaSyBPE9nfY4BG4P6Q5lxVkVSVElgQrRLKgV0",
    'authDomain': "seatsfinderbot.firebaseapp.com",
    'databaseURL': "https://seatsfinderbot.firebaseio.com",
    'projectId': "seatsfinderbot",
    'storageBucket': "seatsfinderbot.appspot.com",
    'messagingSenderId': "427671677247"
        };
    firebase = pyrebase.initialize_app(config)
    auth2 = firebase.auth()
    database = firebase.database()

    statusURL = "http://72.201.206.220:8001/api/WebAPI?GetSuperPowerVMTaskSchedulerStatus=true&guid="
    checkURL = "http://72.201.206.220:8001/api/WebAPI?checkStatusByBot=true&prefix=&number=&location=Tempe&term="
    superPowerStatusURL = "http://72.201.206.220:8001/api/WebAPI?registerStatusNotify=true&status="

    myEmail = "mopjtv@gmail.com"
    start_urls = ['']
    deviceId = ""
    def update_databse(self,message):
        try:
            status = message
            data = {"logs": status, "coueseId": self.section, "jobId": os.environ['SCRAPY_JOB'], "mode": self.choice,
                    "user": self.username, "count": count, "instructor": self.instructor, "courseID": self.courseID,
                    "deviceID": self.deviceID, "password": self.password, "semester": self.semester}
            userID  = str(self.username)
            userID.replace("\"","")
            self.database.child("users").child(self.username).child("courses").child(self.section).set(data)
        except:
            logging.info("fail to contact with firebase!!")
    def send_Notification(self,message, key, device_id):

        token_hex = device_id
        payload = Payload(alert=message, sound="default", badge=1)
        topic = 'ASU.SeatsFinderBot'
        client = APNsClient(key, use_sandbox=False, use_alternative_port=False)
        client.send_notification(token_hex, payload, topic)

    def start_requests(self):
        global isDuo
        if self.twoSteps == "disable":
            isDuo = 0
        else:
            isDuo = 1
        global count
        count = count + 1
        logging.info('start')
        self.update_databse("")

        self.start_urls = [str(self.checkURL) + str(self.semester) + "&sectionNumber=" + str(self.section) + "&reservedSeats=" + str(self.reserved)]
        request = scrapy.Request(url=self.start_urls[0], callback=self.parse)
        
        yield request
    def parse(self, response):
        global isDuo
        global count

        count = count + 1
        currTime = self.get_local_time()
        currTimeInSec = self.get_local_time_inSec()
        #logging.info("start parsing: "+currTime)
        currenturl = str(self.checkURL) + str(self.semester) + "&sectionNumber=" + str(self.section) + "&reservedSeats=" + str(self.reserved)

        #data = {"logs": status,"coueseId":self.section,"jobId":os.environ['SCRAPY_JOB'],"mode":self.choice,"user":self.username}
        #self.database.child("users").child(self.username).child("courses").child(self.section).set(data)
        print (currenturl)
        contents =  response.body
        #logging.info(contents)
        print ("******")
        print (contents)
        print ("******")

        

        if "FULL" in str(contents):
            status ="Checked on " + currTimeInSec + ", the class is FULL"
            #logging.info("Checked on " + currTimeInSec + ", the class is FULL")
            print("Checked on " + currTimeInSec + ", the class is FULL ")
            self.update_databse(status)
            time.sleep(float(self.timeInterval))
            if str(self.choice) == "swap":

                request = scrapy.Request(url=self.start_urls[0], callback=self.parse,dont_filter = True)
                yield request

            if str(self.choice) == "add":

                request = scrapy.Request(self.start_urls[0], callback=self.parse,dont_filter = True)

                yield request

    
        elif "OPEN" in str(contents):
            status ="Checked on " + currTimeInSec + ", the class is OPEN"
            self.update_databse(status)
            global deviceId
            try:
                deviceId = self.deviceID
            except:
                deviceId = "e4d3e8cb6e8c29d0dd6af4926e698c69632e2a8965cd17d66ed2d0cdd7869269"

            try:
                self.send_Notification("Course "+self.section+" is available now, please check out.","apns-push_sf-cert.pem",deviceId)
                logging.info("send notification success")
                print("send notification success")
            except:
                traceback.print_exc()
                print("fail to send notification")
                logging.info("fail to send notification")
            #self.database.child("users").child(self.username).child("courses").child(self.section).set(data)
            time.sleep(float(self.timeInterval))
            if self.choice == "swap":
                self.urlErrorCheck(self.statusURL + 'ZhenAdmin' + "&taskID=" + str(self.section) + "&time=" + currTime + "&status=OPEN")
            if self.choice == "add":
                self.urlErrorCheck(self.statusURL + 'ZhenAdmin' + "&taskID=" + str(self.section) +
                              "&time=" + currTime + "&status=OPEN")
            if self.choice == "add":
                print(self.level,self.username,self.password,self.section,self.semester)
                statusAdd = self.addClass(self.level,self.username,self.password,self.section,self.semester,currTimeInSec)

                self.urlErrorCheck(
                    self.superPowerStatusURL + statusAdd + "&email=" + self.myEmail + "&guid=" + 'ZhenAdmin' + "&section=" + self.section)
                if statusAdd == 'SuccessEnrolled':
                    print('success')
                else:
                    request = scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)

                    #yield request
            if self.choice == "swap":
                statusSwap = self.swapClass(self.level,self.username,self.password,self.section,self.swapWith,self.semester,currTimeInSec)

                self.urlErrorCheck(
                    self.superPowerStatusURL + statusSwap + "&email=" + self.myEmail + "&guid=" + 'ZhenAdmin' + "&section=" + self.section)
                if statusSwap == 'SuccessEnrolled':
                    print('success')
                else:
                    request = scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)

                    #yield request
            #logging.info("Checked on " + currTimeInSec + ", the class is OPEN")



        elif "NOT FOUND" in str(contents):
            status = "Checked on " + currTimeInSec + ", the class is NOT FOUND"
            self.update_databse(status)
            time.sleep(float(self.timeInterval))
            print(
                        "Checked on " + currTimeInSec + ", the class is NOT FOUND")
            request = scrapy.Request(url=self.start_urls[0], callback=self.parse,dont_filter = True)
            yield request
        elif "ERRORURL" in str(contents):
            status = "HTTP ERROR on " + currTimeInSec + " "
            self.update_databse(status)
            time.sleep(float(self.timeInterval))
            print("HTTP ERROR on " + currTimeInSec + " ")
            request = scrapy.Request(url=self.start_urls[0], callback=self.parse,dont_filter = True)
            yield request
        else:
            status = "OTHER ERROR on " + currTimeInSec + " "
            self.update_databse(status)
            time.sleep(float(self.timeInterval))
            print("OTHER ERROR on " + currTimeInSec + " ")
            request = scrapy.Request(url=self.start_urls[0], callback=self.parse,dont_filter = True)
            yield request


    def get_local_time(self):

        current_time = datetime.datetime.now().strftime("%H:%M")
        #logging.info("get_local_time(): %s", current_time)

        return str(current_time)

    def get_local_time_inSec(self):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        #logging.info("get_local_time(): %s", current_time)
        return str(current_time)

    def check_exists_by_id(self,id, driver):
        try:
            driver.find_element_by_id(id)
        except:
            return False
        return True

    def semesterIndex(self,semesterCombo):
        if semesterCombo == "Spring+2019":
            return "2191"
        if semesterCombo == "Spring+2020":
            return "2201"
        if semesterCombo == "Spring+2021":
            return "2211"
        if semesterCombo == "Spring+2022":
            return "2221"
        if semesterCombo == "Spring+2023":
            return "2231"
        if semesterCombo == "Spring+2024":
            return "2241"
        if semesterCombo == "Spring+2025":
            return "2251"
        if semesterCombo == "Fall+2019":
            return "2197"
        if semesterCombo == "Fall+2020":
            return "2207"
        if semesterCombo == "Fall+2021":
            return "2217"
        if semesterCombo == "Fall+2022":
            return "2227"
        if semesterCombo == "Fall+2023":
            return "2237"
        if semesterCombo == "Fall+2024":
            return "2247"
        if semesterCombo == "Fall+2025":
            return "2257"

    def addClass(self,level, username, password, sectionNum, semesterCombo,currTimeInSec):
        currTimeInSec = currTimeInSec
        status = "Found Seat on " + currTimeInSec + " Start adding..."
        self.update_databse(status)
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        options.add_argument('lang=zh_CN.UTF-8')
        options.add_argument('--no-sandbox')
        #options.add_argument('--headless')
        options.add_argument('user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"')
        driver=webdriver.Chrome(chrome_options = options)
        driver.set_window_size(2560, 8000)

        STRM = self.semesterIndex(semesterCombo)

        driver.get("https://go.oasis.asu.edu/addclass/?STRM=" +
                   str(STRM) + "&ACAD_CAREER=" + level)

        driver.switch_to_frame(driver.find_element_by_xpath(
            "//frame[@src='https://weblogin.asu.edu/cgi-bin/login?callapp=https%3A//go.oasis.asu.edu/waitframeset.html%3Fdelay%3D3500%26url%3Dhttps%253A//cs.oasis.asu.edu/asucsprd/golink/%253F/EMPLOYEE/PSFT_ASUCSPRD/s/WEBLIB_ASU_SA.ASU_SA_ISCRIPT.FieldFormula.IScript_SA%253FURL%253D/EMPLOYEE/PSFT_ASUCSPRD/c/SA_LEARNER_SERVICES.SSR_SSENRL_CART.GBL%25253FSTRM%25253D" + str(
                STRM) + "%252526ACAD_CAREER%25253D" + level + "%252526Page%25253DSSR_SSENRL_ADD%252526Action%25253DA%252526INSTITUTION%25253DASU00%252526golink%25253DY']"))
        driver.find_element_by_id("username").send_keys(username)
        driver.find_element_by_id("password").send_keys(password)
        driver.find_element_by_class_name("submit").send_keys(Keys.RETURN)
        if isDuo == 0:
            time.sleep(0)
        else:
            time.sleep(25)
        driver.switch_to_frame(0)
        driver.switch_to_frame(0)
        driver.switch_to_frame(2)

        time.sleep(1)

        # Empty Shopping Cards
        while self.check_exists_by_id("P_DELETE$0", driver):
            driver.find_element_by_id("P_DELETE$0").send_keys(Keys.RETURN)
            time.sleep(1)
        time.sleep(1)

        # Enter Section Number
        try:
            driver.find_element_by_id(
                "DERIVED_REGFRM1_CLASS_NBR").send_keys(sectionNum)
            driver.find_element_by_id(
                "DERIVED_REGFRM1_SSR_PB_ADDTOLIST2$9$").send_keys(Keys.RETURN)

            # Add Class
            driver.implicitly_wait(10)
            driver.find_element_by_id(
                "DERIVED_CLS_DTL_NEXT_PB$280$").send_keys(Keys.RETURN)

            driver.implicitly_wait(10)
            driver.find_element_by_id(
                "DERIVED_REGFRM1_LINK_ADD_ENRL$82$").send_keys(Keys.RETURN)

            driver.implicitly_wait(10)
            driver.find_element_by_id(
                "DERIVED_REGFRM1_SSR_PB_SUBMIT").send_keys(Keys.RETURN)

            driver.implicitly_wait(10)
            status = driver.find_element_by_id("win0divSSR_SS_ERD_ER$0").text
        except:
            status = "tried add class on " + currTimeInSec + " Action Fail"
            self.update_databse(status)

        FinalStatus = ""

        if "Error" in status:
            status = "tried add class on " + currTimeInSec + " Action Fail"
            self.update_databse(status)
            driver.close()
            FinalStatus = "FailEnrolled"

        elif "Success" in status:
            status = "tried add class on " + currTimeInSec + " Action Success"
            self.update_databse(status)
            
            FinalStatus = "SuccessEnrolled"

        else:
            status = "tried add class on " + currTimeInSec + " UnknownStatus Error"
            self.update_databse(status)

            FinalStatus = "UnknownStatus"
        driver.close()
        return FinalStatus

    def swapClass(self,level, username, password, sectionNum, swapWith, semesterCombo,currTimeInSec):
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        options.add_argument('lang=zh_CN.UTF-8')
        options.add_argument('--no-sandbox')
        #options.add_argument('--headless')
        options.add_argument('user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"')
        driver=webdriver.Chrome(chrome_options = options)
        driver.set_window_size(2560, 8000)

        STRM = self.semesterIndex(semesterCombo)

        driver.get("https://go.oasis.asu.edu/swapclass/?STRM=" +
                   str(STRM) + "&ACAD_CAREER=" + level + "&ASU_CLASS_NBR=" + str(sectionNum))

        driver.switch_to_frame(driver.find_element_by_xpath(
            "//frame[@src='https://weblogin.asu.edu/cgi-bin/login?callapp=https%3A//go.oasis.asu.edu/waitframeset.html%3Fdelay%3D3500%26url%3Dhttps%253A//cs.oasis.asu.edu/asucsprd/golink/%253F/EMPLOYEE/PSFT_ASUCSPRD/s/WEBLIB_ASU_SA.ASU_SA_ISCRIPT.FieldFormula.IScript_SA%253FURL%253D/EMPLOYEE/PSFT_ASUCSPRD/c/SA_LEARNER_SERVICES.SSR_SSENRL_SWAP.GBL%25253FSTRM%25253D" + str(
                STRM) + "%252526ACAD_CAREER%25253D" + level + "%252526ASU_CLASS_NBR%25253D" + str(
                sectionNum) + "%252526Page%25253DSSR_SSENRL_SWAP%252526Action%25253DA%252526INSTITUTION%25253DASU00%252526golink%25253DY']"))

        driver.find_element_by_id("username").send_keys(username)
        driver.find_element_by_id("password").send_keys(password)
        driver.find_element_by_class_name("submit").send_keys(Keys.RETURN)

        driver.switch_to_frame(0)
        driver.switch_to_frame(0)
        driver.switch_to_frame(2)

        time.sleep(1)

        # Empty Shopping Cards
        while self.check_exists_by_id("P_DELETE$0", driver):
            driver.find_element_by_id("P_DELETE$0").send_keys(Keys.RETURN)
            time.sleep(1)
        try:
            # Select class from dropdownlist
            dropdownlist = driver.find_element_by_id("DERIVED_REGFRM1_DESCR50$225$")

            # create select element object
            selectElement = Select(dropdownlist)

            # select by value
            selectElement.select_by_value(str(swapWith))

            # Click Enter
            driver.implicitly_wait(10)
            driver.find_element_by_id(
                "DERIVED_REGFRM1_SSR_PB_ADDTOLIST2$106$").send_keys(Keys.RETURN)

            # Click Next
            driver.implicitly_wait(10)
            driver.find_element_by_id("DERIVED_CLS_DTL_NEXT_PB").send_keys(Keys.RETURN)

            # Click Finish Swaping
            driver.implicitly_wait(10)
            driver.find_element_by_id(
                "DERIVED_REGFRM1_SSR_PB_SUBMIT").send_keys(Keys.RETURN)

            driver.implicitly_wait(10)
            status = driver.find_element_by_id("win0divSSR_SS_ERD_ER$0").text
        except:
            status = "tried add class on " + currTimeInSec + " Action Fail"
            self.update_databse(status)

        FinalStatus = ""

        if "Error" in status:
            status = "tried add class on " + currTimeInSec + " Action Fail"
            self.update_databse(status)
            driver.close()
            FinalStatus = "FailEnrolled"
        elif "Success" in status:
            status = "tried add class on " + currTimeInSec + " Action Success"
            self.update_databse(status)
            FinalStatus = "SuccessEnrolled"
        else:
            status = "tried add class on " + currTimeInSec + " UnknownError"
            self.update_databse(status)
            driver.close()
            FinalStatus = "UnknownStatus"

        return FinalStatus

    def urlErrorCheck(self,url):
        url = url.replace(' ','')
        req = Request(url)
        print('test1%&%&%^&%&^%&^%&')
        print(url)
        print('test1%&%&%^&%&^%&^%&')

        try:
            response = urlopen(req).read()
        except HTTPError as e:
            print('Error code: ', e.code)
            return "ERRORURL"
        except URLError as e:
            print('Reason: ', e.reason)
            return "ERRORURL"
        else:
            return response

    def runAction(level, semester, reserved, section, GUID, choice, username, password, swapWith, timeInterval):
        try:
            currTime = get_local_time()
            currTimeInSec = get_local_time_inSec()
            contents = urlErrorCheck(checkURL + str(semester) + "&sectionNumber=" +
                                     str(section) + "&reservedSeats=" + str(reserved))
            if "FULL" in str(contents):
                if choice == "swap":
                    urlErrorCheck(statusURL + GUID + "&taskID=" + str(section) +
                                  "&time=" + currTime + "&status=FULL")
                if choice == "add":
                    urlErrorCheck(statusURL + GUID + "&taskID=" + str(section) +
                                  "&time=" + currTime + "&status=FULL")
                print(
                            "Checked on " + currTimeInSec + ", the class is FULL, next check in " + timeInterval + " seconds.")
            elif "OPEN" in str(contents):
                if choice == "swap":
                    urlErrorCheck(statusURL + GUID + "&taskID=" + str(section) + "&time=" + currTime + "&status=OPEN")
                if choice == "add":
                    urlErrorCheck(statusURL + GUID + "&taskID=" + str(section) +
                                  "&time=" + currTime + "&status=OPEN")
                if choice == "add":
                    statusAdd = addClass(level, username, password, section, semester,currTimeInSec)
                    urlErrorCheck(
                        superPowerStatusURL + statusAdd + "&email=" + myEmail + "&guid=" + GUID + "&section=" + section)
                if choice == "swap":
                    statusSwap = swapClass(level, username, password, section, swapWith, semester,currTimeInSec)
                    urlErrorCheck(
                        superPowerStatusURL + statusSwap + "&email=" + myEmail + "&guid=" + GUID + "&section=" + section)
                print(
                            "Checked on " + currTimeInSec + ", the class is OPEN, next check in " + timeInterval + " seconds.")
            elif "NOT FOUND" in str(contents):
                print(
                            "Checked on " + currTimeInSec + ", the class is NOT FOUND, next check in " + timeInterval + " seconds.")
            elif "ERRORURL" in str(contents):
                print("HTTP ERROR on " + currTimeInSec + ", next check in " + timeInterval + " seconds.")
            else:
                print("OTHER ERROR on " + currTimeInSec + ", next check in " + timeInterval + " seconds.")
        except:
            print("runAction error on " + currTimeInSec + ", next check in " + timeInterval + " seconds.")


