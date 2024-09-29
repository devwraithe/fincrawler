import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from collections import deque

# set up chrome for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # run in headless mode
chrome_options.add_argument("--disable-gpu")  # disable gpu acceleration

# set up the webdriver
driverService = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=driverService, options=chrome_options)
# driver.maximize_window()

# start with the main page
start_url = "https://www.finance.yahoo.com/"
driver.get(start_url)

# set up the queue and visited urls set
url_queue = deque([start_url])
visited_urls = set()


# infinite scroll function
def infinite_scroll():
    scroll_pause_time = 2  # pause time for dynamic content to load
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# get all internal links on the page
def get_internal_links():
    page_links = driver.find_elements(By.TAG_NAME, 'a')
    int_links = set()  # internal links

    for page_link in page_links:
        href = page_link.get_attribute('href')
        if href and start_url in href and href not in visited_urls:
            int_links.add(href)

    return int_links


# store the scraped data in a list
articles = []
article_titles = set()  # set to track unique article titles

# set a limit for pages to crawl
MAX_PAGES = 100
pages_crawled = 0

# crawler loop
while url_queue and pages_crawled < MAX_PAGES:
    current_url = url_queue.popleft()
    if current_url in visited_urls:
        continue

    # visit the url and add it to the visited set
    driver.get(current_url)
    visited_urls.add(current_url)
    pages_crawled += 1  # increment the pages_crawled counter

    # scroll to load dynamic content
    infinite_scroll()

    # scrape the articles on the current page
    headlines = driver.find_elements(By.CSS_SELECTOR, "div.content.yf-16rx63c, div.content.yf-1e4au4k")

    for headline in headlines:
        try:
            title_element = headline.find_element(By.CSS_SELECTOR, 'h2, h3')
            title = title_element.text
            link = headline.find_element(By.TAG_NAME, 'a').get_attribute("href")

            # check for uniqueness before appending
            if title not in article_titles:
                articles.append({'title': title, 'link': link})
                article_titles.add(title)  # add to the set to track unique titles

        except Exception as e:
            print(f"Error scraping headline: {e}")
            continue

    # extract internal links and add to the queue
    internal_links = get_internal_links()
    url_queue.extend(internal_links)

    # delay between page requests to avoid rate limiting
    time.sleep(2)

    print(f"Crawled {pages_crawled} pages so far.")


# close the browser
driver.quit()

# convert the articles list to a DataFrame
df = pd.DataFrame(articles)

# save the data to a CSV file
df.to_csv('financial_news_crawler.csv', index=False)
print(f"Data saved to financial_news_crawler.csv with {len(articles)} articles.")

# close the browser
driver.quit()
