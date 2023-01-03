#import requests library and beautifulSoup
import time
from selenium import webdriver
import itertools
from bs4 import BeautifulSoup
from datetime import datetime
import functools

def driver_page_source(url_link):
    print(url_link)
    # Web scrapper
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('chromedriver', options=chrome_options)

    #executable_path = r"E:\Chromedriver\chromedriver_win32_chrome83\chromedriver.exe"

    # the website URL
    driver.get(url_link)

    scroll_pause_time = 0.1  # You can set your own pause time. My laptop is a bit slow so I use 1 sec
    screen_height = driver.execute_script("return window.screen.height;")  # get the screen height of the web
    i = 1

    while True:
        # scroll one screen height each time
        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
        i += 1
        time.sleep(scroll_pause_time)
        # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
        scroll_height = driver.execute_script("return document.body.scrollHeight;")
        # Break the loop when the height we need to scroll to is larger than the total scroll height
        if (screen_height) * i > scroll_height:
            break
    return  driver.page_source

#scrapin_one_page
def scraping_one_page(page_n):
    url_link = f"https://www.autoscout24.fr/lst?fregfrom={int(datetime.today().strftime('%Y')) - 4}&sort=standard&desc=0&atype=C&ustate=N%2CU&powertype=kw&search_id=1eb3bnej86n&page={page_n}"
    # driver page source
    page_source = driver_page_source(url_link)

    # create an instance of BeautifulSoup class for parse and process the data
    doc = BeautifulSoup(page_source, "html.parser")

    # FIND ELEMENT BY article
    #res = list(filter(date_inferior_5, doc.find_all("article")))
    res = list(doc.find_all("article"))

    return  list(map(scraping_, res))


#this method returns true if the difference between today's date and car date is less than 5 years
def date_inferior_5(ele):
    try:
        details = ele.find_all("span", class_="VehicleDetailTable_item__koEV4")
        return (int(datetime.today().strftime("%Y")) - int(
            datetime.strptime(details[1].text, '%m/%Y').strftime("%Y"))) < 5
    except:
        return False

def scraping_title(ele):
    title= ele.find('h2').text
    title= title.strip()

    return title.lower()

def scraping_price(ele):
    try :
        price= ele.find("p", class_="Price_price__WZayw").text
    except :
        price= ele.find("span", class_="SuperDeal_highlightContainer__EPrZr").text

    ch = filter(lambda x: x.isnumeric(), price)
    ch = float(functools .reduce(lambda x, y: x+y, ch))

    return ch

def scraping_image_url(ele):

    image_url= ele.find("img", class_="NewGallery_img__bi92g")

    return image_url['src']

def scraping_Detail(ele):

        details = ele.find_all("span", class_="VehicleDetailTable_item__koEV4")
        #kilometrage
        kilometrage = details[0].text
        try :
            kilometrage= filter(lambda x: x.isnumeric(), kilometrage)
            kilometrage = float(functools.reduce(lambda x, y: x + y, kilometrage))
        except:
            kilometrage = 0

        #date
        try :
            date = details[1].text.split('/')[1]
        except :
            date = datetime.today().strftime("%Y")
        #carburant
        carburant = details[6].text

        return date, kilometrage, carburant.lower()

def scraping_href(ele):
    a= ele.find('a', class_="ListItem_title__znV2I Link_link__pjU1l")
    href= "https://www.autoscout24.fr/" + a['href']

    return href

def scraping_(ele) :
    item= dict()
    item['name'] = scraping_title(ele)
    item['url_image']= scraping_image_url(ele)
    item['price']= scraping_price(ele)
    item['date'], item['kilometrage'], item['carburant']= scraping_Detail(ele)
    item['href']= scraping_href(ele);
    item['site_name']= 'autoscout24';
    return item


def autoscout24():
    try :
        t_start = time.time()
        data=list()

        data=[ scraping_one_page( i) for i in range(1, 21 )]

        data= list(itertools.chain(*data))

        print("number of all items ",len(data))
        #print(data)
        t_final = time.time()
        print("time of scraping ", (t_final - t_start)//60, " seconds")

        from database import database_communication

        database_communication(data, 'autoscout24')
    except :
        autoscout24()
#threads = [threading.Thread(target=scraping_one_page, args=(data, i)) for i in range(1, 21)]
    #for thread in threads :
     #   thread.start()
