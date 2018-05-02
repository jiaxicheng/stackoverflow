## awk to search texts by rolling not marching ##
REF: [https://stackoverflow.com/questions/50054149/accurate-awk-array-searching](https://stackoverflow.com/questions/50053094/bash-search-a-string-and-exactly-display-the-exact-number-of-times-a-substring/50065272#50065272)

Target text: `AAAAAHHHAAHH`
Search the following sub-strings and expected result:
```
+-----+---+
| AA  | 5 |
| HH  | 3 |
| AAA | 3 |
| HHH | 1 |
| AAH | 2 |
| HHA | 1 |
+-----+---+
```
awk solution:
```
$ echo 'AA
HH
AAA
HHH
AAH
HHA'> combinations.txt

$ awk '{ x="AAAAAHHHAAHH"; n=0 }$0 != ""{
    while(t=index(x,$0)){ n++; x=substr(x,t+1) } 
    print $0,n
}' combinations.txt 
AA 5
HH 3
AAA 3
HHH 1
AAH 2
HHA 1
```

How it works:
+ use index() to search the substring `$0`(feeded from the file combination.txt) from the 
  string `x` and then return the position of the substring `$0` and save it to `t`. 
+ index() will return zero when no match is found, and thus quits the `while` loop
+ the original string `x` will then delete all chars before the matching point (including the 
  first char) by `x = substr(x, t+1)`
+ `n++` to increment the number of occurances for the matching substring `$0`
+ `$0 != ""` befoer the main while block is to skip empty string which will make a infinit loop.
