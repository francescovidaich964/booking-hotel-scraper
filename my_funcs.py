
#########################################
##### Functions for Booking scraper #####
#########################################

import requests 
from selectorlib import Extractor



# Function that collects all informations from the page linked to the url
def scrape(url, e):    
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


######################################################################################


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


#####################################################################################


# Function that extract check-in and check-out from the url
def retrieve_checkin_checkout(url):

    # Define list of strings to identify
    #strings  = [ 'checkin_monthday' , 'checkin_month' , 'checkin_year' , 
    #             'checkout_monthday', 'checkout_month', 'checkout_year' ]
    strings  = [ 'checkin_year' , 'checkin_month' , 'checkin_monthday' , 
                 'checkout_year', 'checkout_month', 'checkout_monthday' ]

    # Find position of the strings inside the url
    pos_str = [url.find(s) for s in strings]

    # If strings are not found (url.find() returns -1), the dates
    # are explicitly written as 'checkin' and 'checkout'
    if pos_str[0] == -1:
        strings = ['checkin', 'checkout']
        pos_str = [url.find(s) for s in strings]


    # Check if there a '=' char between each string and their value or if
    # it is encoded with its code '%3D' to take the position of the value
    if url[ pos_str[0] + len(strings[0]) ]  ==  '=' :
        pos_values = [ (int(pos_str[i]) + len(strings[i]) + 1) for i in range(len(strings)) ]
    else: 
        pos_values = [ (int(pos_str[i]) + len(strings[i]) + 3) for i in range(len(strings)) ]

    # Collect the value of each variable one char at time 
    # (don't stop at '-' if dates are written explicitly in the url)
    values = [''] * len(strings)
    for i in range(len(strings)):
        while url[pos_values[i]].isdigit() or url[pos_values[i]]== '-':
            values[i] = values[i] + url[pos_values[i]]
            pos_values[i] += 1

    # Build checkin and checkout dates from the values
    if len(strings) == 6:
        checkin = '-'.join(values[:3])
        checkout = '-'.join(values[3:])
    else:
        checkin, checkout = values[:]

    return checkin, checkout
