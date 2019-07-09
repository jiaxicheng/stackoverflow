
if you are using pandas 0.18.0+, you can try extractall()
https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.extractall.html

    df = pd.DataFrame([('C55H85N17O25S4',),('C23H65',)],columns=['molecular_formula'])
    df = pd.DataFrame([('C55H85N17O25S4',),('C23H65',),(None,), (None,), ('C22H16ClN3OS2',)
             , ('C37H42Cl2N2O6',), ('C21H30BrNO4',), ('C11H13ClN2',), ('C34H53NaO8',), ('A0',) 
        ],columns=['molecular_formula'])
    #  molecular_formula
    #0    C55H85N17O25S4
    #1            C23H65


    # list of concerned atoms 
    atoms = ['C', 'H', 'O', 'N', 'Cl','S','Br']

    # regeex pattern
    atom_ptn = r'(?P<atom>' + r'|'.join(atoms) + r')(?P<cnt>\d+)'
    print(atom_ptn)
    #(?P<atom>C|H|O|N|Cl|S|Br)(?P<cnt>\d+)

    # extract the combo of atoms and number into rows and drop index.levels[1]
    df1 = df.molecular_formula.str.extractall(atom_ptn).reset_index(level=1, drop=True)
    #  atom  cnt
    #0    C   55
    #0    H   85
    #0    N   17
    #0    O   25
    #0    S    4
    #1    C   23
    #1    H   65

    # now you can pivot, reindex and then fillna
    lst = pd.pivot(index=df1.index, columns=df1.atom, values=df1.cnt) \
            .reindex(columns=atoms) \
            .fillna(0, downcast='infer')
    #atom    C   H   O   N  Cl  S  Br
    #0      55  85  25  17   0  4   0
    #1      23  65   0   0   0  0   0

    # join the result to the original dataframe
    df.join(lst)
    #  molecular_formula    C   H   O   N  Cl  S  Br
    #0    C55H85N17O25S4   55  85  25  17   0  4   0
    #1           C231H65   23  65   0   0   0  0   0

#########################################################
#########################################################
s = df[~df.molecular_formula.isnull()].molecular_formula.str.findall(atom_ptn)

## 
list = [ (i, *v) for i, L in zip(s.index, s.str) for v in L  if type(v) is tuple ]
list = [ (i, *v) for i, L in zip(s.index, s.values) for v in L ]
Note: *v is a Panthon-3 feature and does not work for Panthon-2


df1 = pd.DataFrame([ (i, vs[0], vs[1]) for i,d in zip(s.index, s.values) for vs in d], columns=['idx', 'atom', 'cnt']).set_index('idx')

lst = pd.pivot(index=df1.idx, columns=df1.atom, values=df1.cnt) \
        .reindex(columns=atoms) \
        .fillna(0, downcast='infer')
#########################################################

    
    df = pd.DataFrame([('C55H85N17O25S4',),('C23H65',),(None,), (None,), ('C22H16ClN3OS2',)
             , ('C37H42Cl2N2O6',), ('C21H30BrNO4',), ('C11H13ClN2',), ('C34H53NaO8',), ('A0',) 
        ],columns=['molecular_formula'])


    df1 = df.molecular_formula.str.extractall(atom_ptn) \
            .reset_index(level=1, drop=True) \
            .set_index('atom', append=True) \
            .unstack(1)
    
    df1.columns = [ c[1] for c in df1.columns ]
    
    df.join(df1.reindex(columns=atoms).fillna(0, downcast='infer'))
    #  molecular_formula    C    H    O    N   Cl    S   Br
    #0    C55H85N17O25S4   55   85   25   17    0    4  0.0
    #1            C23H65   23   65    0    0    0    0  0.0
    #2              None  NaN  NaN  NaN  NaN  NaN  NaN  NaN
    #3              None  NaN  NaN  NaN  NaN  NaN  NaN  NaN
    #4     C22H16ClN3OS2   22   16    0    3    0    2  0.0
    #5     C37H42Cl2N2O6   37   42    6    2    2    0  0.0
    #6       C21H30BrNO4   21   30    4    0    0    0  0.0
    #7        C11H13ClN2   11   13    0    2    0    0  0.0
    #8        C34H53NaO8   34   53    8    0    0    0  0.0
    #9                A0  NaN  NaN  NaN  NaN  NaN  NaN  NaN

    df.join(df1.reindex(columns=atoms)).fillna({c:0 for c in atoms}, downcast='infer') 
    #  molecular_formula   C   H   O   N Cl  S  Br
    #0    C55H85N17O25S4  55  85  25  17  0  4   0
    #1            C23H65  23  65   0   0  0  0   0
    #2              None   0   0   0   0  0  0   0
    #3              None   0   0   0   0  0  0   0
    #4     C22H16ClN3OS2  22  16   0   3  0  2   0
    #5     C37H42Cl2N2O6  37  42   6   2  2  0   0
    #6       C21H30BrNO4  21  30   4   0  0  0   0
    #7        C11H13ClN2  11  13   0   2  0  0   0
    #8        C34H53NaO8  34  53   8   0  0  0   0
    #9                A0   0   0   0   0  0  0   0



######
# 
df.join(df.molecular_formula.str.extractall(atom_ptn) 
          .droplevel(1)
          .set_index('atom', append=True) 
          .unstack(1) 
          .droplevel(0, axis=1) 
          .reindex(columns=atoms) 
   ).fillna({c:0 for c in atoms}, downcast='infer')

UPDATE 5/13/2019

Per comments, atoms with missing numbers should be assigned with a constant '1'

Modifications:

(1) the regex:
  * `cnt` should allow EMPTY string, thus: from `(?P<cnt>\d+)` to `(?P<cnt>\d*)` 
  * `atom` must be sorted so that longer string matches before shorter ones, this is important 
    how regex engine works

        # sort the list of atoms based on their length
        atoms_sorted = [ i[0] for i in sorted([ (k, len(k)) for k in atoms], key=lambda x: -x[1]) ]
        atoms_sorted = sorted(atoms, key=len, reverse=True)

        # the new pattern based on list of atoms_sorted and \d* on cnt
        atom_ptn = r'(?P<atom>' + r'|'.join(atoms_sorted) + r')(?P<cnt>\d*)'
        print(atom_ptn)
        #(?P<atom>Cl|Br|C|H|O|N|S)(?P<cnt>\d*)

  To test it out. you can try: `df.molecular_formula.str.extractall(atom_ptn)` by using
  *atom_ptn* created by both sorted and unsorted list.

(2) fillna(1) for all atoms matching 0 digits from the above regex pattern, see below: 

        df.join(df.molecular_formula.str.extractall(atom_ptn)
                  .fillna(1)
                  .droplevel(1)
                  .set_index('atom', append=True)
                  .unstack(1)
                  .droplevel(0, axis=1)
                  .reindex(columns=atoms)
           ).fillna({c:0 for c in atoms}, downcast='infer')

