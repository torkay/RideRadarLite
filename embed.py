import json
import requests
import os

DISCORD_WEBHOOK_URL = {
    'gumtree': 'https://discord.com/api/webhooks/1270306540401721385/vlQ0e1UlLijiUfzcyjm0thU3EBR4M22o_NqSyGGNHSWsCqI17AstITnyscr_E6ad-a06',
    'facebook': 'https://discord.com/api/webhooks/1272899520916881410/K4YuW4FPiXBWj6Ht3Rb6sLj-zjB5G6j05oJ8igbHWXmmOYyTku0I5fbL9rqUn2kJ6_QT'
}

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

def send_discord_message(title, price, location, date, href, img_url, type):
    """Send a message to a Discord webhook."""
    # Adjust the embed structure according to Discord's API
    if type == 'gumtree':
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
            "footer": {
                "text": "RideRadarLite"
            },
            "timestamp": "2024-08-13T00:00:00Z"  # Replace with actual date if available
        }
        
        data = {
            "embeds": [embed]
        }
    elif type == 'facebook':
        embed = {
            "title": title,
            "description": f"**Price:** {price}\n**Location:** {location}\n**[View Listing]({href})**",
            "image": {
                "url": img_url
            },
            "author": {
            "name": "Facebook Worker",
            "url": "https://facebook.com",
            "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/2023_Facebook_icon.svg/1024px-2023_Facebook_icon.svg.png"
            },
            "footer": {
                "text": "RideRadarLite"
            },
            "timestamp": "2024-08-13T00:00:00Z"  # Replace with actual date if available
        }
        
        data = {
            "embeds": [embed]
        }
    
    webhook_url = DISCORD_WEBHOOK_URL.get(type)
    if not webhook_url:
        print(f"Invalid webhook URL for type: {type}")
        return
    
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print(f"Successfully sent message to Discord for: {title}")
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
        print(f"Response content: {response.content.decode()}")

def main(type='gumtree'):
    current_listings = load_json(f'./storage/{type}_listings.json')
    cached_listings = load_json(f'./storage/{type}_cached_listings.json')

    new_listings = [listing for listing in current_listings.get('listings', []) 
                    if listing not in cached_listings.get('listings', [])]

    # Send new listings to Discord
    if type == 'gumtree':
        for listing in new_listings:
            send_discord_message(
                title=listing.get('title', 'No title'),
                price=listing.get('price', 'No price'),
                location=listing.get('location', 'No location'),
                date=listing.get('date', 'No date'),
                href=listing.get('href', 'No link'),
                img_url=listing.get('img', 'No image'),
                type=type
            )
    elif type == 'facebook':
        for listing in new_listings:
            send_discord_message(
                title=listing.get('name', 'No name'),
                price=listing.get('price', 'No price'),
                location=listing.get('location', 'No location'),
                date=listing.get('title', 'No title'),
                href=listing.get('link', 'No link'),
                img_url=listing.get('image', 'No image'),
                type=type
            )
    # Save current listings as cached
    save_json(current_listings, f'./storage/{type}_cached_listings.json')

if __name__ == '__main__':
    for platform in ['gumtree', 'facebook']:
        main(type=platform)
