from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json
import os
import time
import platform
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel

class SearchGumtree:
    def __init__(self, verbose=False):
        self.url = None
        self.new_url = None
        self.console = Console()
        self.verbose = verbose  # Verbose flag

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
            try:
                with open(filename, 'r') as file:
                    existing_data = json.load(file)
            except json.JSONDecodeError:
                self.console.log(f"Error reading JSON file: {filename}. Starting with an empty list.")
                existing_data = {'listings': []}
        else:
            existing_data = {'listings': []}

        existing_data['listings'].extend(data)

        with open(filename, 'w') as file:
            json.dump(existing_data, file, indent=4)
        self.console.log(f"Data appended to {filename}.")

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
            return []

    def print_header(self):
        type = platform.system().capitalize()
        header_text = f"Start {type} server instance 0.1.0"
        panel = Panel(header_text, title="RideRadarLite", title_align="left", border_style="bold cyan")
        self.console.print(panel)

    def main(self, vehicle_names_file, output_file):
        all_listings = []
        vehicle_names = []

        if not os.path.exists(vehicle_names_file):
            self.console.log(f"Vehicle names file does not exist: {vehicle_names_file}")
            return

        with open(vehicle_names_file, 'r') as file:
            vehicle_names = file.readlines()

        total_vehicles = len(vehicle_names)
        with Progress() as progress:
            task = progress.add_task("[cyan]Searching vehicles...", total=total_vehicles)

            for vehicle_name in vehicle_names:
                _vehicle_name = vehicle_name.strip()
                vehicle_name = vehicle_name.strip().lower().split()

                if len(vehicle_name) >= 2:
                    if vehicle_name[0] == 'bmw':
                        carmake = f"carmake-{vehicle_name[0]}"
                        carmodel = f"carmodel-{vehicle_name[0]}_{vehicle_name[1][0]}/variant-{vehicle_name[1][1:]}"
                        url = f"https://www.gumtree.com.au/s-cars-vans-utes/brisbane/{carmake}/{carmodel}/c18320l3005721?forsaleby=ownr&view=gallery"
                    else:
                        carmake = f"carmake-{vehicle_name[0]}"
                        carmodel = f"carmodel-{vehicle_name[0]}_{vehicle_name[1]}"
                        url = f"https://www.gumtree.com.au/s-cars-vans-utes/brisbane/{carmake}/{carmodel}/c18320l3005721?forsaleby=ownr&view=gallery"
                elif len(vehicle_name) == 1:
                    carmake = f"carmake-{vehicle_name[0]}"
                    url = f"https://www.gumtree.com.au/s-cars-vans-utes/brisbane/{carmake}/c18320l3005721?forsaleby=ownr&view=gallery"

                self.url = url
                html = self.fetch_html(url)
                aria_labels = self.extract_aria_labels(html)
                all_listings.extend(aria_labels)
                
                # Clear the previous output and print the new status
                if self.verbose:
                    self.console.print(f"[bold cyan]Pending:[/bold cyan] {_vehicle_name}")
                progress.update(task, advance=1)  # Update the progress bar

        if all_listings:
            self.append_to_json(all_listings, output_file)
        else:
            self.console.print("No listings found to save.")

if __name__ == "__main__":
    verbose = False  # Change this to False to disable verbose logging
    search = SearchGumtree(verbose=verbose)
    search.print_header()  # Print the header once
    while True:
        search.main(vehicle_names_file='list.txt', output_file='listings.json')
        print("Waiting for 6 hours before the next scrape...")
        time.sleep(21600)  # Sleep for 6 hours (21600 seconds)
