import json
import requests
import os

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1270306540401721385/vlQ0e1UlLijiUfzcyjm0thU3EBR4M22o_NqSyGGNHSWsCqI17AstITnyscr_E6ad-a06'

def load_json(filename):
    """Load JSON data from a file."""
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {"listings": []}

def save_json(data, filename):
    """Save JSON data to a file."""
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def send_discord_message(title, price, location, date, href, img_url):
    """Send a message to a Discord webhook."""
    embed = {
        "title": title,
        "description": f"**Price:** {price}\n**Location:** {location}\n**Date:** {date}\n**[View Listing]({href})**",
        "image": {
            "url": img_url
        },
        "author": {
            "name": "Gumtree Worker",
            "url": "https://gumtree.com.au",
            "icon_url": "https://s3-eu-west-1.amazonaws.com/tpd/logos/4859ad6d000064000502bbb2/0x0.png"
        },
        
    }
    data = {
        "embeds": [embed]
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print(f"Successfully sent message to Discord for: {title}")
    else:
        print(f"Failed to send message. Status code: {response.status_code}")

def main():
    current_listings = load_json('./storage/listings.json')
    cached_listings = load_json('./storage/cached_listings.json')

    new_listings = [listing for listing in current_listings.get('listings', []) 
                    if listing not in cached_listings.get('listings', [])]

    # Send new listings to Discord
    for listing in new_listings:
        send_discord_message(
            title=listing.get('title', 'No title'),
            price=listing.get('price', 'No price'),
            location=listing.get('location', 'No location'),
            date=listing.get('date', 'No date'),
            href=listing.get('href', 'No link'),
            img_url=listing.get('img', 'No image')  # Added image URL
        )

    # Save current listings as cached
    save_json(current_listings, './storage/cached_listings.json')

if __name__ == '__main__':
    main()
