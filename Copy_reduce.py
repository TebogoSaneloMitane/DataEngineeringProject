#!/usr/bin/env python3
"""reducer.py"""

import sys

current_word = None
current_count = 0
word = None

# input comes from STDIN
for line in sys.stdin:
    # remove whitespace in the beginning and end of a string
    line = line.strip()

    # parse the input we got from mapper.py
    try:
        word, count = line.split('\t', 1)
    # convert count ('1') to int, its a string from mapper
        count = int(count)  
    except ValueError:
        # ingore the line if count was not a number
        continue

    # Output from mapper, key is the pronoun and the value is 1. If the current word is the same as
    # the word then current_count add 1
    if current_word == word:
        current_count += count
    else:
        if current_word:
            # write result to STDOUT
            print(f'{current_word}\t{current_count}')
        current_count = count
        current_word = word

# output is the number of tweets with each pronouns
if current_word == word:
    print(f'{current_word}\t{current_count}')
