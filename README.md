# BBC Football Gossip Summariser

A personal project to collect, organise, and display football transfer 
gossip from the BBC Sport website.

## What it does

The BBC Sport website publishes daily football gossip articles covering 
transfer rumours and news. This tool scrapes those articles, identifies 
which Premier League teams are mentioned in each paragraph, and presents 
them in a clean, searchable web page. Users can select a team from a 
dropdown to see all gossip mentioning that team from the last six weeks.

## How it works

The project has two parts:

**Data collection (`BBC_Football_gossip.py`)**
A Python script that scrapes the BBC Sport gossip pages, processes each 
article into individual paragraphs, tags each paragraph with the Premier 
League teams mentioned, and saves the results to `processed_articles.json`. 
Only new articles are processed each time the script runs, avoiding 
duplication. The script is run automatically every day at 1am via 
GitHub Actions, keeping the data fresh without any manual intervention.

**Web interface (`index.html`)**
A static HTML page hosted on GitHub Pages. It loads the processed data 
from `processed_articles.json` and `teams.json`, populates a dropdown 
with Premier League team names, and filters the gossip in the browser 
using JavaScript when a team is selected. No server is required.

## Project files

| File | Description |
|------|-------------|
| `BBC_Football_gossip.py` | Main scraper script |
| `teams.json` | Premier League teams and name variants used for tagging |
| `processed_articles.json` | Processed gossip data (auto-generated) |
| `index.html` | Static web page |
| `.github/workflows/scraper.yml` | GitHub Actions workflow for daily automation |

## Technologies used

- Python (requests, BeautifulSoup)
- GitHub Pages
- GitHub Actions
- HTML, CSS, JavaScript

## Notes

- This is a purely personal project and is not affiliated with or 
endorsed by the BBC.
- The `teams.json` file controls which teams are tracked. Name variants 
must be listed longest first to ensure correct text matching.
- Data is refreshed automatically each day but can also be updated 
manually by running `BBC_Football_gossip.py` locally.

## Author

Jacob Webber