from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json
import os
import time
import platform
import re
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel
import threading

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
            """Extract and parse aria-label attributes from <a> tags."""
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', attrs={'aria-label': True})
            
            listings = []
            for link in links:
                aria_label = link.get('aria-label')
                href = "https://www.gumtree.com.au" + link.get('href')

                # Find the img element within the current link
                img = link.find('img', class_='carousel__image image image--is-visible')
                img_src = img.get('src') if img else 'N/A'
                
                # Regular expression patterns
                title_pattern = r"^(.*?)(?:\.\n)"
                price_pattern = r"Price:\s*(.*?)\s*\.\n"
                location_pattern = r"Location:\s*(.*?)\s*\.\n"
                date_pattern = r"Ad listed\s*(\d{2}/\d{2}/\d{4})\."

                # Extracting details
                title_match = re.search(title_pattern, aria_label)
                price_match = re.search(price_pattern, aria_label)
                location_match = re.search(location_pattern, aria_label)
                date_match = re.search(date_pattern, aria_label)

                # Parse results
                title = title_match.group(1).strip() if title_match else 'N/A'
                price = price_match.group(1).strip() if price_match else 'N/A'
                location = location_match.group(1).strip() if location_match else 'N/A'
                date = date_match.group(1).strip() if date_match else 'N/A'

                listings.append({
                    'title': title,
                    'price': price,
                    'location': location,
                    'date': date,
                    'href': href,
                    'img': img_src
                })
            
            return listings
        else:
            return []

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
            task = progress.add_task("[cyan]Searching gumtree...", total=total_vehicles)

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

class SearchFacebook:
    def __init__(self, verbose=False):
        self.console = Console()
        self.verbose = verbose  # Verbose flag
        self.word_file = "list.txt"  # File containing search terms
        self.output_file = "./storage/facebook_listings.json"  # Output JSON file
        self.facebook_cached_listings_file = "./storage/facebook_cached_listings.json"  # Cached file for comparison
        self.max_retries = 3  # Number of retries for fetching data
        self.retry_delay = 5  # Delay between retries in seconds
        self.car_parts_filter = [
            'taillights', 'rims', 'hotwheels', 'toy', 'headlights', 'bumper',
            'grill', 'fender', 'side skirts', 'spoiler', 'exhaust', 'air intake',
            'brake pads', 'shocks', 'struts', 'suspension', 'battery', 'alternator',
            'starter', 'radiator', 'transmission', 'engine', 'wheel bearing',
            'clutch', 'driveshaft', 'CV joint', 'muffler', 'catalytic converter',
            'fuel pump', 'oil filter', 'air filter', 'spark plugs', 'serpentine belt',
            'timing belt', 'window regulator', 'door handle', 'mirror', 'headliner',
            'floor mats', 'seat covers', 'steering wheel cover', 'shift knob',
            'car cover', 'car alarm', 'sound system', 'GPS', 'dash cam', 'wiper blades',
            'hydraulics', 'roll cage'
        ]

    def construct_url(self, word):
        self._word = word
        word = word.split()
        base_url = "https://www.facebook.com/marketplace/brisbane/search?query="
        if len(word) == 1:
            return f"{base_url}{word[0]}"
        elif len(word) == 2:
            return f"{base_url}{word[0]}%20{word[1]}"
        else:
            raise ValueError("Input should be a list with 1 or 2 words")

    def extract_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        parsed = []
        listings = soup.find_all('div', class_='x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24')

        for listing in listings:
            try:
                # Extract image URL
                image = listing.find('img', class_='xt7dq6l xl1xv1r x6ikm8r x10wlt62 xh8yej3')
                image = image['src'] if image else 'No image'

                # Extract title
                title = listing.find('span', class_='x1lliihq x6ikm8r x10wlt62 x1n2onr6')
                title = title.text if title else None

                # Skip listing if title includes any part from the filter list
                if title and any(part.lower() in title.lower() for part in self.car_parts_filter):
                    continue

                # Skip listing if title does not contain the exact phrase from self._word
                if self._word.lower() not in title.lower():
                    continue

                # Extract price
                price = listing.find('span', class_='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 x1s688f xzsf02u')
                price = price.text if price else 'No price'

                # Extract URL 
                post_url = listing.find('a', class_='x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1sur9pj xkrqix3 x1lku1pv')
                post_url = f"https://facebook.com{post_url['href']}" if post_url else None

                # Extract location
                location = listing.find('span', class_='x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft x1j85h84')
                location = location.text if location else 'No location'

                # Only append to results if both title and URL are present
                if title and post_url:
                    parsed.append({
                        'image': image,
                        'title': title,
                        'price': price,
                        'post_url': post_url,
                        'location': location
                    })
            except Exception as e:
                pass

        result = []
        for item in parsed:
            result.append({
                'name': item['title'],
                'price': item['price'],
                'location': item['location'],
                'title': item['title'],
                'image': item['image'],
                'link': item['post_url']
            })
        return result

    def fetch_html(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            )
            page = context.new_page()
            for attempt in range(self.max_retries):
                try:
                    page.goto(url)
                    page.wait_for_selector('body', timeout=10000)
                    for _ in range(5):
                        page.keyboard.press('End')
                        time.sleep(2)
                    content = page.content()
                    return content
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed with error: {e}")
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay * (2 ** attempt)
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        print("All retry attempts failed.")
                        return ""
                finally:
                    browser.close()

    def append_to_json(self, data, filename):
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

    def compare_and_update(self, new_data, cached_file, output_file):
        if os.path.exists(cached_file):
            with open(cached_file, 'r') as file:
                cached_data = json.load(file)
        else:
            cached_data = {'listings': []}

        existing_links = {listing['link'] for listing in cached_data['listings']}
        new_listings = [listing for listing in new_data if listing['link'] not in existing_links]

        if new_listings:
            self.append_to_json(new_listings, output_file)
            with open(cached_file, 'w') as file:
                json.dump({'listings': new_data}, file, indent=4)

    def main(self):
        with open(self.word_file, 'r') as file:
            vehicle_names = file.readlines()
        total_vehicles = len(vehicle_names)
        all_data = []  # Accumulate all data here

        with Progress() as progress:
            task = progress.add_task("[cyan]Searching facebook marketplace...", total=total_vehicles)

            for word in vehicle_names:
                word = word.strip()
                url = self.construct_url(word)

                page_content = self.fetch_html(url)
                if page_content:
                    extracted_data = self.extract_data(page_content)
                    if extracted_data:
                        all_data.extend(extracted_data)  # Collect data from all searches
                    else:
                        pass
                else:
                    self.console.log(f"Failed to fetch HTML for: {word}")

                progress.update(task, description=f"[cyan]Searching facebook marketplace...", completed=len(all_data))

            if all_data:
                self.compare_and_update(all_data, self.facebook_cached_listings_file, self.output_file)
                self.console.log(f"Data appended successfully.")
            else:
                self.console.log(f"No data to append.")