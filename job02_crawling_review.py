from http.client import responses
from bs4 import BeautifulSoup
import requests
import re
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import datetime
import time

options = ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
options.add_argument('user_agent=' + user_agent)
options.add_argument('lang=ko_KR')

service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

file_path = 'C:/work/movie_for_you_intel03/crawling_data/movie_review03_20250203.csv'


# 기존 CSV 파일에서 영화 링크 읽어오기
movie_links = pd.read_csv(file_path)["movie_link"].tolist()

movie_links = movie_links[:2]
movie_data = []

#-----------영화 제목 크롤링 함수---------------
def get_movie_title(movie_url):
    driver.get(movie_url)
    time.sleep(2)

    try:
        title = driver.find_element(By.XPATH, "//*[@id='contents']/div[1]/div[2]/div[1]/div[1]/h2").text
    except Exception as e:
        title = "제목 없음"
    return title

#--------- 리뷰 크롤링 함수-----------------
def get_movie_reviews(movie_url, max_reviews=20):
    driver.get(movie_url)
    time.sleep(1)  # 페이지 로딩을 위한 대기 시간 설정

    reviews = []

    try:
        # 리뷰 버튼 클릭 (리뷰가 보이도록 하기 위해)
        review_button = driver.find_element(By.XPATH, "//*[@id='review']")
        review_button.click()
        time.sleep(1)  # 버튼 클릭 후 리뷰가 로드될 때까지 대기
    except Exception as e:
        print("리뷰 버튼을 클릭하는데 문제가 발생했습니다.")

    # 스크롤 다운하여 리뷰 로딩
    scroll_down(driver, units=1, sleep_time=0.5)  # 필요한 만큼 스크롤을 내리도록 설정

    while len(reviews) < max_reviews:
        try:
            review_elements = driver.find_elements(By.XPATH, "//*[@id='contents']/div[5]/section[2]/div/article[3]/div[3]/a")
            for review_element in review_elements:
                review = review_element.text
                if review and len(reviews) < max_reviews:
                    reviews.append(review)
            #스크롤을 내려서 더 많은 리뷰 로딩
                scroll_down(driver, units=1, sleep_time=0.5)
                time.sleep(1)
        except Exception as e:
                print(f"Error while scraping reviews: {e}")
                break
    return reviews[:max_reviews]  # 50개 리뷰까지만 반환

#--------------스크롤 내리는 함수-------------
def scroll_down(driver, units=1, sleep_time=0.5):
    """
    Scrolls down the page by a fraction of the scrollable container's height.
    You might need to adjust the target container.
    """
    try:
        # First try to scroll the designated container
        container = driver.find_element(By.XPATH, "//*[@id='review-section']")
        for _ in range(units):
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;", container
            )
            time.sleep(sleep_time)
    except Exception:
        # Fallback to scrolling the window if container not found
        for _ in range(units):
            driver.execute_script("window.scrollBy(0, window.innerHeight/3);")
            time.sleep(sleep_time)
#------------------------------------------------------

for movie_url in movie_links:
    try:
        print(f"크롤링 중:{movie_url}")
        title = get_movie_title(movie_url)
        movie_data.append({
            "title": title,
            "reviews": get_movie_reviews(movie_url)
        })

    except Exception as e:
        print(f"Error while scraping {movie_url}:{e}")

df_movies = pd.DataFrame(movie_data)

df_movies.to_csv('C:/work/movie_for_you_intel03/movie_title_review03/movie_titles_{}.csv'.format(datetime.datetime.now().strftime('%Y%m%d')), index=False)

# 브라우저 종료
driver.quit()

print(f"총 {len(df_movies)}개의 영화 제목을 수집했습니다.")