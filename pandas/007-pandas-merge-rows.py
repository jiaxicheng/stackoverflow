""" merge rows for each Task when Status_From is the same as the Status_To in the previous Row
"""

data = """Task,Status_From,Status_To
AAA,31-Aug-18,04-Sep-18
BBB,21-Jun-18,21-Jun-18
BBB,21-Jun-18,29-Jun-18
BBB,29-Jun-18,29-Jun-18
CCC,20-Aug-18,20-Aug-18
CCC,24-Aug-18,24-Aug-18
CCC,24-Aug-18,01-Sep-18
DDD,06-Jul-18,06-Jul-18
EEE,18-May-18,18-May-18
FFF,01-Aug-18,01-Aug-18
GGG,20-Apr-18,23-Apr-18
GGG,23-Apr-18,23-Apr-18
HHH,22-Jan-18,23-Jan-18
HHH,23-Jan-18,23-Jan-18
HHH,23-Jan-18,30-Jan-18"""

df = pd.read_csv(pd.io.common.StringIO(data))

df1 = df.assign(
    g=df.groupby('Task').apply(lambda x: (x.Status_From != x.Status_To.shift()).cumsum()).reset_index(level=0, drop=True)
)

df1['Status_To'] = df1.groupby(['Task', 'g']).Status_To.transform('last')

df1 = df1.drop_duplicates(['Task','g'])

df1
#Out[350]: 
#   Task Status_From  Status_To  g
#0   AAA   31-Aug-18  04-Sep-18  1
#1   BBB   21-Jun-18  29-Jun-18  1
#4   CCC   20-Aug-18  20-Aug-18  1
#5   CCC   24-Aug-18  01-Sep-18  2
#7   DDD   06-Jul-18  06-Jul-18  1
#8   EEE   18-May-18  18-May-18  1
#9   FFF   01-Aug-18  01-Aug-18  1
#10  GGG   20-Apr-18  23-Apr-18  1
#12  HHH   22-Jan-18  30-Jan-18  1

