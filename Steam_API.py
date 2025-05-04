import requests
import pandas as pd
import time
import os
from datetime import datetime


# ---------------------
#     LINK AND GAME NAME
# ---------------------
game_name = "AC_Shadow" # the file names
app_id = "3159330" # use the steam store page to know the app id
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
filters = ["all"]

# ---------------------
#     LOAD CHECKPOINT 
# ---------------------
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
cursor = "*"
prev_cursor = None
same_cursor_count = 0
backoff_counter = 0

for day_range in day_ranges:
    for filter_type in filters:
        print(f"\n Request with day_range={day_range}, filter='{filter_type}'")
        while True:
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        url,
                        params={
                            "cursor": cursor,
                            "json": 1,
                            "num_per_page": 50,
                            "day_range": day_range,
                            "filter": filter_type
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        break
                    else:
                        print(f"API Error {response.status_code}. Retrying...")
                except Exception as e:
                    print(f"Request failed: {e}. Retrying...")
                time.sleep(2 + attempt)
            
            else:
                print("Max retries reached. Exiting.")
                break

            data = response.json()

            if "reviews" not in data or not data["reviews"]:
                print("No more reviews found.")
                break

            new_count = 0
            for review in data["reviews"]:
                review_id = str(review.get("recommendationid"))
                if review_id in review_ids:
                    continue

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

            print(f"Collected {len(reviews)} reviews so far... (+{new_count} new)")

            # === Backoff Counter ===
            if new_count == 0:
                backoff_counter += 1
            else:
                backoff_counter = 0

            if backoff_counter >= backoff_limit:
                print("No new reviews for several rounds. Stopping.")
                break

            # === Save Checkpoint ===
            if len(reviews) % checkpoint_interval < new_count:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                pd.DataFrame(reviews).to_csv(checkpoint_file, index=False)
                print(f"Checkpoint saved at {len(reviews)} reviews [{timestamp}]")

            # === Stop if max reached ===
            if len(reviews) >= max_reviews:
                print(f"Reached max review limit of {max_reviews}. Stopping.")
                break

            # === Cursor Tracking ===
            if cursor == data.get("cursor", ""):
                same_cursor_count += 1
                if same_cursor_count >= 3:
                    print("Cursor stuck (same for 3 rounds). Exiting loop.")
                    break
            else:
                same_cursor_count = 0

            prev_cursor = cursor
            cursor = data.get("cursor", "")
            time.sleep(2)  # Slightly longer pause to avoid being rate-limited

# ---------------------
#     FINAL SAVE
# ---------------------
timestamp = datetime.now().strftime('%Y%m%d_%H%M')
df = pd.DataFrame(reviews)
df.to_csv(final_output, index=False)
print(f"Final saved: {len(reviews)} reviews to '{final_output}' at {timestamp}")