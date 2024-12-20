from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import locale
import re
import time

# 러시아어 날짜 처리를 위해 locale 설정
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # 러시아어 (UTF-8 지원)

# Selenium 설정
driver = webdriver.Chrome()  # ChromeDriver 경로가 설정되어 있어야 함
driver.get("https://russian.rt.com/search?q=%D0%BC%D0%BE%D1%81%D0%BA%D0%B2%D0%B0&type=&df=2022-10-01&dt=2024-12-20")  # 검색 URL

# 스크롤 및 더보기 버튼 클릭
scroll_pause_time = 10
while True:
    try:
        # "더보기" 버튼 찾기 및 클릭
        more_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.button__item.button__item_listing"))
        )
        more_button.click()
        time.sleep(scroll_pause_time)  # 로드 대기
    except Exception:
        print("모든 결과를 불러왔습니다.")
        break

# BeautifulSoup로 HTML 파싱
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

# 정규 표현식 키워드 설정
pattern = re.compile(r'^москв.*', re.IGNORECASE)

# 기사 제목, 링크 추출
articles = soup.find_all('a', class_='link link_color')
article_data = []

print(f"수집된 기사 개수: {len(articles)}")

for article in articles:
    title = article.text.strip()
    link = "https://russian.rt.com" + article['href']
    parent_div = article.find_parent('div', class_='card')

    # 제목과 링크 출력 (디버깅)
    print(f"제목: {title}, 링크: {link}")

    # 키워드 필터링: 정규 표현식 적용
    if not pattern.match(title):
        continue

    # 날짜 추출 (날짜 필터링은 제거)
    if parent_div:
        time_tag = parent_div.find('time', class_='date')
        date_text = time_tag.text.strip() if time_tag else "날짜 없음"
        article_data.append({"Title": title, "Link": link, "Date": date_text})

# 데이터프레임 생성 및 엑셀 저장
df = pd.DataFrame(article_data)
output_file = "filtered_articles_with_keyword.xlsx"
try:
    df.to_excel(output_file, index=False, engine="openpyxl")
    print(f"엑셀 파일이 저장되었습니다: {output_file}")
except Exception as e:
    print(f"엑셀 저장 오류: {e}")
