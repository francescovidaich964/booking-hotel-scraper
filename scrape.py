
##########################################
##### BOOKING SCRAPER (main program) #####
##########################################


from selectorlib import Extractor
import csv

# import functions defined in 'my_funcs.py'
import my_funcs


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
        checkin_date, checkout_date = my_funcs.retrieve_checkin_checkout(url)

        # ...collect search results until the last page
        while (url!=None):

            # Collect and store data of the current page
            data = my_funcs.scrape(url, e)
            if data:

                # For every hotel in the page:
                for h in data['hotels']:

                    # Split stars and "promoted" flag
                    stars_str, pr_str = my_funcs.split_stars_promoted(h['Stars'])
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