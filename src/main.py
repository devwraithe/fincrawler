import requests
from bs4 import BeautifulSoup
from collections import deque
import time
import pandas as pd

# url to scrape
initial_url = "https://www.finance.yahoo.com/"

# store urls to be crawled
url_queue = deque([initial_url])

# create a set to store visited urls
visited_urls = set()

# list to store the scraped data
articles = []

# set a limit for the number of pages to crawl
MAX_PAGES = 100

# modify the loop to stop when the limit is reached
pages_crawled = 0

print("Please wait...")

# loop through the queue while there are urls left to crawl
while url_queue and pages_crawled < MAX_PAGES:

    current_url = url_queue.popleft()  # get the next url in queue

    if current_url in visited_urls:  # check if this url has been visited
        continue

    # fetch the page content
    response = requests.get(current_url)

    # check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve {current_url}")
        continue

    # parse html using beautifulsoup
    parse_html = BeautifulSoup(response.content, "html.parser")

    # mark the url as visited
    visited_urls.add(current_url)

    # extract article headlines and links
    headlines = parse_html.find_all("div", class_="content")

    # loop through the headlines and extract relevant data
    for headline in headlines:
        title = headline.find(['h2', 'h3']).text
        link = headline.find("a")["href"]

        articles.append({'title': title, 'link': link})

        # add the new link to the queue if it hasn't been visited yet
        if link not in visited_urls:
            url_queue.append(link)

    pages_crawled += 1
    time.sleep(2)

# convert the articles list to a DataFrame
df = pd.DataFrame(articles)

# save the data to a csv file
df.to_csv('financial_news_crawler.csv', index=False)
print("Data saved to financial_news_crawler.csv")
