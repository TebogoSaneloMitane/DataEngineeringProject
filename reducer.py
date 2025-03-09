#!/usr/bin/env python3

import sys
from collections import defaultdict

# Dictionary to store country-wise unique subreddit count
country_subreddits = defaultdict(set)

for line in sys.stdin:
    try:
        country, subreddit = line.strip().split("\t")
        country_subreddits[country].add(subreddit)  # Store unique subreddits
    except ValueError:
        continue  # Skip malformed lines

# Compute discussion counts and sort by most discussed countries
country_discussion_counts = {country: len(subreddits) for country, subreddits in country_subreddits.items()}
sorted_countries = sorted(country_discussion_counts.items(), key=lambda x: x[1], reverse=True)

# Output top 10 most discussed countries
for country, count in sorted_countries[:10]:
    print(f"{country}\t{count}")
