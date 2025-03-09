#!/usr/bin/env python3

import sys
import json
import re

# List of 10 largest countries by population
COUNTRIES = ["China", "India", "United States", "Indonesia", "Pakistan", 
             "Brazil", "Nigeria", "Bangladesh", "Russia", "Mexico"]

def preprocess_text(text):
    """Convert text to lowercase and remove special characters."""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Remove punctuation
    return text

for line in sys.stdin:
    try:
        # Parse JSON input
        post = json.loads(line)

        # Extract subreddit and content
        subreddit = post.get("subreddit", "").strip()
        content = post.get("content", "").strip()  # Use full post content
        if not subreddit or not content:
            continue  # Skip posts with missing subreddit or content

        # Preprocess content
        clean_content = preprocess_text(content)

        # Track whether this subreddit has already discussed a country
        discussed_countries = set()

        # Check if any country is mentioned
        for country in COUNTRIES:
            if country.lower() in clean_content:
                discussed_countries.add(country)

        # Output unique subreddit-country pairs
        for country in discussed_countries:
            print(f"{country}\t{subreddit}")  # Emit (country, subreddit)

    except json.JSONDecodeError:
        continue  # Skip malformed JSON
