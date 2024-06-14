from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.window import WindowTypes
import time
from selenium.webdriver import ActionChains
import json
import re

options = Options()
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=options)


def get_links():
    links = []
    paper_elements = driver.find_elements(By.XPATH, "//a[@class='fw-bold']")
    for paper in paper_elements:
        links.append(paper.get_attribute('href'))
    return links


def extract_article_info(links):
    data = []
    driver.switch_to.new_window(WindowTypes.TAB)
    for art in links:
        if 'courses' not in art:

            driver.get(art)
            time.sleep(1)

            article_info = {}
            article_info['title'] = driver.find_element(
                By.CLASS_NAME, 'document-title').text

            try:
                pages = driver.find_element(
                    By.XPATH, '//*[@id="xplMainContentLandmark"]/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/div/xpl-document-abstract/section/div[2]/div[2]/div[1]/div[1]').text.split(':')[-1]
            except:
                pages = None

            article_info['Pages'] = pages

            cites = driver.find_elements(
                By.CLASS_NAME, 'document-banner-metric-count')
            if len(cites) == 3:
                article_info['Cites in Papers'] = cites[0].text
                article_info['Cites in Patent'] = cites[1].text
                article_info['Full Text Views'] = cites[2].text
            elif len(cites) == 2:
                article_info['Cites in Papers'] = cites[0].text
                article_info['Cites in Patent'] = None
                article_info['Full Text Views'] = cites[1].text
            elif len(cites) == 1:
                article_info['Cites in Papers'] = None
                article_info['Cites in Patent'] = None
                article_info['Full Text Views'] = cites[0].text
            else:
                article_info['Cites in Papers'] = None
                article_info['Cites in Patent'] = None
                article_info['Full Text Views'] = None

            article_info['Publisher'] = driver.find_element(
                By.XPATH, '//*[@id="xplMainContentLandmark"]/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/div/xpl-document-abstract/section/div[2]/div[3]/div[2]/div[2]/xpl-publisher/span/span/span/span[2]').text

            article_info['DOI'] = driver.find_element(
                By.XPATH, '//*[@id="xplMainContentLandmark"]/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/div/xpl-document-abstract/section/div[2]/div[3]/div[2]/div[1]/a').text

            try:
                conf_date = driver.find_element(
                    By.CLASS_NAME, 'doc-abstract-confdate').text.split(':')[-1]
            except:
                pub = driver.find_element(
                    By.XPATH, '//*[@id="xplMainContentLandmark"]/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/div/xpl-document-abstract/section/div[2]/div[2]/a').text.split(':')[-1]
                year_pattern = re.compile(r'\b\d{4}\b')
                year_result = year_pattern.search(pub)
                conf_date = year_result

            article_info['Date of Publication'] = conf_date

            article_info['abstract'] = driver.find_element(
                By.XPATH, '//*[@id="xplMainContentLandmark"]/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/div/xpl-document-abstract/section/div[2]/div[1]/div/div/div').text

            published_name = driver.find_element(
                By.XPATH, '//*[@id="xplMainContentLandmark"]/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/div/xpl-document-abstract/section/div[2]/div[2]/a').text.split(':')[-1]
            published_link = driver.find_element(
                By.XPATH, '//*[@id="xplMainContentLandmark"]/div/xpl-document-details/div/div[1]/div/div[2]/section/div[2]/div/xpl-document-abstract/section/div[2]/div[2]/a').get_attribute('href')
            article_info['Published in'] = [
                {"name": published_name, "link": published_link}]

            authors_btn = driver.find_element(
                By.XPATH, '//*[@id="document-tabs"]/div[2]/a')
            authors_btn.click()

            authors_list = driver.find_elements(
                By.CSS_SELECTOR, '.authors-accordion-container')
            authors = []
            for author_info in authors_list:
                name = author_info.find_element(By.CSS_SELECTOR, 'a span')

                author_name = name.text.strip()
                from_element = author_info.find_element(
                    By.CSS_SELECTOR, 'div:nth-child(2)')
                try:
                    second_from = author_info.find_element(
                        By.CSS_SELECTOR, 'div:nth-child(3)')
                    from_ = {from_element.text.strip(),
                             second_from.text.strip()}
                except:
                    from_ = from_element.text.strip()
                authors.append({"name": author_name, "from": from_})

            article_info['Authors'] = [authors]

            keywords_element = driver.find_element(
                By.XPATH, '//*[@id="document-tabs"]/div[6]/a')
            if article_info['title'] == 'Security Assessment Model for Blockchain Software and Hardware Fusion Device Based on Decision Tree Algorithm':
                keywords_element = driver.find_element(
                    By.XPATH, '//*[@id="document-tabs"]/div[5]/a')

            keywords_element.click()

            ieee_keywords = driver.find_element(
                By.XPATH, '//*[@id="keywords"]/xpl-document-keyword-list/section/div/ul/li[1]/ul').text.split('\n')
            ieee_keywords = [item for item in ieee_keywords if item != ',']
            article_info['IEEE Keywords'] = ieee_keywords

            author_keywords = driver.find_element(
                By.XPATH, '//*[@id="keywords"]/xpl-document-keyword-list/section/div/ul/li[3]/ul').text.split('\n')
            author_keywords = [
                item1 for item1 in author_keywords if item1 != ',']
            article_info['Author Keywords'] = author_keywords

            data.append(article_info)
    driver.switch_to.window(driver.window_handles[0])
    return data


try:
    driver.get("https://ieeexplore.ieee.org/Xplore/home.jsp")

    search_Xpath = '//*[@id="LayoutWrapper"]/div/div/div[3]/div/xpl-root/header/xpl-header/div/div[2]/div[2]/xpl-search-bar-migr/div/form/div[2]/div/div[1]/xpl-typeahead-migr/div/input'
    element = driver.find_element(By.XPATH, search_Xpath)
    element.send_keys("Blockchain")
    element.send_keys(Keys.RETURN)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located(
        (By.CLASS_NAME, 'List-results-items')))
    i = 1
    while i < 6:
        if i > 1:
            next_btn = driver.find_element(
                By.CLASS_NAME, f'stats-Pagination_{i}')
            next_btn.click()
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'List-results-items')))
        links = get_links()
        data = extract_article_info(links=links)
        print(data)
        i += 1

        # time.sleep(5)


except Exception as e:
    print(e)


driver.quit()