# ver 1.1
#2019/08/25 19:40

# Chrome version : Chrome	73.0.3683.86 (공식 빌드) (64비트) (cohort: Stable)
# Chrome WebDriver는 Chrome version 이 변경되면 아래 url 에서 변경 필요함.
# Chrome WebDriver : https://sites.google.com/a/chromium.org/chromedriver/downloads
# Chrome version 확인 방법 : chrome 에서 chrome://version/ 로 연결

from time import sleep
import shutil
import os
import sys
from datetime import datetime
from selenium.webdriver import Chrome
from selenium.webdriver.chrome import webdriver as chrome_webdriver
from selenium.webdriver.support.ui import Select

from sendMail import *

now = datetime.now()
dt = datetime.today().strftime("%Y%m%d_%H%M")

tmpdir = os.path.join(os.getcwd(), "tmp")

#다운 로드 받은 최근 파일일 이름을 변경
def change_download_file_name(str, extension="xls"):
    filepath = tmpdir
    filename = max([filepath +"/"+ f for f in os.listdir(filepath)], key=os.path.getctime)

    if not os.path.exists(os.path.join(os.getcwd(), "data", dt)):
        os.makedirs(os.path.join(os.getcwd(), "data", dt))

    print(filename)
    shutil.move(filename, os.path.join(os.getcwd(), "data", dt, str + "."+extension))
    print(os.path.join(os.getcwd(), "data", dt,  str + "."+extension))
    print("=========")

    ##upCapa 프로그램 참조로 복사
    if str == "spec":
        ueCapaPath = 'C:\\Users\\SKTelecom\\PycharmProjects\\ueCapa\\program'
        if os.path.exists(ueCapaPath) :
            print("Spec 복사 ", ueCapaPath)
            shutil.copy(os.path.join(os.getcwd(), "data", dt,  str + "."+extension), ueCapaPath)

def downloads_done():
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)

    for i in os.listdir(tmpdir):
        if ".crdownload" in i:
            sleep(0.5)
            downloads_done()


class DriverBuilder():
    def get_driver(self, download_location=None, headless=False):

        driver = self._get_chrome_driver(download_location, headless)
        driver.implicitly_wait(5) ## 암묵적으로 웹 자원을 (최대) 3초 기다리기

        # driver.set_window_size(1400, 700)

        return driver

    def _get_chrome_driver(self, download_location, headless):
        chrome_options = chrome_webdriver.Options()
        if download_location:
            # prefs = {'download.default_directory': download_location,
            #          'download.prompt_for_download': False,
            #          'download.directory_upgrade': True,
            #          'safebrowsing.enabled': False,
            #          'safebrowsing.disable_download_protection': True}

            prefs =  { 'download.default_directory': download_location,
                        'download.prompt_for_download': False,
                        'download.directory_upgrade': True,
            }

            chrome_options.add_experimental_option('prefs', prefs)


        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('log-level=0')

        # chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        # chrome_options.add_argument('window-size=1920x1080')
        chrome_options.add_argument("disable-gpu")
        # chrome_options.add_argument("lang=ko_KR") # 한국어!

        # dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = 'c:/'
        driver_path = os.path.join(dir_path, "drivers/chromedriver")

        if sys.platform.startswith("win"):
            driver_path += ".exe"

        driver = Chrome(executable_path=driver_path, options=chrome_options)

        if headless:
            self.enable_download_in_headless_chrome(driver, download_location)

        return driver

    def enable_download_in_headless_chrome(self, driver, download_dir):
        """
        there is currently a "feature" in chrome where
        headless does not allow file download: https://bugs.chromium.org/p/chromium/issues/detail?id=696481
        This method is a hacky work-around until the official chromedriver support for this.
        Requires chrome version 62.0.3196.0 or above.
        """

        # add missing support for chrome "send_command"  to selenium webdriver
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
        command_result = driver.execute("send_command", params)
        print("response from browser:")
        for key in command_result:
            print("result:" + key + ":" + str(command_result[key]))



from connection_info import get_connection_info

#ID/PW
plm_id = get_connection_info("plm_id")
plm_pw = get_connection_info("plm_pw")


headless_raw = True
# headless_raw = False   #for test

host = get_connection_info("plm_host")
# host = host = get_connection_info("plm_host_test_server") #개발 서버

headless = True
if(headless_raw == "FALSE" or headless_raw == False):
    headless = False
print("headless = " + str(headless))

def login_plm():
    ## Login
    db = DriverBuilder()
    driver = db.get_driver(tmpdir, headless)
    driver.get(host)
    driver.find_element_by_name('userID').send_keys(plm_id) ## 값 입력
    driver.find_element_by_name('password').send_keys(plm_pw)
    driver.find_element_by_xpath('//*[@id="sub"]/div/div[3]/form/div/div[1]/button').click()
    return driver


try :
    driver = login_plm()
except Exception as ex:
    print(ex)
    print("Please Check chromedriver version..")
    # sendSMS("PLM Selenium, Please Check chromedriver version.. ")
    sendMail(title="PLM Crawling Error occurred, login_plm", text="PLM Selenium, Please Check chromedriver version.. ")
    exit(-1)

try :
    # 로그인 여부 확인
    driver.find_element_by_xpath('//*[@id="wrapper"]/article/header/div/article/ul/li[1]/span/a') #단말시험
except Exception as ex:
    print(ex)
    # sendSMS(ex.msg)
    sendMail(title="PLM Crawling Error occurred, login_plm ", text=ex.__str__())
    exit(-1)


# IOT
driver.find_element_by_xpath('//*[@id="wrapper"]/article/header/div/article/ul/li[1]/span/a').click() #단말시험
try :
    driver.find_element_by_xpath('//*[@id="mask"]').click() # 공지시 예외처리
except Exception as ex:
    pass
driver.find_element_by_xpath('//*[@id="leftMenuDiv"]/h1').click()
# 엑셀 받기
driver.switch_to.frame(driver.find_element_by_id("m_content")) #내부 frame 로 변경
driver.find_element_by_xpath('//*[@id="test_list"]/ul/li[1]/select').click()

select = Select(driver.find_element_by_xpath('//*[@id="test_list"]/ul/li[1]/select')) #전체 보기
# select by visible text
select.select_by_visible_text('전체보기')
# # select by value
# select.select_by_value('1')

sleep(1)
driver.find_element_by_xpath('//*[@id="test_list"]/ul/li[5]/a').click()
# driver.save_screenshot("IOT.png")

# 이름 변경
while(1):
    sleep(1)
    downloads_done()
    try:
        change_download_file_name("iot")
    except Exception as ex:
        print("waiting..")
        continue
    break

# OSU
driver.switch_to.default_content()
# driver.find_element_by_xpath('//*[@id="wrapper"]/article/header/div/article/ul/li[1]/span/a').click() #단말시험
driver.find_element_by_xpath('//*[@id="mdt_os_list"]').click()
# 엑셀 받기
driver.switch_to.frame(driver.find_element_by_id("m_content")) #내부 frame 로 변경
# driver.save_screenshot("OSU1.png")
driver.find_element_by_xpath('//*[@id="os_test_list"]/ul/li[5]/a').click()


# # 신규 Tab을 통해 파일 다운로드
#190327 tab 없이 열리도록 개선
# # 응답시간이 너무 짧기 때문에 동작에 문제 있음.
# if headless:
#     instances = driver.window_handles
#     driver.switch_to.window(instances[1]) # this is the new browser
#     enable_download_in_headless_chrome(driver, tmpdir)
#     driver.switch_to.window(instances[0])


# 이름 변경
while(1):
    sleep(1)
    downloads_done()
    try:
        change_download_file_name("osu")
    except Exception as ex:
        print("waiting..")
        continue
    break

#
# MR
driver.switch_to.default_content()
# driver.find_element_by_xpath('//*[@id="wrapper"]/article/header/div/article/ul/li[1]/span/a').click() #단말시험
driver.find_element_by_xpath('//*[@id="leftMenuDiv"]/ul/li[3]/ul[1]/li').click()

# 엑셀 받기
driver.switch_to.frame(driver.find_element_by_id("m_content")) #내부 frame 로 변경
driver.find_element_by_xpath('//*[@id="rc_test_list"]/ul/li[5]/a').click()


# 이름 변경
while(1):
    sleep(1)
    downloads_done()
    try:
        change_download_file_name("mr")
    except Exception as ex:
        print("waiting..")
        continue
    break


#Spec
driver.switch_to.default_content()
driver.find_element_by_xpath('//*[@id="wrap"]/header/hgroup/ul/li[5]/span/a').click()
driver.find_element_by_xpath('//*[@id="statistic_spec"]').click()

# 엑셀 받기
driver.switch_to.frame(driver.find_element_by_id("m_content")) #내부 frame 로 변경
driver.find_element_by_xpath('//*[@id="spec_list"]/ul/li[5]/a[2]').click()
# 이름 변경
while(1):
    sleep(1)
    downloads_done()
    try:
        change_download_file_name("spec", "xlsx")
    except Exception as ex:
        print(ex)
        continue
    break

driver.quit()

print("Complete!!")


from make_db_data import StartMakeDb
StartMakeDb()

from ftpupload import start_upload
file_list = start_upload()
