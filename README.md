# RideRadarLite
## Introduction
RideRadarLite is light-weight alternative to RideRadar.
The RR-Lite engine is the solution to the constraints of the selenium driver.
This version will always be open-source and free.
### Main objective
* Serviceable on any silicon, specifically `ARM64 Linux`
* Implement the playwright library rather a selenium-based one
* Light-weight codebase
* Reduction of dependency constraints

## How to use
### Step 1: Import libraries
    from rideradarlite import start, engine, embed
### Step 2: Create object
*Vendors include `Gumtree` and `Facebook` as of version 0.1.0*

    search_facebook = engine.SearchFacebook(verbose=False)
### Step 3: Print heading (optional)
    start.print_header()
### Step 4: Create a work instance from the engine object
    search_gumtree.main(vehicle_names_file='list.txt', output_file='./storage/listings_gumtree.json')
*Where `list.txt` is a text list of vehicles, and `listings_gumtree.json` is the result*
### Step 5: Embed to discord (optional)
    embed.main(type='gumtree')

## Full disclosure
It is important to address that having a third-party web crawl one's information is generally not allowed, high influxes of requests may result in access request suspension or ban.