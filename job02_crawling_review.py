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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import datetime
import time

# ChromeOptions 객체 생성 (브라우저 옵션 설정)
options = ChromeOptions()

# 사용자 에이전트(user agent) 설정 - 크롬 브라우저로 인식되도록 설정
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
options.add_argument('user_agent=' + user_agent)
options.add_argument('lang=ko_KR')  # 언어 설정: 한국어

# Chrome WebDriver 설정
service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 크롤링할 CSV 파일 경로 설정
file_path = 'C:/work/movie_for_you_intel03/crawling_data/movie_review03_20250203.csv'

# 기존 CSV 파일에서 영화 링크 읽어오기
movie_links = pd.read_csv(file_path)["movie_link"].tolist()

# 영화 링크 중 처음 500개만 사용
movie_links = movie_links[:500]

# 영화 제목을 가져오는 함수
def get_movie_title(movie_url):
    driver.get(movie_url)  # 영화 페이지 접속
    time.sleep(2)  # 페이지 로딩 대기

    try:
        # 영화 제목을 XPATH로 찾기
        title = driver.find_element(By.XPATH, "//*[@id='contents']/div[1]/div[2]/div[1]/div[1]/h2").text
    except Exception as e:
        # 예외가 발생하면 "제목 없음"으로 처리
        title = "제목 없음"
    return title

# 영화 리뷰를 가져오는 함수
def get_movie_reviews(movie_url, max_reviews=20):
    driver.get(movie_url)  # 영화 페이지 접속
    time.sleep(1)  # 페이지 로딩 대기

    reviews = []  # 리뷰를 저장할 리스트

    try:
        # 리뷰 버튼 클릭 (리뷰를 보기 위한 버튼)
        review_button = driver.find_element(By.XPATH, "//*[@id='review']")
        review_button.click()
        time.sleep(1)  # 버튼 클릭 후 리뷰 로딩 대기
    except Exception as e:
        print("리뷰 버튼을 클릭하는데 문제가 발생했습니다.")

    # ActionChains 객체 생성 (마우스나 키보드 입력을 자동화)
    actions = ActionChains(driver)

    # 리뷰 탭으로 이동
    review_btn_xpath = '//*[@id="review"]'
    time.sleep(0.3)
    driver.find_element(By.XPATH, review_btn_xpath).click()  # 리뷰 탭 클릭
    time.sleep(1)

    # 페이지 스크롤
    actions.send_keys(Keys.PAGE_DOWN).perform()  # 페이지를 아래로 스크롤
    category_btn_xpath = '//*[@id="contents"]/div[5]/section[2]/div/div[2]/div[1]/button[1]'
    time.sleep(0.3)
    driver.find_element(By.XPATH, category_btn_xpath).click()  # '전체' 버튼 클릭

    # 약 400번 페이지 다운 (최대 50개 리뷰 수집을 위해 충분한 페이지 스크롤)
    for j in range(400):
        actions.send_keys(Keys.PAGE_DOWN).perform()

    # 페이지의 HTML 소스 가져오기
    resp = driver.page_source
    soup = BeautifulSoup(resp, 'html.parser')  # BeautifulSoup으로 HTML 파싱
    articles = soup.find_all('article')  # 모든 article 요소 찾기

    time.sleep(5)

    # 리뷰 수집
    for idx, article in enumerate(articles, start=1):
        try:
            review_element = article.find('div', class_='review-item__contents')  # 리뷰가 포함된 div
            if review_element:
                review = review_element.find('h5').get_text().strip()  # 실제 리뷰 텍스트 추출
            else:
                review = 'No review text available'  # 리뷰가 없을 경우

            # 리뷰 저장 메시지 출력
            print(f"{idx}번째 리뷰 저장")
            print(f"리뷰: {review}")

            # 최대 50개 리뷰까지만 저장
            if idx >= 50:
                break  # 50개가 넘으면 루프 종료

            reviews.append(review)  # 리뷰 리스트에 추가

        except Exception as e:
            print(f"오류 발생: {e}")
            continue  # 오류 발생 시 넘어가도록 설정

    return reviews  # 리뷰 리스트 반환

# 각 영화마다 리뷰를 별도의 CSV 파일로 저장하는 과정
for movie_url in movie_links:
    try:
        print(f"크롤링 중: {movie_url}")  # 크롤링 중인 영화 URL 출력
        title = get_movie_title(movie_url)  # 영화 제목 가져오기
        reviews = get_movie_reviews(movie_url)  # 영화 리뷰 가져오기

        # 영화 제목과 리뷰 데이터를 DataFrame으로 저장
        df_movie = pd.DataFrame({
            "title": [title] * len(reviews),  # 리뷰 개수만큼 영화 제목 반복
            "review": reviews  # 해당 영화의 리뷰 리스트
        })

        # 파일명에 영화 제목을 포함하여 CSV로 저장 (파일 이름을 안전하게 만들기 위해 공백이나 특수문자 처리)
        filename = f"C:/work/movie_for_you_intel03/movie_title_review03/{title}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df_movie.to_csv(filename, index=False)  # DataFrame을 CSV 파일로 저장

        print(f"{title}의 리뷰를 {filename} 파일로 저장했습니다.")  # 저장 완료 메시지 출력

    except Exception as e:
        print(f"Error while scraping {movie_url}: {e}")  # 크롤링 도중 오류 발생 시 출력

# 크롤링이 끝난 후 브라우저 종료
driver.quit()

print("크롤링이 완료되었습니다.")  # 전체 크롤링 완료 메시지 출력
