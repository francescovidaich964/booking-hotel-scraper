
from selectorlib import Extractor
import requests 
from time import sleep
import csv


# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('booking.yml')


# Function that collects all informations from the url
def scrape(url):    
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        # You may want to change the user agent if you get blocked
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',

        'Referer': 'https://www.booking.com/index.en-gb.html',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    # Download the page using requests
    print("\nDownloading %s"%url)
    r = requests.get(url, headers=headers)
    # Pass the HTML of the page and create 
    return e.extract(r.text,base_url=url)




# Open 'urls.txt' as input file and 'data.csv' as output file
with open("urls.txt",'r') as urllist, open('data.csv','w') as outfile:
    
    # Define the names of all columns
    fieldnames = [
        "name",
        "location",
        "price",
        "price_for",
        "room_type",
        "beds",
        "rating",
        "rating_title",
        "number_of_ratings",
        "url"
    ]

    # Build the 'data.csv' table
    writer = csv.DictWriter(outfile, fieldnames=fieldnames,quoting=csv.QUOTE_ALL)
    writer.writeheader()

    # For every url in the file...
    for url in urllist.readlines():

        # ...collect search results until the last page
        while (url!=None):

            # Collect and write data of the current page
            data = scrape(url) 
            if data:
                for h in data['hotels']:
                    writer.writerow(h)
            
            # Redefine url using the 'next_page' link
            url = data['next_page_link']