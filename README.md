# Internet of Things Knowledge Grapg (IoT KG) 🧠

## Overview
<img src="assets/iot_kg_workflow.png"/>

## Web Scraper
<img src="assets/web_scraper_workflow.png"/>

## LLM Usage
<img src="assets/llm_workflow.png"/>

## Validators
<img src="assets/validator_workflow.png"/>

## Database
<img src="assets/database_workflow.png"/>

## Execute the code 💻

### Scrape a Website
```sh
  uv run -m src.scraper.scrape
```

### Scrape E-commerce
```sh
  uv run -m src.scraper.scrape_to_disk --<config_name>
```

Example for scraping Amazon:
```sh
  uv run -m src.scraper.scrape_to_disk --amazon
```
This command works by passing command-line arguments (e.g., --amazon) as keys into a dictionary of config files

### Scrape Private Policy
```sh
  In progress 🚧
```
