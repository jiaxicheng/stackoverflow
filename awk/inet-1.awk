#  an gawk program to calculate inet_ntoa and inet_aton, similar to 
#  https://github.com/jiaxicheng/bigdata/blob/master/pyspark/notes/n090-sparksql-bitwise-2_inet.txt
#
# Example:
#
#   echo "68.192.173.70/27" | awk -f inet.awk

function inet_aton(    ip,n,val,i,ips) {
    n = split(ip, ips, "[.]")
    val = 0;
    for(i=1; i<=n; i++) {
        val += ips[i]*lshift(1,8*(4-i))
    }
    return val
}

function inet_ntoa(num,    ip,i) {
    ip = ""
    for(i=24; i>=0; i-=8) { 
        ip = (ip == "" ? "" : ip".") rshift(and(lshift(255,i),num),i)
    }
    return ip
}

function ip_network(iprange,   subnet,ips,net) {
    split(subnet, net, "[/]")
    iprange["start"] = and(inet_aton(net[1]),lshift(-1,32-net[2]))
    iprange["end"] = iprange["start"] + compl(lshift(-1,32-net[2]))
}

/\// { 
    ip_network(iprange,$1); 
    print iprange["start"], inet_ntoa(iprange["start"]) ,iprange["end"], inet_ntoa(iprange["end"]);
    next 
}
{ print inet_aton($1) }

