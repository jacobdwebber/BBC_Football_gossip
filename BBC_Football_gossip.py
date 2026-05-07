#!/usr/bin/env python
# coding: utf-8

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import json
import os
import re

# Retrieve links for all articles from BBC football gossip pages 1 & 2. Returns 48 links

base_url = "https://www.bbc.co.uk"
archive_url = "https://www.bbc.co.uk/sport/football/gossip"
page_url = ["", "?page=2"]
articles = []

for page in page_url:
    url = urljoin(archive_url, page)
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    articles_html = soup.find_all("div", attrs={"type": "article"})
    for article in articles_html:
        link_tag = article.find("a", href=True)
        link = urljoin(base_url, link_tag["href"])
        articles.append(link)

# Drop last six links to leave a list of six weeks of articles

articles = articles[:-6]

# List of previously unchecked articles - should be just one a day

processed_file = "processed_articles.json"

if os.path.exists(processed_file):
    with open(processed_file, "r", encoding="utf-8") as file:
        processed_articles = json.load(file)
else:
    processed_articles = []

processed_urls = {p["url"] for p in processed_articles}

new_articles = [a for a in articles if a not in processed_urls]

# Import list of teams and their variations to tag articles with relevant teams

with open("teams.json", "r", encoding="utf-8") as file:
    teams_list = json.load(file)

def tag_teams(para, teams_list):
    found = set()
    lower_para = para.lower()
    
    for name, variations in teams_list.items():
        for var in variations:
            if var.lower() in lower_para:
                found.add(name)
                break
    
    return list(found)

# Define functions to retreive individual paragraphs from articles, removing the first which is always a summary

def get_soup(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    return soup
    
def clean_paras(p_tag):
    parts = []
    for t in p_tag.contents:
        if isinstance(t, str):
            parts.append(t)
        elif t.name == 'a':
            href = t.get('href', '')
            for hidden in t.find_all(class_='visually-hidden'):
                hidden.decompose()
            link_text = t.get_text(strip=True)
            if href.startswith('http') and link_text:
                parts.append(f'<a href="{href}" target="_blank" rel="noopener noreferrer">{link_text}</a>')
            else:
                parts.append(f'<u>{link_text}</u>')
        else:
            for hidden in t.find_all(class_='visually-hidden'):
                hidden.decompose()
            parts.append(t.get_text(strip=True))
    text = ' '.join(parts)
    text = ' '.join(text.split())
    return text

def get_paras(soup):
    body = soup.find("div", class_=re.compile("RichTextContainer"))
    paras = [clean_paras(p) for p in body.find_all("p")]
    return paras[1:]

def get_date(soup):
    time_tag = soup.find("time")
    date = time_tag.get_text(strip=True)
    return date

def process_article(url, teams_list):
    soup = get_soup(url)
    date = get_date(soup)
    paras = get_paras(soup)
    processed_paras = []
    for para in paras:
        teams = tag_teams(para, teams_list)
        processed_paras.append({
            "url": url,
            "date": date,
            "text": para,
            "teams": teams})
    return processed_paras

# Process all required articles and update processed_articles json file

processed_new_articles = []

for article in new_articles:
    processed_new_article = process_article(article, teams_list)
    processed_new_articles.extend(processed_new_article)

all_articles = processed_articles + processed_new_articles

valid_urls = set(articles)
all_articles = [p for p in all_articles if p["url"] in valid_urls]
all_articles.sort(key=lambda x: datetime.strptime(x["date"], "%d %B %Y"),reverse=True)

with open(processed_file, "w", encoding="utf-8") as file:
    json.dump(all_articles, file, indent=2, ensure_ascii=False)