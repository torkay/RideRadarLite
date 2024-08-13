import time
from engine import SearchGumtree, SearchFacebook
import embed
import platform
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel

def print_header(console):
        type = platform.system().capitalize()
        header_text = f"Start {type} server instance 0.1.0"
        panel = Panel(header_text, title="RideRadarLite", title_align="left", border_style="bold cyan")
        console.print(panel)

if __name__ == "__main__":
    verbose = False  # Change this to False to disable verbose logging

    # Initialize both search classes
    search_gumtree = SearchGumtree(verbose=verbose)
    search_facebook = SearchFacebook(verbose=verbose)

    # Print header
    print_header(Console())

    while True:
        search_gumtree.main(vehicle_names_file='list.txt', output_file='./storage/listings_gumtree.json')
        embed.main(type='gumtree')

        search_facebook.main()
        embed.main(type='facebook')

        print("Waiting for 6 hours before the next scrape...")
        time.sleep(21600)  # Sleep for 6 hours (21600 seconds)
