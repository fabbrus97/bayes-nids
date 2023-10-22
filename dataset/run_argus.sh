#!/bin/bash

if [ $# != 3 ] && [ $# != 4 ]
then
	echo "Usage:" 
	echo "$0 src_file out_folder argus_path [rm]"
	exit 1
fi

INPUT=$1
OUTPUT_PATH=$2
BIN_PATH=$3
name=${INPUT%.pcap}

name=`echo $name | awk ' {
	out = gensub(/.+\//, "", "g", $0 )
	print out
} '`

$BIN_PATH/argus/bin/argus -J -r $INPUT -w $OUTPUT_PATH/$name.argus

$BIN_PATH/argus-clients/bin/ra -n -u -r $OUTPUT_PATH/$name.argus -c ',' -s saddr sport daddr dport proto state dur sbytes dbytes sttl dttl sloss dloss service sload dload spkts dpkts swin dwin stcpb dtcpb smeansz dmeansz sjit djit stime ltime sintpkt dintpkt tcprtt synack ackdat trans min max sum -M dsrs=+time,+flow,+metric,+agr,+jitter > $OUTPUT_PATH/$name-argus.csv

if [ "$4" == "rm" ]
then 
	rm $OUTPUT_PATH/$name.argus
fi
