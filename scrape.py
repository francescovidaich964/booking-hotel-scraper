
from selectorlib import Extractor
import requests 
from time import sleep
import csv

import numpy as np
from datetime import datetime


# Function that collects all informations from the page linked to the url
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
    print("\nDownloading:\n%s"%url)
    r = requests.get(url, headers=headers)
    # Pass the HTML of the page and create the data
    return e.extract(r.text,base_url=url)



# Function to split the number of stars and the "Promoted" flag
def split_stars_promoted(orig_str):

    # Check (using the length of orig_str) if the str contains the title:
    #   "Promoted This property spends a little extra to promote their visibility 
    #    on our site. It matches your search criteria and is a great choice for you."

    if len(orig_str)>100:

        stars_str = orig_str[:-148]
        pr_str = 'PROMOTED'
        return stars_str, pr_str

    else: # else return original string ('promotions' remains empty)
        return orig_str, ''



# Function that extract check-in and check-out from the url
def retrieve_checkin_checkout(url):

    # Define list of strings to identify
    strings  = [ 'checkin_monthday' , 'checkin_month' , 'checkin_year' , 
                 'checkout_monthday', 'checkout_month', 'checkout_year' ]

    # Find position of the strings inside the url
    pos_str = [url.find(s) for s in strings]

    # Check if there a '=' char between each string and their value or if
    # it is encoded with its code '%3D' to take the position of the value
    if url[ pos_str[0] + len(strings[0]) ]  ==  '=' :
        pos_values = [ (int(pos_str[i]) + len(strings[i]) + 1) for i in range(6) ]
    else: 
        pos_values = [ (int(pos_str[i]) + len(strings[i]) + 3) for i in range(6) ]

    # Collect the value of each variable one char at time
    values = ['']*6
    for i in range(6):
        while url[pos_values[i]].isdigit():
            values[i] = values[i] + url[pos_values[i]]
            pos_values[i] += 1

    # Build checkin and checkout dates
    checkin = ' / '.join(values[:3])
    checkout = ' / '.join(values[3:])

    return checkin, checkout






######################################################################



# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('booking.yml')

# Open 'urls.txt' as input file and 'data.csv' as output file
with open("urls.txt",'r') as urllist, open('data.csv','w') as outfile:
    
    # Define the names of all columns
    fieldnames = [
        
        "Name",

        "Location",
        "Coords",
        "How_far",
        
        "Stars", "Promotion",  # given by the same css item
        "Price",
        
        "Price_for",
        "Room_type",
        "Beds",
        
        "Breakfast",
        "Cancellation",
        "Checkin",
        "Checkout",
        
        "Rating_title",
        "Rating",
        "Number_of_ratings",
        #"url",
        #"map",
    ]

    # Build the 'data.csv' table
    writer = csv.DictWriter(outfile, fieldnames=fieldnames,quoting=csv.QUOTE_ALL)
    writer.writeheader()

    # For every url in the file...
    for url in urllist.read().splitlines():

        # Extract checkin and checkout dates from the url 
        # (equal for each page of the same search)
        checkin_date, checkout_date = retrieve_checkin_checkout(url)

        # ...collect search results until the last page
        while (url!=None):

            # Collect and store data of the current page
            data = scrape(url)
            if data:

                # For every hotel in the page:
                for h in data['hotels']:

                    # Split stars and "promoted" flag
                    stars_str, pr_str = split_stars_promoted(h['Stars'])
                    h['Stars'] = stars_str
                    h['Promotion'] = pr_str

                    # Remove text "Show on map" from the Location tag
                    h['Location'] = h['Location'][:-12]

                    # Add checkin and checkout to the 'data' table
                    h['Checkin'] = checkin_date
                    h['Checkout'] = checkout_date

                    # Store hotel informations on the csv file
                    writer.writerow(h)
            
            # Redefine url using the 'next_page' link
            url = data['next_page_link']

    print("\nScraped all pages!\n")