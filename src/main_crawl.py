import json
import logging
import time
from pathlib import Path
from typing import Tuple

# noinspection PyUnresolvedReferences
import chromedriver_binary
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, ChromeOptions

logging.basicConfig(level=logging.INFO)

options = ChromeOptions()
options.add_argument('--headless')
driver = Chrome(options=options)


# ref. https://gist.github.com/ruhiel/12c3f8415b568e4fdf6a1acc4b0914a4

class TogetterCrawler:

    def crawl_pages(self, url: str, name: str, max_pages: int = 99) -> None:
        index = 1
        while True:
            time.sleep(1)
            logging.info(f'{name}:{index:03}-- Fetching {url}')
            url, html = self._crawl(url)
            path = Path(f"result/{name}/{index:03}.html")
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, mode='w') as f:
                f.write(html + '\n')
            if url is None:
                break
            if index >= max_pages:
                break
            index += 1

    def _crawl(self, url: str) -> Tuple[str, str]:
        """togetterページのクローリングを行い、htmlと次のページを返す"""
        driver.get(url)
        more_tweet_id = "more_tweet_btn"
        driver.implicitly_wait(5)

        if len(driver.find_elements_by_id(more_tweet_id)) > 0:
            # ref. https://qiita.com/toimenbou/items/635a6e0e241149317e32
            # 「残りを読む」を押下する必要がある
            element = driver.find_element_by_id(more_tweet_id)
            driver.execute_script("arguments[0].click();", element)
            logging.info(f'found more-tweet-btn...')

        if len(driver.find_elements_by_id(more_tweet_id)) > 0:
            logging.warning(f'remaining more-tweet-btn')

        # htmlソースを取得
        html = driver.page_source
        # htmlパースを実行
        soup = BeautifulSoup(html, 'lxml')
        elements = soup.find_all("link", attrs={"rel": "next"})

        # 次のURLを取得する
        if len(elements) > 0:
            next_url = elements[0]['href']
        else:
            next_url = None
        return (next_url, html)


if __name__ == "__main__":
    input_json_path = "src/input.json"
    with open(input_json_path, "r") as f:
        input_data = json.load(f)
    url = input_data["url"]
    name = input_data["name"]
    crawler = TogetterCrawler()
    crawler.crawl_pages(url, name)
