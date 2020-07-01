
from selectorlib import Extractor
import requests 
from time import sleep
import csv


# Function that collects all informations from the page linked from the url
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
    # Pass the HTML of the page and create the data
    return e.extract(r.text,base_url=url)


# Function to split the number of stars and the "Promoted" flag
def split_stars_promoted(orig_str):

    # Check (using the length of orig_str) if the str contains the title:
    # "Promoted This property spends a little extra to promote their visibility 
    #  on our site. It matches your search criteria and is a great choice for you."

    if len(orig_str)>100:

        stars_str = orig_str[:-148]
        pr_str = 'PROMOTED'
        return stars_str, pr_str

    else: # else return original string ('promotions' remains empty)
        return orig_str, ''





######################################################################


# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('booking.yml')

# Open 'urls.txt' as input file and 'data.csv' as output file
with open("urls.txt",'r') as urllist, open('data.csv','w') as outfile:
    
    # Define the names of all columns
    fieldnames = [
        
        "name",

        "location",
        "coords",
        "how_far",
        
        "stars", "promotion",  # given by the same css item
        "price",
        
        "price_for",
        "room_type",
        "beds",
        
        "breakfast",
        "cancellation",
        "checkin",
        "checkout",
        
        "rating_title",
        "rating",
        "number_of_ratings",
        #"url",
        #"map",
    ]

    # Build the 'data.csv' table
    writer = csv.DictWriter(outfile, fieldnames=fieldnames,quoting=csv.QUOTE_ALL)
    writer.writeheader()

    # For every url in the file...
    for url in urllist.readlines():

        # ...collect search results until the last page
        while (url!=None):

            # Collect and store data of the current page
            data = scrape(url)
            if data:

                # For every hotel ...
                for h in data['hotels']:

                    # Split stars and "promoted" flag
                    stars_str, pr_str = split_stars_promoted(h['stars'])
                    h['stars'] = stars_str
                    h['promotion'] = pr_str

                    # Remove text "Show on map" from the Location tag
                    h['location'] = h['location'][:-12]

                    # Store hotel informations on the csv file
                    writer.writerow(h)
            
            # Redefine url using the 'next_page' link
            url = data['next_page_link']

    print("\nScraped all pages!\n")