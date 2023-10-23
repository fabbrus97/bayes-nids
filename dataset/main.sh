#!/bin/bash

ARGUSPATH="/home/simone/Scaricati/tesi/argus"

if [ $# != 2 ]
then
	echo "Usage:"
	echo "$0 src_folder_pcap output_folder"
	exit 1
fi

SRC=$1
OUT=$2

#zeek:
#1. create tmp folder
tmp_folder=`openssl rand -base64 6`
mkdir $tmp_folder

function run_zeek(){
	#2. extract data to that folder
        zeek -C -r $1 addFeatures36-47.zeek Log::default_logdir=$tmp_folder
        #2.1 extract the filename
        name=`echo $1 | awk ' {
        	out = gensub(/.+\//, "", "g", $0 )
        	print out   
        } '`
        #3. take the relevant .log file, rename to csv, and place to output folder
        mv $tmp_folder/additional_features.log $OUT/${name%.pcap}-zeek.csv
        #4. delete data
        rm -r $tmp_folder/*
}

for pcap in `find $SRC -name "*.pcap"`
do
	./run_argus.sh $pcap $OUT $ARGUSPATH rm &
	run_zeek $pcap 

done

#5. delete tmp folder
rm -r $tmp_folder
