import csv
import requests
import json
import os
import time, datetime
import argparse
from bs4 import BeautifulSoup
import pandas as pd
import wikipediaapi, praw
from mastodon import Mastodon

def load_credentials(filepath='credentials.txt'):
    """
    Load credentials from a file containing key-value pairs.
    """
    credentials = {}
    with open(filepath, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            credentials[key] = value
    return credentials

# F01
def getGoogleSearchMetrics(app_name, app_package, credentials):
    # Extract required credentials
    api_key = credentials.get('google_api_key')
    search_engine_id = credentials.get('google_cse_id')
    
    if not api_key or not search_engine_id:
        raise ValueError("Missing Google API Key or Custom Search Engine ID in credentials")
    
    # Construct the search query
    query = f"{app_name}"
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": search_engine_id
    }
    
    try:
        # Send the GET request to the Google Custom Search API
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_results = response.json()
        
        # Extract the number of search results
        total_results = int(search_results.get("searchInformation", {}).get("totalResults", 0))
        
        # Store the feature in the dictionary
        return total_results
    
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching Google Search results: {e}")
        return None  # Assign None if there is an error

# F02, F03, F04
def getWikipediaMetrics(app_name, app_package, credentials):
    wiki_lang = 'en'  # Language of Wikipedia to use, e.g., English Wikipedia
    wiki = wikipediaapi.Wikipedia(user_agent='GESSI NLP4SE (joaquim.motger@upc.edu)', language=wiki_lang)
    
    # Fetch the Wikipedia page for the given app name
    page = wiki.page(app_name)

    if not page.exists():
        return '-', '-', '-'
    
    # Define the URL for the Wikipedia API
    url = f"https://en.wikipedia.org/w/api.php"
    
    # Parameters for the API request
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "titles": app_name,
        "rvprop": "ids",
        "rvlimit": "max"  # Fetches maximum revisions per request
    }

    revisions = '-'
    try:
        # Make the API request
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Extract the page information
        pages = data.get("query", {}).get("pages", {})
        for key in pages:
            revisions = len(pages[key]['revisions'])
    except requests.RequestException as e:
        print(f"Error fetching edits for '{page_title}': {e}")

    # F_02: Number of Edits on Wikipedia Page
    f_02 = revisions

    # F_03: Number of links to the Wikipedia page
    f_03 = len(page.backlinks) if hasattr(page, 'backlinks') else 0

    # F_04: Number of links from the Wikipedia page
    f_04 = len(page.links)

    return f_02, f_03, f_04

# F05
def getRedditMetrics(app_name, app_package, credentials):
    base_url = "https://api.pushshift.io/reddit"
    mention_count = 0

    # Extract the Bearer token from credentials
    headers = {
        "Authorization": f"Bearer {credentials['reddit_bearer_token']}"
    }

    def fetch_data(endpoint, query, size=500):
       
        last_timestamp = None
        total_mentions = 0

        while True:
            params = {
                "q": query,
                "size": size,
            }
            if last_timestamp:
                params["before"] = last_timestamp

            response = requests.get(f"{base_url}/{endpoint}", params=params, headers=headers)
            if response.status_code == 200:
                data = response.json().get('data', [])
                print(data)
                if not data:
                    break  # Exit loop when no more data is available

                total_mentions += len(data)
                last_timestamp = data[-1]['created_utc']  # Use the timestamp of the last item for pagination
            else:
                print(f"Error fetching data from {endpoint}: {response.status_code} {response.content}")
                break

            time.sleep(5)

        return total_mentions

    try:
        # Fetch mentions in posts
        mention_count += fetch_data("search/submission", app_name)

        # Fetch mentions in comments
        mention_count += fetch_data("search/comment", app_name)

    except Exception as e:
        print(f"An error occurred while fetching data from Pushshift: {e}")
        return -1  # Return -1 in case of an error

    return mention_count

#F06
def getMastodonMetrics(app_name, app_package, credentials):
    # Ensure required credentials are available
    api_base_url = credentials.get("mastodon_api_base_url")
    access_token = credentials.get("mastodon_access_token")
    if not api_base_url or not access_token:
        raise ValueError("Missing 'api_base_url' or 'access_token' in credentials.")

    # Initialize the Mastodon client
    mastodon = Mastodon(
        api_base_url=api_base_url,
        access_token=access_token
    )
    
    mentions_count = 0
    try:
        # Pagination setup
        query = f'"{app_name}"'
        max_limit_per_request = 40  # Mastodon API limit per request
        search_results = mastodon.search_v2(query, search_type='statuses', limit=max_limit_per_request)
        statuses = search_results.get("statuses", [])
        mentions_count += len(statuses)
        
        # Retrieve next pages
        while 'next' in search_results and mentions_count < max_results:
            time.sleep(1)  # To avoid hitting rate limits
            search_results = mastodon.fetch_next(search_results)
            statuses = search_results.get("statuses", [])
            mentions_count += len(statuses)
            if mentions_count >= max_results:
                break
        
        return min(mentions_count, max_results)
    
    except Exception as e:
        print(f"Error collecting mentions for {app_name}: {e}")
        return mentions_count

def process_app_features(app_name, app_package, credentials):
    features = {}

    # F01 #TODO get API key
    features['F_01'] = getGoogleSearchMetrics(app_name, app_package, credentials)

    # F02, F03, F04
    features['F_02'], features['F_03'], features['F_04'] = getWikipediaMetrics(app_name, app_package, credentials)

    # F05 #TODO overcome API limits (requires pagination)
    # features['F_05'] = getRedditMetrics(app_name, app_package, credentials)

    # F06
    features['F_06'] = getMastodonMetrics(app_name, app_package, credentials)

    # F07
    # ...

    # F08
    # ...

    # F09
    # ...

    # F10
    # ...

    # F11
    # ...

    # F12
    # ...

    # F13
    # ...

    # F14
    # ...

    # F15
    # ...

    # F16
    # ...

    # F17
    # ...

    # F18
    # ...

    # F19
    # ...

    # F20
    # ...

    # F21
    # ...

    # F22
    # ...

    # F23
    # ...

    # F24
    # ...

    # F25
    # ...

    # F26
    # ...

    # F27
    # ...

    # F28
    # ...

    # F29
    # ...

    # F30
    # ...

    # F31
    # ...

    # F32
    # ...

    # F33
    # ...

    # F34
    # ...

    # F35
    # ...

    # F36
    # ...

    # F37
    # ...

    # F38
    # ...

    # F39
    # ...

    # F40
    # ...

    # F41
    # ...

    # F42
    # ...

    # F43
    # ...

    # F44
    # ...

    # F45
    # ...

    # F46
    # ...

    # F47
    # ...

    # F48
    # ...

    # F49
    # ...

    # F50
    # ...


    return features

def main(input_csv, output_csv):

    credentials = load_credentials()
    # Read the input CSV
    input_data = pd.read_csv(input_csv)
    # Output data
    output_data = input_data.copy()
    # Process each app in the input
    for index, row in input_data.iterrows():
        app_name = row['app_name']
        app_package = row['package']
        print(f"Processing app: {app_name} ({app_package})")
        features = process_app_features(app_name, app_package, credentials)
        # Append features to the row in the output data
        for feature_key, feature_value in features.items():
            output_data.at[index, feature_key] = feature_value
        time.sleep(1)  # Adding delay to avoid being blocked by web services
    # Write the output CSV
    output_data.to_csv(output_csv, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process app features from input CSV and output results to a new CSV.")
    parser.add_argument('input_csv', type=str, help='Path to the input CSV file')
    parser.add_argument('output_csv', type=str, help='Path to the output CSV file')
    args = parser.parse_args()
    main(args.input_csv, args.output_csv)
