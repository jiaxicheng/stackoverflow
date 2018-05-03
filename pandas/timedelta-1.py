#!/usr/bin/env python
"""Problem: The user wanted to sum the total time visitors spent in a location 
between 8PM and 8AM the next day. each line of records has two timestamps:
`t1` as arrival time and `t2` as departure time. t1 and t2 can span multiple 
days. 
REF:https://stackoverflow.com/questions/50124353/optimized-method-for-dataframes-to-find-time-range-overlaps-with-specified-hou/50143130#50143130

See the diagram, the window has been divided into 6 zones by 8AM and 8PM on 
1-2 consecutive days depends on the adjusted start-time and end-time which
I will discuss below:

            +---day1--+---day2--+
            |   z1    |   z4    |
            +---------+---------+<-- 8AM (a8)
            |   z2    |   z5    |
(p8) 8PM -->+---------+---------+
            |   z3    |   z6    |
            +---------+---------+

First we calculate the `delta_in_days` between two timestamps `t1` and `t2`,
each individual delta day will get you extra 12 hours into the final total.

Adding up the delta_in_days to the start-time. so the calculating
window is within 1 day (24 hours). Assume `ts` is the adjusted start-time 
and `te` is the leaving-time, then  

   ts = t1 + delta_in_days
   te = t2

Also set:
 - `p8` the same day as `ts` but at 8PM
 - `a8` the same day as `te` but at 8AM

Case-1: `ts` and `te` in the same day - basically in `day2` and `p8 > a8`
   if both in the same zone: z4(te < a8) or z6(ts > p8): 
      total = te - ts
   else:
      total = max(0, te - p8) + max(0, a8 - ts)

Case-2: `ts`, `te` in different days, if `te` in z6, then `ts` must be in z3
   if te > p8 + 1day:
       total = (te - p8 - 1day) + (a8 - ts)

Case-3: `ts`, `te` in different days, if `ts` in z1, then `te` must be in z4
   if ts < a8 - 1day
       total = (a8 - 1day - ts) + (te - p8)

Case-4: `ts` in [z2, z3] while `te` in [z4, z5]
   total = min(a8, te) - max(p8, ts)  

XiCheng Jia, May 2, 2018 @ New York
Environment: Python 3.6.4, Pandas 0.22.0
"""

import pandas as pd
from io import StringIO

str="""Jan 1, 15:00 to Jan 1, 18:35 
Jan 3, 09:12 to Jan 5, 10:54 
Jan 5, 21:00 to Jan 6, 23:48
Jan 5, 23:00 to Jan 6, 20:48
Jan 5, 03:00 to Jan 6, 02:48
Jan 5, 10:00 to Jan 6, 05:48
Jan 5, 21:00 to Jan 6, 10:48
"""

df = pd.read_table(StringIO(str)
     , sep='\s*to\s*'
     , engine='python'
     , names=['t1','t2']
)

for field in ['t1', 't2']:
    df[field] = pd.to_datetime(df[field], format="%b %d, %H:%M")

delta_1_day = pd.Timedelta('1 days')
# add 12 houtrs for each delta_1_day
ns_spent_in_1_day = int(delta_1_day.value*12/24)

# the total time is counted in nano seconds
def count_off_hour_in_ns(x):
    t1 = x['t1']
    t2 = x['t2']

    # number of days from t1 to t2
    delta_days = (t2 - t1).days 
    if delta_days < 0: 
        return 0

    # add delta_days to start-time so ts and te in 1-day window
    # define the start-time(ts) and end-time(te) of the window
    ts = t1 + pd.Timedelta('{} days'.format(delta_days))
    te = t2

    # 8PM the same day as ts
    p8 = ts.replace(hour=20, minute=0, second=0)

    # 8AM the same day as te
    a8 = te.replace(hour=8, minute=0, second=0)

    # Case-1: te and ts on the same day
    if p8 > a8:
        if te < a8 or ts > p8:
            total = (te - ts).value
        else:
            total = max(0, (te - p8).value) + max(0, (a8 - ts).value)
    # Case-2: different days
    elif te > p8 + delta_1_day:
        total = (te - p8 - delta_1_day + a8 - ts).value
    # Case-3: different days
    elif ts < a8 - delta_1_day:
        total = (a8 - delta_1_day - ts + te - p8).value
    # Case-4: different days, all others 
    else:
        total = (min(te, a8) - max(ts, p8)).value

    return total + delta_days * ns_spent_in_1_day

df['total'] = df.apply(count_off_hour_in_ns, axis=1)

print(df)
