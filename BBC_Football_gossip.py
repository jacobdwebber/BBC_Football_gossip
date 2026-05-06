#!/usr/bin/env python
# coding: utf-8

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
from urllib.parse import urljoin
import json
import os
import re
from flask import Flask, render_template_string, request

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

# Define Premier League Teams using different name variants

teams_list = {
    "Arsenal": ["Arsenal"],
    "Aston Villa": ["Aston Villa", "Villa"],
    "AFC Bournemouth": ["Bournemouth", "AFC Bournemouth"],
    "Brentford": ["Brentford"],
    "Brighton & Hove Albion": ["Brighton", "Brighton & Hove Albion"],
    "Burnley": ["Burnley"],
    "Chelsea": ["Chelsea"],
    "Crystal Palace": ["Crystal Palace", "Palace"],
    "Everton": ["Everton"],
    "Fulham": ["Fulham"],
    "Leeds United": ["Leeds", "Leeds United", "Leeds Utd"],
    "Liverpool": ["Liverpool"],
    "Manchester City": ["Manchester City", "Man City"],
    "Manchester United": ["Manchester United", "Man United", "Man Utd"],
    "Newcastle United": ["Newcastle United", "Newcastle"],
    "Nottingham Forest": ["Nottingham Forest", "Forest", "Nottm Forest"],
    "Sunderland": ["Sunderland"],
    "Tottenham Hotspur": ["Tottenham", "Spurs", "Tottenham Hotspur"],
    "West Ham United": ["West Ham", "West Ham United", "West Ham Utd"],
    "Wolverhampton Wanderers": ["Wolves", "Wolverhampton", "Wolverhampton Wanderers"],
}

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
        else: parts.append(t.get_text(strip=True))
    text = ' '.join(parts)
    text = ' '.join(text.split())
    text = re.sub(r'\(\s*[^)]*?,\s*external\s*\)', '', text, flags=re.IGNORECASE)
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


# Process all required articles

processed_new_articles = []

for article in new_articles:
    processed_new_article = process_article(article, teams_list)
    processed_new_articles.extend(processed_new_article)

all_articles = processed_articles + processed_new_articles

valid_urls = set(articles)
all_articles = [p for p in all_articles if p["url"] in valid_urls]
all_articles.sort(key=lambda x: datetime.strptime(x["date"], "%d %B %Y"),reverse=True)

# Write all to json file

with open(processed_file, "w", encoding="utf-8") as file:
    json.dump(all_articles, file, indent=2, ensure_ascii=False)


# Define function to query for a particular team and output all relevant paragraphs of gossip, with their dates

def get_team_gossip(all_articles, team_name):
    team_name_lower = team_name.lower()
    team_paras = [
        f"{para['text']} ({para['date']})"
        for para in all_articles
        if team_name_lower in [t.lower() for t in para['teams']]
    ]
    return team_paras

# Create the HTML user interface

html_template = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>BBC Football Gossip</title>
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Roboto', sans-serif;
      background-color: #f5f5f5;
      margin: 0;
      padding: 0;
      color: #222;
    }
    header {
      background-color: #FFB81C;  /* BBC Sport yellow */
      color: #000;                 /* black text */
      padding: 20px;
      text-align: center;
    }
    main {
      max-width: 900px;
      margin: 30px auto;
      background-color: #fff;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    form {
      margin-bottom: 20px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
    }
    select, input[type="submit"] {
      padding: 8px 12px;
      font-size: 16px;
      border-radius: 4px;
      border: 1px solid #ccc;
    }
    h1 {
      margin: 0;
      font-size: 28px;
    }
    h2 {
      margin-top: 20px;
      font-size: 22px;
      border-bottom: 2px solid #FFB81C;
      padding-bottom: 5px;
    }
    .gossip-container {
      max-height: 500px;
      overflow-y: auto;
      margin-top: 10px;
    }
    .gossip-container p {
      margin: 20px 0;
      line-height: 1.5;
    }
  </style>
</head>
<body>
  <header>
    <h1>BBC Football Gossip Summariser</h1>
  </header>
  <main>
    <p>Select a Premier League team to see all the gossip reported on the <a href="https://www.bbc.co.uk/sport/football/gossip" target="_blank" rel="noopener noreferrer">BBC website</a> in the last six weeks.</p>
    <form method="post">
      <label for="team">Choose a team:</label>
      <select name="team" id="team">
        <option value="" disabled selected>Select a team</option>
        {% for team in teams %}
        <option value="{{ team }}" {% if team==team_name %}selected{% endif %}>{{ team }}</option>
        {% endfor %}
      </select>
      <input type="submit" value="Show Gossip">
    </form>

    {% if team_name %}
      <h2>Gossip for {{ team_name }}</h2>
      {% if gossip %}
      <div class="gossip-container">
        {% for para in gossip %}
          <p>{{ para }}</p>
        {% endfor %}
      </div>
      {% else %}
        <p>No gossip found for {{ team_name }} in the last six weeks.</p>
      {% endif %}
    {% endif %}
  </main>
</body>
</html>
"""


app = Flask(__name__)

# Make a sorted list of team names for the dropdown

teams_available = sorted(list(teams_list.keys()))

# Apply get_team_gossip within the user interface app

@app.route("/", methods=["GET", "POST"])
def home():
    team_name = None
    gossip = []

    if request.method == "POST":
        team_name = request.form.get("team")
        if team_name:
            team_name = team_name.strip()
            # Gather gossip for selected team
            gossip = get_team_gossip(all_articles, team_name)

    return render_template_string(html_template, teams=teams_list.keys(), gossip=gossip, team_name=team_name)

if __name__ == "__main__":
    app.run(debug=True)