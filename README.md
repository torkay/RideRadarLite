# ⚠️ DEPRECATED ⚠️
# RideRadarLite

## Introduction

**RideRadarLite** is a lightweight, proprietary scraping engine for the now production RideRadar platform. It was developed as a solution to overcome **operating system constraints** and **brittleness** often associated with Selenium-based web scraping.

### Key Objectives Achieved
* Designed for deployment on **lightweight server hardware**, primarily `ARM64 Linux`.
* Migrated the browser automation foundation from Selenium to the more robust **Playwright** library.
* Features an **oversimplified, lightweight codebase**.
* Significantly **reduced external dependency constraints**.

## How to Use

### Step 1: Import Modules
```python
from rideradarlite import start, engine, embed
```

### Step 2: Initialize an Engine Object
*(Supported vendors as of version 0.1.0 include Gumtree and Facebook)*
```python
search_facebook = engine.SearchFacebook(verbose=False)
```

### Step 3: Print Header (Optional)
```python
start.print_header()
```
### Step 4: Run the Work Instance
```python
search_gumtree.main(vehicle_names_file='list.txt', output_file='./storage/listings_gumtree.json')
```
*Note: list.txt must contain a text list of vehicles, and the results will be written to listings_gumtree.json*

### Step 5: Embed Results to Discord (Optional)
```python
embed.main(type='gumtree')
```

## Important Disclosure
Automating browser tasks on a service that prohibits such activity may lead to penalties or service restrictions.
