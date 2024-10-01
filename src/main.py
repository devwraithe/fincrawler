import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from collections import deque

print("Crawler initiated")

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

driverService = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=driverService, options=chrome_options)

urls = deque([
    "https://www.finance.yahoo.com/",
    "https://www.cnbc.com/",
])

visited_urls = set()
pages_crawled = 0

articles = []
articles_titles = set()


def internal_links_new(parent):
    desired_texts = ["news", "market"]
    parent_links = parent.find_elements(By.CSS_SELECTOR, "a")
    int_links = set()

    for int_link in parent_links:
        int_href = int_link.get_attribute("href")

        # Check if int_href exists, contains any of the desired_texts, and is not already visited
        if int_href and any(text in int_href for text in desired_texts) and int_href not in visited_urls:
            int_links.add(int_href)

    return int_links


print("-" * 10)
while urls:
    url = urls.popleft()  # Process the next URL

    try:
        print(f"Crawler processing: {url}")
        driver.get(url)

        content = driver.find_elements(By.CSS_SELECTOR, "div.content, li.js-stream-content, "
                                                        "div.FeaturedCard-contentText, div.RiverHeadline-headline, "
                                                        "div.LatestNews-headlineWrapper, div.Card-pro",)
        navigation = driver.find_elements(By.CSS_SELECTOR, "li._yb_l34kgb, ul.nav-menu-subLinks",)

        # For storing links discovered in this iteration
        internal_links = set()

        for data in content:
            try:
                title = data.find_element(By.CSS_SELECTOR, "h2, h3, a").text
                link = data.find_element(By.TAG_NAME, "a").get_attribute("href")

                # check for uniqueness before appending
                if title not in articles_titles:
                    articles.append({'title': title, 'link': link})
                    articles_titles.add(title)

            except Exception as e:
                print(f"Content scraping failed: {e}")
                continue

        for link in navigation:
            try:
                retrieved_links = internal_links_new(link)
                internal_links.update(retrieved_links)

            except Exception as e:
                print(f"Navigation link scraping failed: {e}")
                continue

    except Exception as e:
        print(f"URL loading failed: {e}")
        continue

    pages_crawled += 1
    visited_urls.add(url)
    print(f"Crawled {pages_crawled} pages so far")

    # Ensure only unvisited URLs are added to the queue
    for link in internal_links:
        if link not in visited_urls and link not in urls:
            urls.append(link)

    print(f"Retrieved {len(articles)} articles so far")
    print("-" * 10)

print(f"Crawled {pages_crawled} pages in total")
print(f"Retrieved {len(articles)} articles in total")

# Save the articles to a CSV file
df = pd.DataFrame(articles)
df.to_csv('articles.csv', index=False)
print(f"{len(articles)} saved to articles.csv")

driver.quit()
print("Crawling done!")
