#!/usr/bin/env python
"""Sometimes, it's useful to post-process a Pivot table or a simialr MultiIndex
dataframe. for example to add new columns, to sort different levels. 
below is an example from stackoverflow:
https://stackoverflow.com/questions/50750189/calculated-columns-in-multiindex/50753435#50753435

The following knowledge is very useful for this task:
(1) df.loc() method supports an axis argument which can simplify referencing row/column in 
    MultiIndex dataframes. for example, the following 4 notations are the same:
 
    *  df2.loc(1)[:,'total']  which is the same as: df2.loc(axis=1)[:,'total'] 

    *  df2.loc[:,(slice(None), 'total')]

    *  idx = pd.IndexSlice
       df2.loc[:,idx[:,'total']]

    The first form is not supported in the older version of Pandas 0.17.0
    Working version includes: 0.22.0 and 0.23.0

(2) df.sort_index() has some interesting behaviors: by default, sort_remaining=True, 
    so all levels will be sorted even if you don't specify them on the level argument. 
    One solution to overcome this is to specify both `level` and `ascending` arguments as 
    list(as used in the below code example), then the excluded levels will not be sorted. 
    In the newer version Pandas, you can also use `sort_remaining` argument:
    
        sort_index(axis=1, level=[0], sort_remaining=False).

    Note: with the older version like 0.17.0, columns index must be sorted before
          using the assignment, otherwise you will receive the following error:

   KeyError: 'MultiIndex Slicing requires the index to be fully lexsorted tuple len (2), lexsort depth (1)'

    Adding the following line before assigning 'total', 'avg' and 'std' columns solved the issue.
    In such case, you might still need reindex() to sort the level-1 columns to a specific order.
   
        df2.sort_index(axis=1, inplace=True)

(3) There are often alignment issues on multiIndex when assigning calculated fields 
    after running groupby(). Using values attribute to convert dataframe into numpy.ndarray 
    can overcome this issue.

Note: Below code shuold be working with Pandas version 0.22.0 and above
Pandas 0.17.0 has some issues when assigning values in multiIndex and will not work.

"""
import pandas as pd

str="""card    auth   trans_month   order_number
Amex     A        2017-11       1234
Visa     A        2017-12       2345
Amex     D        2017-12       3416
MC       A        2017-12       3426
Visa     A        2017-11       3436
Amex     D        2017-12       3446
Visa     A        2017-11       3466
Amex     D        2017-12       3476
Visa     D        2017-11       3486
"""

# create dataframe from the above sample data
df = pd.read_table(pd.io.common.StringIO(str), sep='\s+')

# create a pivot table
df1 = df.pivot_table(index='card', columns=['trans_month', 'auth'],values='order_number', aggfunc='count')
print(df1)

# month 2017-11      2017-12     
# auth        A    D       A    D
# card                           
# Amex      1.0  NaN     NaN  3.0
# MC        NaN  NaN     1.0  NaN
# Visa      2.0  1.0     1.0  NaN

# create an empty dataframe with the same index/column layout as df1
# except the level-1 in columns
midx = pd.MultiIndex.from_product([df1.columns.levels[0], ['total', 'avg', 'std', 'pct']], names=df1.columns.names)
df2 = pd.DataFrame(columns=midx, index=df1.index)
print(df2)

# month  2017-11                  2017-12                
# auth     total  avg   std  pct    total  avg   std  pct
# card                                                   
# Amex       NaN  NaN   NaN  NaN      NaN  NaN   NaN  NaN
# MC         NaN  NaN   NaN  NaN      NaN  NaN   NaN  NaN
# Visa       NaN  NaN   NaN  NaN      NaN  NaN   NaN  NaN

# Calculate the common stats:
df2.loc(1)[:,'total'] = df1.groupby(level=0, axis=1).sum().values
df2.loc(1)[:,'avg']   = df1.groupby(level=0, axis=1).mean().values
df2.loc(1)[:,'std']   = df1.groupby(level=0, axis=1).std().values

# join df2 with df1 and assign the result to df3 (can also overwrite df1): 
# sort the result on columns level-0 only, keep the order of level-1 as-is
df3 = df1.join(df2).sort_index(axis=1, level=[0], ascending=[True])

# calculate `pct` which needs both a calculated field and an original field
# auth-rate = A / total
df3.loc(1)[:,'pct'] = df3.groupby(level=0, axis=1)\
                         .apply(lambda x: x.loc(1)[:,'A'].values/x.loc(1)[:,'total'].values) \
                         .values

# round the floating numbers to decimals
df3.loc(1)[:,'pct'] = df3.loc(1)[:,'pct'].round(decimals=2)
df3.loc(1)[:,'std'] = df3.loc(1)[:,'std'].round(decimals=4)
print(df3)

# month 2017-11                               2017-12                         
# auth        A    D total  avg     std   pct       A    D total  avg std  pct
# card                                                                        
# Amex      1.0  NaN   1.0  1.0     NaN  1.00     NaN  3.0   3.0  3.0 NaN  NaN
# MC        NaN  NaN   0.0  NaN     NaN   NaN     1.0  NaN   1.0  1.0 NaN  1.0
# Visa      2.0  1.0   3.0  1.5  0.7071  0.67     1.0  NaN   1.0  1.0 NaN  1.0
