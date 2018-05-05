#!/usr/bin/env python
"""For an Dataframe like the following:
  userID  dayID  feature0  feature1  feature2  feature3
0    xy1      0        24      15.3        41        43
1    xy1      1         5      24.0        34        40
2    xy1      2        30       7.0         8        10
3    gh3      0        50       4.0        11        12
4    gh3      1        49       3.0        59        11
5    gh3      2         4       9.0        12        15

For each userID, select from feature0 to feature3 and dayID from 0 to 2, every dayID
and feature must be selected at least once.

The problem can be divided into the following items: 
(1) Given an 3*4 zeros 2-D array np.zeros((3,4)) and 4 '1', you need to fill '1' into this 
zeros array, so that the sum of every row and evry column is greater than '0'. 
(2) You will then need to find the indices of these '1' and retrieve the values on these 
indices(not '1' in the actual problems)

The real problems might contains 300+ dayID, 1000+ features for each users. so performance
is another consideration.

The following code works on the 3*4 matrix for each userID:
1. in the function randx(), we first create a list of row indices which can cover all rows 0,1,2
and the rest ones will be randomly selected from all possible row indices. This is to guarantee 
all rows get involved. 

2. shuffle the list to randomize it

3. enumerate all columns and specify a row index from the above list for each column

4. the element value wll be retrieved with df.iat() based on the row/column indice and 
   the result is returned as a pd.Series(), so that each element hold a column of its own

5. run .rename() to set up the column names.

REF: https://stackoverflow.com/questions/50165614/selecting-a-random-value-in-a-pandas-data-frame-by-column/50176681#50176681

XiCheng Jia, May 4, 2018 @ New York
Environment: Python 3.6.4, Pandas 0.22.0
"""
import pandas as pd
import numpy as np
from io import StringIO

str = """userID  dayID  feature0  feature1  feature2  feature3
xy1      0        24      15.3        41        43
xy1      1         5      24.0        34        40
xy1      2        30       7.0         8        10
gh3      0        50       4.0        11        12
gh3      1        49       3.0        59        11
gh3      2         4       9.0        12        15
"""

df = pd.read_table(StringIO(str), sep='\s+')

def randx(dfg):
    # create a list and make sure 0,1,2 all in so that all DayIDs are covered
    # the last one is randomly slected from 0,1,2
    x = [ 0, 1, 2, np.random.randint(3) ]

    # shuffle the list 
    np.random.shuffle(x)

    # enumerate list-x, with the row-index and the counter aligned with the column-index,
    # to retrieve the actual element in the dataframe. the 2 in enumerate
    # is to skip the first two columns which are 'userID' and 'dayID'
    return pd.Series([ dfg.iat[j,i] for i,j in enumerate(x,2) ])

    ## you can also return the list of result into one column
    #return [ dfg.iat[j,i] for i,j in enumerate(x,2) ]

def feature_name(x): 
    return 'feature{}'.format(x)

# if you have many irrelevant columns, then
# retrieve only columns required for calculations
# if you have 1000+ columns(features) and all are required
# skip the following line, you might instead split your dataframe using slicing, 
# i.e. putting 200 features for each calculation, and then merge the results
new_df = df[[ "userID", "dayID", *list(map(feature_name, [0,1,2,3])) ]]

# do the calculations
d1 = (new_df.groupby('userID')
            .apply(randx)
            # comment out the following .rename() function if you want to 
            # return list instead of Series
            .rename(feature_name, axis=1)
     )

print(df, d1, sep="\n\n")

"""More thoughts:
1. the list of random row indices that satisfy the requirements can be dished out before running apply(randx).
   For example if all userID have the same number of dayID, you can use a list of list that preset these row-indices.
   otherwise use a dictionary of lists. 

   A reminder: if you use list of lists and L.pop() to dish out the row-indices, make sure the number 
   of lists should be number of unique userID + 1, since GroupBy.apply() call it's function twice on the first
   group

2. Instead of returning a pd.Series() in the function randx(), you can also directly return a list. in such 
   case, all retrieved features will be saved in one column(see below). you can normalize them later.
```
userID
gh3    [50, 3.0, 59, 15]
xy1    [30, 7.0, 34, 43]
```

3. if still slow, you can split 1000+ features into groups, i.e. process 200 columns(features) each run, slice the
   predefined row-indices accordingly, and then merge the results. 

"""
