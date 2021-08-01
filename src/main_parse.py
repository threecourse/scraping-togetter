import json
import os
import re
from pathlib import Path
from typing import Tuple, List

import pandas as pd
from bs4 import BeautifulSoup


class Parser:

    def run(self, root_path: Path) -> pd.DataFrame:
        paths = self._get_paths(root_path)

        attrs_list = []
        for path in paths:
            attrs_list += self._get_attrs_list(path)

        attrs_records = []
        for url, time, text in attrs_list:
            attrs_records.append({"url": url, "time": time, "text": text})
        df = pd.DataFrame(attrs_records)
        return df

    def _get_paths(self, root_path: Path) -> List[Path]:
        paths = []
        for dirpath, dirnames, filenames in os.walk(root_path):
            for filename in filenames:
                if re.match(r'\d+.html', filename):
                    path = os.path.join(dirpath, filename)
                    paths.append(path)
        paths = sorted(paths)
        paths = [Path(path) for path in paths]
        return paths

    def _get_attrs_list(self, path: Path) -> List[Tuple[str, str, str]]:
        attrs_list = []
        with open(path, mode='r') as f:
            html = "".join([line for line in f.readlines()])
            soup = BeautifulSoup(html, 'lxml')
            tweet_elements = soup.find_all("div", attrs={"class": "type_tweet"})
            for tweet_element in tweet_elements:
                attrs = self._get_attrs(tweet_element)
                attrs_list.append(attrs)
        return attrs_list

    def _get_attrs(self, tweet_element) -> Tuple[str, str, str]:
        status = tweet_element.find("span", attrs={"class": "status"})
        tweet_url = status.find("a", attrs={"class": "link"})["href"]
        tweet_time = status.find("a", attrs={"class": "link"}).text
        tweet_text = tweet_element.find("p", attrs={"class": "tweet"}).text
        tweet_url = tweet_url.strip()
        tweet_time = tweet_time.strip()
        tweet_text = tweet_text.strip()
        return (tweet_url, tweet_time, tweet_text)


if __name__ == "__main__":
    input_json_path = "src/input.json"
    with open(input_json_path, "r") as f:
        input_data = json.load(f)

    name = input_data["name"]
    root_path = Path(f"result/{name}")
    parser = Parser()
    df = parser.run(root_path)
    df.to_csv(f"result/{name}.txt", index=False, sep="\t")
