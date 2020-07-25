
##########################################
##### BOOKING SCRAPER (main program) #####
##########################################


from selectorlib import Extractor
import csv
import datetime

# import functions defined in 'my_funcs.py'
import my_funcs



# SET PARAMETERS to permorm the research for more dates
n_estraz = 1    # num estrazioni (es: una per settimana)
jump_days = 7   # giorni da aggiungere ad ogni estrazione




# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('booking.yml')

# Open 'urls.txt' as input file and 'data.csv' as output file
with open("urls.txt",'r') as urllist, open('data.csv','w') as outfile:
    
    # Define the names of all columns
    fieldnames = [
        
        "Name",
        "Id",
        
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
    for init_url in urllist.read().splitlines():


        # ...perform the research for 'n_estraz' dates and...
        for i in range(n_estraz+1):

            # From the url, extract checkin, checkout, the positions of their
            # values inside the url and the number of chars that each value takes 
            # (equal for each page of the same search)
            checkin, checkout, pos_values, len_values = my_funcs.retrieve_checkin_checkout(init_url)
            
            # we want to store starting url  ->  'url' is the variable that will be modified
            url = init_url


            # ...collect search results of every page until the last one
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
                        # (Convert 'datatime' in a string format)
                        h['Checkin']  = str(checkin)[:10]
                        h['Checkout'] = str(checkout)[:10]

                        # Store hotel informations on the csv file
                        writer.writerow(h)
                
                # Redefine url using the 'next_page' link
                url = data['next_page_link']


            # When the current search results are collected,
            # change the date inside the url and repeat process 
            # for 'n_estraz' times
            init_url = my_funcs.change_date(init_url, jump_days, checkin, checkout, pos_values, len_values)


    print("\nScraped all pages!\n")