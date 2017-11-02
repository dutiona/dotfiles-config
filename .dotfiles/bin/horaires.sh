#!/bin/bash

# Take a command as argument and delete all output of the command
function silent(){ $@ >/dev/null 2>&1; }

# Test if $1 string start match $2
function match(){
    if [ $# -ne 2 ] ; then
        false
        return;
    fi
    echo "$1" | grep -q -E "$2"
}

# Get the IP address of a specified interface if specified
function getIp() {
    if [ "$#" -eq "0" ] ; then
        ethernet=`getIp eth0``getIp en0`
        echo "$ethernet"
        if [ "$ethernet" != "" ] ; then
            return;
        fi

        wlan=`getIp wlan0``getIp en1`
        echo "$wlan"
        return;
    fi

    if ! silent /sbin/ifconfig $1 ; then
        return;
    fi

    if silent which ifdata ; then
        echo $(ifdata -pa $1)
    else
        echo $(/sbin/ifconfig $1 | grep -o -E '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
    fi
}

# Get schedule, tabke 2 argument :
#    - id of start station
#    - id of end station
# Known station id : Lip6 (APK), Ermont Eaubone (ERT), Ivry (IV), Austerlitz (PZB)
function getData() {
    echo $(wget -t 1 -T 20 -q --no-check-certificate -O - "https://www.transilien.com/web/ITProchainsTrainsAvecDest.do?codeTr3aDepart=$1&codeTr3aDest=$2&urlModule=/site/pid/184&gareAcc=true" | grep "[0-9][0-9]:[0-9][0-9]" | sed -r "s/.*([0-9][0-9]:[0-9][0-9]).*/\1/" | head -n4 | xargs)
}



### main ###

if [ `uname` = "Darwin" ] ; then
    sed() { /opt/local/bin/gsed $@; }
    wget() { /opt/local/bin/wget $@; }
fi

if [ "$1" = "conky" ] ; then
    line_header="\${goto 32}\${color1}"
    data_header="\${color2}"
else
    line_header=
    data_header=
fi

if match $(getIp) "^132\.227\." ; then
    echo "${line_header}A>I : ${data_header}$(getData PZB IV)"
elif match $(getIp) "^192\.168\.42\." ; then
    echo "${line_header}I>A : ${data_header}$(getData IV PZB)"
elif match $(getIp) "^192\.168\.0\." ; then
    echo "${line_header}E>I : ${data_header}$(getData ERT IV)"
else
    echo ""
fi

