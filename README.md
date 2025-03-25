🎯 Project Title:
"Shadows of Opinion: A Sentiment Analysis of Assassin's Creed Shadows Across Platforms"

🧩 Problem Statement:
While Assassin’s Creed Shadows currently holds a "Very Positive" rating on Steam (81%), this aggregated score lacks depth. The goal is to uncover detailed, topic-specific, and temporal sentiment trends surrounding the game—across multiple platforms (Steam, Reddit, Twitter, YouTube, etc.).

🔍 Project Goals:
 - Classify sentiments (Positive, Negative, Neutral) from user-generated content.
 - Extract specific themes (e.g., stealth mechanics, characters, setting, bugs).
 - Track sentiment over time (e.g., from first trailer to release and beyond).
 - Compare sentiments across platforms (Steam vs Reddit vs Twitter).
 - Visualize insights to support players, developers, and analysts.

📚 Data Sources:
 - Steam Reviews (scraped using steamreviews or beautifulsoup)
 - Reddit Posts/Comments
 - Subreddits: r/assassinscreed, r/games, r/gaming
   - Use PRAW or Pushshift API
 - Twitter/X
   - Use Tweepy or Twitter API v2
 - YouTube Comments
   - Trailer or dev update videos using YouTube Data API

🛠️ Tools & Libraries:
 - Data Collection: requests, BeautifulSoup, PRAW, Tweepy, youtube_dl, steamreviews
 - Text Processing: nltk, spaCy, re, langdetect, emoji
 - Sentiment Analysis:
 - Basic: TextBlob, VADER (good for social media/short text)
 - Advanced: BERT (with transformers, for context-aware sentiment)
 - Topic Modeling: LDA, BERTopic
 - Visualization: matplotlib, seaborn, plotly, wordcloud, streamlit (for dashboards)

🧠 Workflow:
1. Data Collection & Cleaning
2. Remove duplicates, translate non-English, clean HTML tags/emojis
3. Sentiment Labeling
4. Classify each comment/post into Positive / Neutral / Negative
5. Keyword Extraction & Topic Modeling
6. Identify key topics: characters, story, combat, visuals, performance
7. Time Series Sentiment
8. Compare sentiment from trailer launch → gameplay reveal → release → patches
9. Cross-Platform Comparison
10. Are Steam users more positive than Redditors? Are Twitter users more critical?
11. Optional: Review Bomb Detection
12. Use timestamps and sudden spikes in review count or negativity

📊 Output & Deliverables:
Interactive dashboard showing:
 - Sentiment trends over time
 - Word clouds by sentiment class
 - Platform comparison chart
 - Topic-based sentiment breakdown
 - PDF report or Medium-style blog post with key insights
 - GitHub repo with cleaned dataset, notebook, and dashboard app

🧪 Bonus Explorations:
 - Gender-based sentiment (if detectable)
 - Regional sentiment mapping (e.g., are Japanese players more critical of the setting?)
 - Compare AC Shadows with previous AC titles

🧭 Success Criteria:
 - Collect and analyze >5,000 comments from multiple platforms
 - 80% classification accuracy (if building your own model)
 - Provide actionable insights or interesting findings beyond "81% positive"
