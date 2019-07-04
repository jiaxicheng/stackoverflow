https://stackoverflow.com/questions/55959836/find-the-minimum-value-of-a-column-between-two-occurrences-of-a-value-in-another

str="""No Open High Low Close signal 
1   75   95   65  50    signal 
2   78   94   74  77    none 
3   83   91   81  84    none 
4   91   101  88  93    signal 
5   104  121  95  103   none 
6   101  111  99  105   none 
7   97   108  95  101   signal 
8   103  113  102 106   none 
9   108  128  105 114   signal 
10  104  114  99  102   none 
11  110  130  105 115   signal 
12  112  122  110 115   none 
13  118  145  112 123   none 
14  123  143  71  133   signal 
15  130  150  120 140   none"""

df = pd.read_csv(pd.io.common.StringIO(str), sep='\s+') 

# cols which are used in this task
cols = ['No', 'Low', 'signal'] 

# create a new dataframe, cloned all 'signal' rows but rename signal to 'temp', sort the rows
df1 = pd.concat([df[cols], df.loc[df.signal=='signal',cols].assign(signal='temp')]) \
        .sort_values(['No', 'signal'],ascending=[1,0])

# set up group-number with cumsum() and get min() value from each group
df1['g'] = (df1.signal == 'signal').cumsum()
# the following field just for reference, no need for calculation
df1['Low_min'] = df1.groupby('g').Low.transform('min')

<plot>

Based on your description, for Line no 9 (yellow backgroud, the first item in df1.g==4), we can check 
df1.loc[df1.g==3, "Low_min"] (red bordered) against 
df1.loc[df1.g==1, "Low_min"] (green bordered)

# if we have the following:
s = df1.groupby('g').Low.min()
# the list of buy group should satisfy s.shift(1) > s.shift(3)
buy = s[s.shift(1) > s.shift(3)].index.tolist()

# set up condition
# m1: row marked with signal
# skip the first 3 groups which do not have enough signals
m1 = df1.signal.eq('signal') & df1.g.gt(3)
# m2: m1 plus must in buy list
m2 = df1.g.isin(buy) & m1
df1['trade'] = np.select([m2, m1], ['Buy', 'None'], '') 

#In [36]: df1
#Out[36]: 
#    No  Low  signal  g  Low_min trade
#0    1   65    temp  0       65      
#0    1   65  signal  1       65      
#1    2   74    none  1       65      
#2    3   81    none  1       65      
#3    4   88    temp  1       65      
#3    4   88  signal  2       88      
#4    5   95    none  2       88      
#5    6   99    none  2       88      
#6    7   95    temp  2       88      
#6    7   95  signal  3       95      
#7    8  102    none  3       95      
#8    9  105    temp  3       95      
#8    9  105  signal  4       99   Buy
#9   10   99    none  4       99      
#10  11  105    temp  4       99      
#10  11  105  signal  5       71   Buy
#11  12  110    none  5       71      
#12  13  112    none  5       71      
#13  14   71    temp  5       71      
#13  14   71  signal  6       71  None
#14  15  120    none  6       71      


#g = (df1.signal == 'signal').cumsum()
#s = df1.groupby('g').Low.min()
#g_buy = s[(s.shift(1) > s.shift(3)) ].index.tolist()


# set up column `trade` with EMPTY as default and update 
# the field based on df1.trade (using the index)
df['trade'] = ''
df.trade.update(df1.loc[df1.signal=='signal',"trade"])
