from typing import List, Dict
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def parse_rbc() -> List[Dict]:
    url = 'https://www.rbc.ru/short_news'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    quotes = soup.find_all('div', class_='item__wrap l-col-center')
    n_samples = len(quotes)
    links = [quote.find_all('a', class_='item__link')[0]["href"] for quote in quotes]
    categories = [quote.find_all('a', class_='item__category')[0].text.strip()[:-1] for quote in quotes]
    post_dates = [datetime.today().strftime('%Y-%m-%d') for i in range(n_samples)]
    post_times = [quote.find_all('span', class_='item__category')[0].text.strip() for quote in quotes]
    titles = [quote.find_all('span', class_='item__title rm-cm-item-text')[0].text.strip() for quote in quotes]
    news = [
        {"link": links[i], "category": categories[i], "post_date": post_dates[i], "post_time": post_times[i], "title": titles[i]}
            for i in range(n_samples)
            ]

    return news

def consultant_moth_preprocessor(ru_month_name: str) -> str:
    day, month, year = ru_month_name.split()

    month_dict = {
        "января": 1,
        "февраля": 2,
        "марта": 3,
        "апреля": 4,
        "мая": 5,
        "июня": 6,
        "июля": 7,
        "августа": 8,
        "сентября": 9,
        "октября": 10,
        "ноября": 11,
        "декабря": 12
    }
    month = month_dict[month]

    return f"{year}-{month}-{day}"

def parse_consultant(page_num=1) -> pd.DataFrame:
    url = f'https://www.consultant.ru/legalnews/?page={page_num}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    quotes = [el for el in soup.find_all('div', class_='listing-news__item')]
    links = ["https://www.consultant.ru" + el.find_all("a")[0]["href"] for el in quotes]
    titles = [el.find_all("span")[0].text for el in quotes]
    page_requests = [BeautifulSoup(requests.get(url).text, 'lxml')
             for url in links]

    pages = [el\
             .find_all("div", class_="news-page__text")[0]\
             .find_all("p")
             for el in page_requests]

    dates = list(map(consultant_moth_preprocessor, [el\
             .find_all("div", class_="news-page__date")[0].text
             for el in page_requests]))

    full_texts = []
    for page in pages:
        full_text = ""
        for text_tag in page:
            full_text += f"{text_tag.text}\n"
        full_texts.append(full_text)

    return pd.DataFrame({
        "title": titles,
        "full_text": full_texts,
        "link": links,
        "date": dates
    })


def parse_clerk(page_num=1) -> pd.DataFrame:
    url = f'https://www.klerk.ru/news/page/{page_num}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    quotes = [el for el in soup.find_all('article', class_='feed-item feed-item--normal')]
    links = ["https://www.klerk.ru" + el.find_all("a", class_="feed-item__link feed-item-link__check-article")[0]["href"] for el in quotes]
    n_samples = len(links)
    page_requests = [BeautifulSoup(requests.get(url).text, 'lxml')
             for url in links]

    titles = [
        el.find_all("header", class_="article__header")[0].find_all("h1")[0].text
        for el in page_requests
    ]

    full_texts = ["\n".join([tag.text.strip() for tag in el.find_all("div", class_="article__content")[0].find_all("p")])
             for el in page_requests]

    dates = [datetime.today().strftime('%Y-%m-%d')] * n_samples

    print(*full_texts, sep="\n")


    return pd.DataFrame({
        "title": titles,
        "full_text": full_texts,
        "link": links,
        "date": dates
    })

# all_parts = []
# for i in tqdm(range(1, 11)):
#     all_parts.append(parse_clerk(i))
#
# pd.concat(all_parts).to_csv("clerk_1.csv", index=False)

parse_clerk(0)