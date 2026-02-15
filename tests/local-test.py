import os
import re
import time
import uuid
import requests
from collections import Counter
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# CONFIGURATION
BASE_URL = "https://elpais.com/opinion/"

# RAPIDAPI CREDENTIALS HERE
RAPIDAPI_KEY = 'RAPIDAPI_KEY'
RAPIDAPI_HOST = "google-translate113.p.rapidapi.com"

# Unique folder per parallel session
SESSION_ID = str(uuid.uuid4())[:8]
IMAGE_DIR = f"downloaded_images_{SESSION_ID}"

# DRIVER SETUP
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--lang=es")
    return webdriver.Chrome(options=options)

# COOKIE HANDLER
def accept_cookies(driver):
    wait = WebDriverWait(driver, 10)
    try:
        button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Aceptar')]")
            )
        )
        button.click()
    except Exception:
        pass

# IMAGE DOWNLOAD
def download_image(image_url, index):
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        filename = os.path.join(IMAGE_DIR, f"article_{index}.jpg")

        with open(filename, "wb") as file:
            file.write(response.content)

        print(f"Image saved: {filename}")

    except Exception:
        print("Image download failed.")

# TRANSLATION


def translate_text(text):
    if not text:
        return ""

    url = f"https://{RAPIDAPI_HOST}/api/v1/translator/text"

    payload = {
        "from": "es",
        "to": "en",
        "text": text
    }

    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    try:
        time.sleep(1)  # avoid rate limit in parallel

        response = requests.post(url, json=payload, headers=headers, timeout=15)

        if response.status_code != 200:
            print("Translation API error:", response.status_code)
            return text

        result = response.json()

        if isinstance(result, dict) and "trans" in result:
            return result["trans"]

        return text

    except Exception:
        return text


# GET FIRST 5 LINKS
def get_first_five_links(driver):
    wait = WebDriverWait(driver, 20)

    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "article h2 a"))
    )

    article_links = driver.find_elements(By.CSS_SELECTOR, "article h2 a")

    links = []
    for link in article_links:
        href = link.get_attribute("href")
        if href and href not in links:
            links.append(href)
        if len(links) == 5:
            break

    return links

# SCRAPE ARTICLE

def scrape_article(driver, url, index):
    wait = WebDriverWait(driver, 20)

    driver.get(url)

    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "article h1"))
    )

    print(f"\n===== ARTICLE {index} =====")

    # TITLE
    try:
        title_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article h1"))
        )
        title = title_element.text.strip()
    except Exception:
        title = ""

    print("Title (Spanish):", title)

    # CONTENT
    try:
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "p.a_st, h2.a_st")
            )
        )

        elements = driver.find_elements(
            By.CSS_SELECTOR,
            "p.a_st, h2.a_st"
        )

        content = ""
        for el in elements:
            if el.is_displayed():
                content = el.text.strip()
                break

    except Exception:
        content = ""

    print("Content (Spanish):")
    print(content)

    # IMAGE
    try:
        image_meta = driver.find_element(
            By.XPATH,
            "//meta[@property='og:image']"
        )

        image_url = image_meta.get_attribute("content")

        if image_url and not image_url.startswith("http"):
            image_url = urljoin(url, image_url)

        download_image(image_url, index)

    except Exception:
        print("No image found.")

    # TRANSLATE
    translated = translate_text(title)

    print("Title (English):", translated)

    return translated

# WORD ANALYSIS

def analyze_repeated_words(titles):
    words = []

    for title in titles:
        extracted = re.findall(r"\b[a-zA-Z]+\b", title.lower())
        words.extend(extracted)

    counts = Counter(words)

    print("\n===== REPEATED WORDS (>2 occurrences) =====")

    found = False

    for word, count in counts.items():
        if count > 2:
            print(f"{word}: {count}")
            found = True

    if not found:
        print("No words repeated more than twice.")


# MAIN

def main():
    os.makedirs(IMAGE_DIR, exist_ok=True)

    driver = setup_driver()

    try:
        driver.get(BASE_URL)
        accept_cookies(driver)

        links = get_first_five_links(driver)

        translated_titles = []

        for index, link in enumerate(links, start=1):
            translated = scrape_article(driver, link, index)
            translated_titles.append(translated)

        analyze_repeated_words(translated_titles)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
