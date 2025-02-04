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

movie_titles = []

while len(movie_titles) <50:
    # 현재 페이지에서 영화 제목들 추출
    # 'poster-container' 클래스를 기반으로 추출
    movies = driver.find_elements(By.CLASS_NAME, "poster-container")

    #영화제목추출
    for movie in movies:
        try:
            title = movie.get_attribute("title")  # 'title' 속성에서 영화 제목 추출
            if title and title not in movie_titles:
                movie_titles.append(title)
        except Exception as e:
            print(f"Error: {e}")
            continue
        if len(movie_titles)>=50:
            break
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(1)

# 수집된 500개 영화 제목 출력
for title in movie_titles[:50]:
    print(title)

# 브라우저 종료
driver.quit()

print(f"총 {len(movie_titles)}개의 제목을 수집했습니다.")