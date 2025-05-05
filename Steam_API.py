"""
Script to collect Steam user reviews using the public API.
Implements pagination, cursor trap detection, checkpointing, and error retries.
Target: Assassin's Creed Shadows (App ID: 3159330)
Output: CSV with structured review data for sentiment analysis.
"""

# ---------------------
#     IMPORT LIBRARIES
# ---------------------
import requests
import pandas as pd
import time
import os
from datetime import datetime


# ---------------------
#     LINK AND GAME NAME
# ---------------------
game_name = "AC_Shadows" # the file names
app_id = "3159330" # app id of Assassin's Creed Shadows
url = f"https://store.steampowered.com/appreviews/{app_id}?json=1" # DO NOT CHANGE



# ---------------------
#     CONFIGURATION 
# ---------------------
checkpoint_file = f'{game_name}_checkpoint.csv'
final_output = f'{game_name}_sentiment_final.csv'
max_reviews = 20000
checkpoint_interval = 50
backoff_limit = 5
max_retries = 3
day_ranges = [7, 30, 90, 180, 365, 9999]
filters = ["recent","updated","all"]

# ---------------------
#     LOAD CHECKPOINT 
# ---------------------
# Since the steam API have unique behavior, I decide to Implemented checkpointing to prevent data loss due to connection interruptions.
if os.path.exists(checkpoint_file):
    df_checkpoint = pd.read_csv(checkpoint_file)
    reviews = df_checkpoint.to_dict("records")
    review_ids = set(df_checkpoint['review_id'].astype(str))
    print(f"Loaded checkpoint with {len(reviews)} reviews.")
else:
    reviews = []
    review_ids = set()


# ---------------------
#     API PULL LOOP 
# ---------------------
# steam API use cursor for its request, it will give =the cursor 'link' for next batch of data
cursor = "*"
prev_cursor = None
same_cursor_count = 0
backoff_counter = 0

# request API based on the ranges of days
for day_range in day_ranges:
    # request API based on the filters
    for filter_type in filters:
        # print for easy track during progress
        print(f"\n Request with day_range={day_range}, filter='{filter_type}'")
        # request Loop
        while True:
            # this is a safeguard for failure of request, due to connection or limit issue
            # if it tries as set attempts and failed it will stop
            for attempt in range(max_retries):
                # this is the request of API with set parameters
                try:
                    response = requests.get(
                        url,
                        params={
                            "cursor": cursor, # cursor * means the first page of reviews, steam will return the next batch automatically
                            "json": 1, # get the request in json format
                            "num_per_page": 50, # how many reviews per batch
                            "day_range": day_range, # this will looped based on list above
                            "filter": filter_type # this will looped based on list above
                        },
                        # timeout limit, if the server didn't respond during this period means raise an exception
                        timeout=10 
                    )
                    # if response success break, if not print the error status code
                    if response.status_code == 200:
                        break
                    else:
                        print(f"API Error {response.status_code}. Retrying...")
                
                # track the failure code for easy debugging later
                except Exception as e:
                    print(f"Request failed: {e}. Retrying...")
                time.sleep(2 + attempt)
            
            # if max retry reach, then close the process
            else:
                print("Max retries reached. Exiting.")
                break
            
            data = response.json()

            # this logic is to check if steam return an empty review
            if "reviews" not in data or not data["reviews"]:
                print("No more reviews found.")
                break
            
            # this logic is to get the data itself, it start with checking the unique ID,
            # skip if the ID is exist, add any new data, track how many data we have and how many new so far.
            new_count = 0
            for review in data["reviews"]:
                # every review have unique ID, this logic is converting it to string
                # then check it in review_ids. If the data unique id is exist, then it will be skipped
                review_id = str(review.get("recommendationid"))
                if review_id in review_ids:
                    continue
                
                # data perimeter that we will request the API
                review_data = {
                    "review_id": review_id,
                    "review_text": review.get("review"),
                    "votes_up": review.get("votes_up"),
                    "votes_funny": review.get("votes_funny"),
                    "comment_count": review.get("comment_count"),
                    "author_steamid": review.get("author", {}).get("steamid"),
                    "author_playtime_forever": review.get("author", {}).get("playtime_forever"),
                    "author_playtime_last_2weeks": review.get("author", {}).get("playtime_last_two_weeks"),
                    "language": review.get("language"),
                    "timestamp_created": review.get("timestamp_created"),
                    "timestamp_updated": review.get("timestamp_updated"),
                    "review_score": review.get("weighted_vote_score"),
                    "written_during_early_access": review.get("written_during_early_access"),
                }
                
                reviews.append(review_data)
                review_ids.add(review_id)
                new_count += 1

            # print how many review we have in total and how many new data we get in one batch
            print(f"Collected {len(reviews)} reviews so far... (+{new_count} new)")

            # -----------------------
            #     Backoff Counter 
            # -----------------------
            # This is a counter-measure of the notorious Steam API trap, where it give the 200 status code
            # but give the exact same data. I have waste hours of waiting before implementing this measurement.
            # The logic is simple, if the new_count doesn't add up it will add a backoff_counter
            # if the backoff_counter add to a certain number as set above, the code will stop.
            if new_count == 0:
                backoff_counter += 1
            else:
                backoff_counter = 0

            if backoff_counter >= backoff_limit:
                print("No new reviews for several rounds. Stopping.")
                break
            
            # -----------------------
            #     Save Checkpoint 
            # -----------------------
            # This logic will add a checkpoint so this code can be continued at later date
            # I decide to do this since a progress of thousands of data can be hindered by a terrible internet
            # For every new x data, it will be saved to csv
            if len(reviews) % checkpoint_interval < new_count:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                pd.DataFrame(reviews).to_csv(checkpoint_file, index=False)
                print(f"Checkpoint saved at {len(reviews)} reviews [{timestamp}]")

            # ---------------------------
            #     Stop if max reached 
            # ---------------------------
            # After a set max reviews, the code will stop
            if len(reviews) >= max_reviews:
                print(f"Reached max review limit of {max_reviews}. Stopping.")
                break

            # -----------------------
            #     Cursor Tracking 
            # -----------------------
            # Another steam trap measurements. The logic is almost like the backoff_counter
            # but instead of checking the data, this will track the actual cursore returned by steam
            if cursor == prev_cursor:
                same_cursor_count += 1
                if same_cursor_count >= 3:
                    print("Cursor stuck (same for 3 rounds). Exiting loop.")
                    break
            else:
                same_cursor_count = 0

            prev_cursor = cursor
            cursor = data.get("cursor", "")
            time.sleep(2)

# ---------------------
#     FINAL SAVE
# ---------------------
# Now to actually save the final data, after it loops through all the perimeter
# it will save the final csv. Add timestamp and how many reviews for easy tracking
timestamp = datetime.now().strftime('%Y%m%d_%H%M')
df = pd.DataFrame(reviews)
df.to_csv(final_output, index=False)
print(f"Final saved: {len(reviews)} reviews to '{final_output}' at {timestamp}")