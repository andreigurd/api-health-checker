import requests
import os
from datetime import datetime, timedelta, timezone, date
import json
from tabulate import tabulate
import time
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError
from urllib.parse import urlparse


#-------------------------------------------------------------------------------------------------------------

def datetime_now_stamp():    
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d %H:%M:%S")
    return date_string

#-------------------------------------------------------------------------------------------------------------
def get_api_name(url):        
    
    # from urllib.parse import urlparse and parsed = urlparse(url) breaks url into components
    # .netloc is network location
    # .hostname is up to example.com
    
    parsed_url = urlparse(url)
    domain = parsed_url.hostname

    # .split into two pieces. 0 and -1. [-1] keeps the last piece

    api_name = domain.split(".")[0]
    return api_name.capitalize()

#-------------------------------------------------------------------------------------------------------------
def check_api(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            request_start = time.time()
        
            # Make the request
            response = requests.get(url, timeout=5)
            elapsed_time = (time.time()- request_start) * 1000           
            
            # Check if successful

            # just checking api, no json needed
            if response.status_code == 200:
                # note 1000* sec = ms
                return f'{elapsed_time:.0f}ms'

            # invalid json response.
            if response.status_code == 401:
                print(f"Unauthorized. Key not set or invalid.")
                return "Invalid Key" 
            elif response.status_code == 404:
                print(f"404 Not found.")
                return "Not Found"
            elif response.status_code == 429:
                print(f"Rate limit exceeded.")
                return "Rate Limit Exceeded"
            # not effective to retry 400 codes because status will not change

            elif response.status_code == 500:
                print(f"Server has encountered an unexpected error. Please try again later.")
                return "Server Error"
            else:
                print(f"Error: {response.status_code}")
                return "Unknown Error"
        except ConnectionError:
            print(f"Connection error on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                print("Cannot connect to server. Check your internet connection.")
                return "Server Error"
        
        except Timeout:
            print(f"Timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
            else:
                print("Request timed out after all retries")
                return "Timeout"

        except RequestException as e:
                    return "Request Failed"
        
    

#-------------------------------------------------------------------------------------------------------------
def main():    
    """Main program loop"""

    api_list=[]

    print( "Welcome to API Health Checker")
    print(f"{'='*30}\n")
    
    while True:        
        
        url = input("Enter API endpoint (or 'done'):\n")
        if url == "":
            print("Input cannot be blank. Try again.")
            continue
        elif url.lower()=="done":
            break
        

        api_list.append(url)
        
    print("\nChecking API endpoints\n")

    # loop through each api and get api name and run a check

    results =[]
    healthy = 0

    for url_item in api_list:
        # note api_list is just url strings, no key and values
        api_name = get_api_name(url_item)
        result = check_api(url_item)
        result_dict={
            "name":api_name,
            "result":result
        }
        # note sum() to get total healthy results is complicated. do +1 instead.
        if result and "ms" in result: #and avoids "none"
            healthy+= 1        

        results.append(result_dict)

    # print summary
    header = f'API Health Check - {datetime_now_stamp()}'
    print(header)
    print('='*len(header))

    for item in results:
        print(f'{item["name"]:<16} {item["result"]}')
        
    print(f"\nSummary: {healthy}/{len(api_list)} API's healthy.")
    
    # save to log file
    with open('api_health_log.txt', 'a') as file:
        file.write(f'{header}\n')
        file.write('='*len(header))
        file.write("")

        for item in results:
            file.write(f'{item["name"]:<16} {item["result"]}')

        file.write(f"\nSummary: {healthy}/{len(api_list)} APIs healthy")


#-------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

