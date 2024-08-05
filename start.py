from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json
import os
import time

class SearchGumtree:
    def __init__(self):
        self.url = None
        self.new_url = None

    def fetch_html(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            )
            page = context.new_page()
            page.goto(url)
            self.new_url = page.url
            page.wait_for_selector('body', timeout=10000)  # Adjust the timeout as needed
            content = page.content()
            browser.close()
            return content

    def append_to_json(self, data, filename):
        """Append data to a JSON file."""
        if os.path.exists(filename):
            # Read existing data
            try:
                with open(filename, 'r') as file:
                    existing_data = json.load(file)
            except json.JSONDecodeError:
                # Handle case where the file is empty or corrupted
                print(f"Error reading JSON file: {filename}. Starting with an empty list.")
                existing_data = {'listings': []}
        else:
            existing_data = {'listings': []}

        # Append new data
        existing_data['listings'].extend(data)

        # Write updated data back to the file
        with open(filename, 'w') as file:
            json.dump(existing_data, file, indent=4)
        print(f"Data appended to {filename}.")

    def extract_aria_labels(self, html):
        if self.url == self.new_url:
            """Extract aria-label attributes from <a> tags."""
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', attrs={'aria-label': True})
            return [
                {
                    'aria-label': link.get('aria-label'),
                    'href': "https://www.gumtree.com.au" + link.get('href')  # Assuming href is a relative URL
                }
                for link in links
            ]
        else:
            print(f"URL mismatch: {self.url} != {self.new_url}")
            print("No vehicles found.")
            return []

    def main(self, vehicle_names_file, output_file):
        all_listings = []

        if not os.path.exists(vehicle_names_file):
            print(f"Vehicle names file does not exist: {vehicle_names_file}")
            return

        with open(vehicle_names_file, 'r') as file:
            vehicle_names = file.readlines()

        for vehicle_name in vehicle_names:
            vehicle_name = vehicle_name.strip().lower().split()
            
            # Construct the URL
            if vehicle_name[0] == 'bmw':
                carmake = f"carmake-{vehicle_name[0]}"
                carmodel = f"carmodel-{vehicle_name[0]}_{vehicle_name[1][0]}/variant-{vehicle_name[1][1:]}"
                url = f"https://www.gumtree.com.au/s-cars-vans-utes/brisbane/{carmake}/{carmodel}/c18320l3005721?forsaleby=ownr&view=gallery"
            else:
                carmake = f"carmake-{vehicle_name[0]}"
                carmodel = f"carmodel-{vehicle_name[0]}_{vehicle_name[1]}"
                url = f"https://www.gumtree.com.au/s-cars-vans-utes/brisbane/{carmake}/{carmodel}/c18320l3005721?forsaleby=ownr&view=gallery"
            
            self.url = url
            html = self.fetch_html(url)
            aria_labels = self.extract_aria_labels(html)
            all_listings.extend(aria_labels)
            print(f'Processed: {url}')

        # Save the data to a JSON file
        if all_listings:
            self.append_to_json(all_listings, output_file)
        else:
            print("No listings found to save.")

if __name__ == "__main__":
    search = SearchGumtree()
    while True:
        search.main(vehicle_names_file='list.txt', output_file='listings.json')
        print("Waiting for 6 hours before the next scrape...")
        time.sleep(21600)  # Sleep for 6 hours (21600 seconds)
