#!/user/bin/env python
"""A search-pattern which is not preceded by ['no', 'none'] in the previous 1-3 words.

Challenge-1: Negative lookbehind 
The preceding 1-3 words must not show in a blacklist, say ['no', 'none']
This will match variable-length string/patterns, thus the (?<! ) negative lookbehid
assertion will not work. A workaround with Perl-compatible regex engine is to use alternation:

    (pattern1)|(pattern2)

In the above alternation:
(1) regex engine will always make sure pattern1 matches before pattern2, At the same starting point,
    pattern2 starts only when patter1 fails
(2) pattern1 matches the word ['no', 'none'] followed by 0-3 words which themselves are not 
    in the blacklist. thus any 'no, 'none' and at most three words thereafter will be filtered
    out from the regular search for pattern1. This is another challenge which is discussed next

    in the following string, pattern1 will get two matches: ['no'] and ['none is not matched']

      `no none is not matched`

(3) pattern2 is the regular search-pattern, it proceed only when pattern1 fails
(4) matched pattern1 will be saved into m.group(1) and pattern2 saved in m.group(2)

(5) In the replacement part, we defined a lambda function to handle the following logic:

    lambda m: m.group(1) or terms_map[m.group(2)]

    if m.groupp(1) is not None, meaning the pattern1 matches, we just keep it: m.group(1)
    otherwise, we will get the dictionary mapping based on pattern2 match: terms_map[m.group(2)]

Note: this regex matches either patter1 or pattern2, any texts that match neither of them 
      will be skipped and thus keep as is.


Challenge-2: Not-a-word pattern
With regular expression character set, it's easy to screen out a list of characters, i.e. [^abc] will not
match any character 'a', 'b' or 'c'. what about words, if I dont want a word to show up in a group of words
how to define this in the Perl-compatible regular expressions(regex)

Step-1:
Here is a blacklist of words we want to screen out. ['no', 'none']
which we can create as follows with Python formatter:  

  ptn_to_excluded = r'\b(?i:no|none)\b'

where \b is the word boundary and (?i: ) to make it case insensitive

Step-2:
Assume a word is anything split by the white-spaces, thus \S+ is a complete word.
We can use the negative lookahead assertion to construct a not-a-word condition

  ptn_not_a_word = r'(?:(?!{})\S+\s*)'.format(ptn_to_excluded)

Where
  (?: ) is to group a list of pattern without capturing, so it does not take \1, \2 etc
  (?! ) is the negative lookahead assertion, matches if the enclosed pattern does not match
        this does not consume any strings in the whole matching process
  {}: is a place hold with Python formatter which will fill in the pattern we designed in step-1
  \S+: is a word 
  \s*: to ensure more matched words which need to be connected by whitespaces '\s*'
       not using \s+ is to make sure the matchi does not fail at the end of the whole testing string

Step-3:
Now we want to get at most 3 words that are not in this list
  ptn_not_words = r'{}{{,3}}'.format(ptn_not_a_word)
where:
  {,3} matches 0 to 3 preceding pattern {ptn_not_a_word}
       Note: the double {{ }} is to escape '{' in Python formatter

Now we have the full pattern to match max 3 consecutive words none of which is in the blacklist 
setup in Step-1, the full pattern is as below:

  (?:(?!\b(?i:no|none)\b)\S+\s*){,3}

Combine the logic from both chellenge-1 and challenge-2, we have the final pattern:

pattern1 = r'{}\s*{}'.format(ptn_to_excluded, ptn_not_words)
print(pattern1)   -->    \b(?i:no|none)\b\s*(?:(?!\b(?i:no|none)\b)\S+\s*){,3}

pattern2 = r'\b(?:' + '|'.join(replace_terms_df.Text.tolist()) + r')\b'
print(pattern2)   -->    \b(?:random|here|some)\b

pattern = re.compile('({})|({})'.format(pattern1, pattern2))   
# before complied: (\b(?i:no|none)\b\s*(?:(?!\b(?i:no|none)\b)\S+\s*){,3})|(\b(?:random|here|some)\b)

Below are the original code I posted at stackoverflow.com with small modifications
https://stackoverflow.com/questions/50080353/string-replace-with-condition/50083341#50083341

XiCheng Jia, Apr 29, 2018 @ New York
Platform: Pandas 0.22.0, Python 3.6.4
"""
import re
import pandas as pd

text_df = pd.DataFrame(
  {'ID': [1, 2, 3], 'Text': ['here is some random text', 'no such random text, none here', 'more random text']}
)

replace_terms_df = pd.DataFrame(
  {'Replace_item': ['<RANDOM_REPLACED>', '<HERE_REPLACED>', '<SOME_REPLACED>'], 'Text': ['random', 'here', 'some']}
)

# pattern to excluded words (must match whole-word and case insensitive)
ptn_to_excluded = r'\b(?i:no|none)\b'

# ptn_1 to match the excluded words and the next maximal 3 words which are not in the 
pattern1 = r'{0}\s*(?:(?!{0})\S+\s*){{,3}}'.format(ptn_to_excluded)

# ptn_2 is the list of words you want to convert with your terms
pattern2 = r'\b(?:' + '|'.join(replace_terms_df.Text.tolist()) + r')\b'

# new pattern based on the alternation between pattern1 and pattern2
# regex:  (pattern1)|(pattern2)
pattern = re.compile('({})|({})'.format(pattern1, pattern2))

# map from text to Replace_item
terms_map = replace_terms_df.set_index('Text').Replace_item

# regex function to do the convertion
def adjust_map(x):
    return pattern.sub(lambda m:  m.group(1) or terms_map[m.group(2)], x)

# do the conversion:
text_df['new_text'] = text_df.Text.apply(adjust_map)

# prunt the resule.
print(text_df)
