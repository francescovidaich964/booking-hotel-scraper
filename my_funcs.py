
#########################################
##### Functions for Booking scraper #####
#########################################

import requests 
from selectorlib import Extractor
import datetime



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
# and retuns them as 'datetime' objects
def retrieve_checkin_checkout(url):

    # Define list of strings to identify
    strings  = [ 'checkin_year=' , 'checkin_month=' , 'checkin_monthday=' , 
                 'checkout_year=', 'checkout_month=', 'checkout_monthday=' ]

    # Find position of the strings inside the url
    pos_str = [url.find(s) for s in strings]

    # If strings are not found (url.find() returns -1), the dates
    # are explicitly written as 'checkin' and 'checkout' in the url
    if pos_str[0] == -1:
        strings = ['checkin=', 'checkout=']
        pos_str = [url.find(s) for s in strings]



    """ NO URLS SHOULD CONTAINED THE DESIRED DATE WITH '%3D' (it is used for the history)
    # To take the position of the value, check if there a '=' char between
    # each string and their value or if it is encoded with its code '%3D'
    if url[ pos_str[0] + len(strings[0]) ]  ==  '=' :
        pos_values = [ (int(pos_str[i]) + len(strings[i]) + 1) for i in range(len(strings)) ]
    else: 
        pos_values = [ (int(pos_str[i]) + len(strings[i]) + 3) for i in range(len(strings)) ]
    """
    pos_values = [ (int(pos_str[i]) + len(strings[i])) for i in range(len(strings)) ]



    # Collect the value of each variable one char at time 
    # (don't stop at '-' if dates are written explicitly in the url)
    values = [''] * len(strings)
    len_values = [0] * len(strings)

    for i in range(len(strings)):
        current_pos = pos_values[i] 

        while url[current_pos].isdigit() or url[current_pos] == '-' :
            values[i] = values[i] + url[current_pos]
            len_values[i] += 1
            current_pos = pos_values[i] + len_values[i]

    # Build checkin and checkout dates from the values
    if len(strings) == 6:
        #checkin = '-'.join(values[:3])  # used when function returned the string
        #checkout = '-'.join(values[3:])
        checkin  = datetime.datetime(int(values[0]),int(values[1]),int(values[2]))
        checkout = datetime.datetime(int(values[3]),int(values[4]),int(values[5]))
    else:
        # checkin, checkout = values[:]
        checkin  = datetime.datetime.strptime(values[0], '%Y-%m-%d')
        checkout = datetime.datetime.strptime(values[1], '%Y-%m-%d')

    return checkin, checkout, pos_values, len_values



#####################################################################################


# Function that change the checkin and checkout values of the 
# original url of 'jump_days' days (uses positions and len of 
# the values extracted from the previous function)
def change_date(url, jump_days, checkin, checkout, pos_values, len_values):

    # Compute new checkin and checkout and convert them into strings
    new_checkin  = checkin  + datetime.timedelta(days=jump_days)
    new_checkout = checkout + datetime.timedelta(days=jump_days)

    # Convert datetimes into strngs and, if the url contains the values of Y-M-D 
    # written separately, split also the strings containing the new values.
    # Introduce also the ordering of appearence of this values in the url
    if len(pos_values) == 6:
        new_values = str(new_checkin)[:10].split('-') + str(new_checkout)[:10].split('-')
        ordering = [3,5,4,0,2,1]
    else:
        new_values = [str(new_checkin)[:10], str(new_checkout)[:10]]
        ordering = [1,0]

    # Reorder lists in order to change the url starting from its end
    # (this is useful because pos_values could change if new values have different len)
    new_values = [new_values[i] for i in ordering]
    pos_values = [pos_values[i] for i in ordering]
    len_values = [len_values[i] for i in ordering]

    # Inster each value in its corresponding place in the url
    for i in range(len(new_values)):

        url = url[ : pos_values[i]] + \
               new_values[i]        + \
              url[ pos_values[i]+len_values[i] : ]

    return url