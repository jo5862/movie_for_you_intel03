#movie_review01.csv
#사이트
#ott하나당 500개
#리뷰 50개
#
from http.client import responses

from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import datetime
import time


#패키지 정상 다운로드 확인
# print("librarise are  installed succesfully")

options = ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
options.add_argument('user_agent=' + user_agent)
options.add_argument('lang=ko_KR')

service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url='https://m.kinolights.com/discover/explore'
driver.get(url)
time.sleep(7)

target_movie_count = 500
movie_link = []


while len(movie_link) < target_movie_count:
    # 현재 페이지에서 영화 제목들 추출
    time.sleep(1)#wait for movies to load

    #movie link crawling
    try:
        movies = driver.find_elements(By.XPATH,"//*[@id='contents']/div/div/div[3]/div[2]//a")
        for movie in movies:
            link = movie.get_attribute('href')
            if link and link not in movie_link: #중복을 피하기 위해 확인
                movie_link.append(link)
    except Exception as e:
        print(f"Error collecting movie links: {e}")
        continue
    # #if not enough movies, scroll down 8units to trigger loading of more movies
    # if len(movie_link) < target_movie_count:
    #     scroll_down(units=8, sleep_time=0.7)  # 스크롤을 5번 내리며, 각 스크롤 후 1초 대기
    #     print(f"Collected {len(movie_link)} movies so far...")
    if len(movie_link)>= target_movie_count:
        break
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

# 수집된 500개 영화 제목 출력
for title in movie_link[:target_movie_count]:
    print(title)
# DataFrame으로 변환 후 CSV로 저장
df = pd.DataFrame(movie_link[:target_movie_count], columns=["movie_link"])

df.to_csv('./crawling_data/movie_review03_{}.csv'.format(
    datetime.datetime.now().strftime('%Y%m%d')), index=False)

# 브라우저 종료
driver.quit()

print(f"총 {len(movie_link)}개의 제목을 수집했습니다.")