#!/usr/bin/env python3

#A mapper python code which is designed for JSON formatted data, could be used as a frame 
"""mapper.py"""

import sys
import json
import re

# Countries to shearch for in the reddit comments:
pronouns = {""}

# Read input from standard input 
for line in sys.stdin:
    # Remove whitespace in the beginning and end of a string
    line = line.strip()
    if not line:
        continue

    try:
        reddit = json.loads(line)  #Changed name to reddit from tweet
    except json.JSONDecodeError:  
        continue

    # Skip retweets, if "retweeted_status" is present for retweets
    #This is not necessary for the project
    #if tweet.get("retweeted_status"):
     #   continue

    # Get tweet text and convert all words to lowercase, case insensistiv
    text = reddit.get("text", "").lower()

    # Identify all words in the tweet, ignoring punctuation, uses set to get the unique words
    words = set(re.findall(r'\w+', text))  

    # Find pronouns in the tweet, intersection will return the words which is 
    # present in words and the dict pronouns
    found_pro = pronouns.intersection(words)  

    # For each pronoun found in the tweet, output a count of 1
    for pro in found_pro: 
        print(f"{pro}\t1")
