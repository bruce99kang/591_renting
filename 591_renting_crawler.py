from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import re

def main_page(area_list):
    df_area = []
    for area in area_list:
        options = Options()
        options.add_argument("--disable-notifications")
        browser = webdriver.Chrome(
            ChromeDriverManager().install(), chrome_options=options)
        browser.get(f"https://rent.591.com.tw/?kind=0&region={area_dict[area]}")
        time.sleep(5)

        soup = BeautifulSoup(browser.page_source, "html.parser")
        end_page = int(soup.find_all('a', {"class": "pageNum-form"})[-1].text)
        print(area, 2)
        df_page_list = []
        
        for page in range(0, 2):
            rent_elements = soup.find_all('div', {"class": "switch-list-content"})
            elements = soup.find_all("a", href=re.compile("^https://rent.591.com.tw/rent-detail-"))
        
            df_table = crawler(elements, area)

            print(area, " Page", page)
            page_next = browser.find_element_by_class_name("pageNext")
            page_next.click()
            df_page = pd.DataFrame(df_table)
            df_page_list.append(df_page)
            time.sleep(5)

        browser.close()
        print("===============================")
        print(area, "collected successfully.")
        print("===============================")
        
        df_city = pd.concat(df_page_list)
        df_city.to_json(area+'.json',orient='records')
        df_area.append(pd.concat(df_page_list))
        
    return df_area

def crawler(elements, city):
  df_591 = {'城市':[], '標題':[], "出租者":[], "出租者身分":[],"連絡電話":[],"型態":[], "現況":[],"性別要求":[]}
  for tag in elements:
    # 輸出超連結網址
    print(tag.get('href'))
    options = Options()
    options.add_argument("--disable-notifications")  # 取消所有的alert彈出視窗

    driver = webdriver.Chrome(
        ChromeDriverManager().install(),chrome_options=options)
    time.sleep(10)
    driver.get(tag.get('href'))
    time.sleep(10)
    inner_soup = BeautifulSoup(driver.page_source, "html.parser")
    title_elements = inner_soup.find_all('div',{"class":'house-title'})
    title = title_elements[-1].getText().strip()
    house_elements = inner_soup.find_all('div',{"class":'house-pattern'})
    owner_elements = inner_soup.find_all('div',{"class":'info'})
    phone_elements = inner_soup.find_all('span',{"class":'tel-txt'})
    # print(phone_elements)
    try:
      phone_num = phone_elements[-1].getText().strip()
    except:
      phone_num = 'NULL'
    rule_elements = inner_soup.find_all('div',{"class":'service-rule'})
    
    for element in house_elements:
      try :
        condition = element.find_all('span')[0].getText().strip()
        house_condition = element.find_all('span')[-1].getText().strip()
      except:
        condition, house_condition = 'NULL'
    owner='NULL'
    for element in owner_elements:
      try:
        owner = element.find('p').getText().strip()
        if "仲介勿擾" in owner:
          owner_ = owner.split('\n')[0].split(": ")[0]
        elif "收服務費" in owner:
          owner_ = owner.split('\n')[0].split(": ")[0]
        # 代理人
        else:
          owner_ = owner.split('\n')[0].split(": ")[0]
          owner_name = owner.split('\n')[0].split(": ")[1]
        owner_name = owner.split('\n')[0].split(": ")[1]
      except:
        owner='NULL'

    # for element in phone_elements:
    #   phone = element.findAll('span')
    # phone_num = phone[-1].getText().strip()
    # phone_num = phone_elements[-1].getText().strip()

    for element in rule_elements:
      rule = element.findAll('span')
    rule_ = rule[-1].getText().strip()
    print(rule)
    print(rule_)

    # rule_ = rule[-1].getText().strip()
    if "房屋男女皆可租住" in rule_:
      house_rule = '男女生皆可'
    elif "房屋限女生租住" in rule_:
      house_rule = '限住女性'
    elif "房屋限男性租住" in rule_:
      house_rule = '限住男性'
    else:
      house_rule = '男女生皆可'
    
    print(city)
    print(title)
    print(condition)
    print(house_condition)
    print(owner_)
    print(owner_name)
    print(phone_num)
    print(house_rule)
    
    df_591['城市'].append(city)
    df_591['標題'].append(title)
    df_591['出租者'].append(owner_name)
    df_591['出租者身分'].append(owner_)
    df_591['連絡電話'].append(phone_num)
    df_591['型態'].append(condition)
    df_591['現況'].append(house_condition)
    df_591['性別要求'].append(house_rule)
    time.sleep(10)
    driver.close()
    
  return df_591

if __name__ == '__main__':
    area_dict={"台北市":1, '新北市':3}
    data = main_page(area_dict)