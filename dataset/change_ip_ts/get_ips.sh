#!/bin/bash

for i in {0..123} 
do
	d=`date -d "2020-09-10 + $i days"  --iso-8601`
	echo $d >> ips_output.txt

	for filename in `find D-Link-IoT-Datasets/Network_Packets/ -name "*$d.pcap"`
	do
		
		echo -n "b2:c5:54:44:0f:a4 " >> ips_output.txt
		tcpdump -l -n -r $filename ether src b2:c5:54:44:0f:a4 | awk '{ print gensub(/(.*)\..*/,"\\1","g",$3), $4, gensub(/(.*)\..*/,"\\1","g",$5) }' | cut -f 1 -d " " | sort | uniq >> ips_output.txt
		echo -n "b2:c5:54:44:0f:11 " >> ips_output.txt
		tcpdump -l -n -r $filename ether src b2:c5:54:44:0f:11 | awk '{ print gensub(/(.*)\..*/,"\\1","g",$3), $4, gensub(/(.*)\..*/,"\\1","g",$5) }' | cut -f 1 -d " " | sort | uniq >> ips_output.txt
		echo -n "b0:c5:54:46:48:5d " >> ips_output.txt
		tcpdump -l -n -r $filename ether src b0:c5:54:46:48:5d | awk '{ print gensub(/(.*)\..*/,"\\1","g",$3), $4, gensub(/(.*)\..*/,"\\1","g",$5) }' | cut -f 1 -d " " | sort | uniq >> ips_output.txt
		echo -n "b0:c5:54:3d:3e:93 " >> ips_output.txt
		tcpdump -l -n -r $filename ether src b0:c5:54:3d:3e:93 | awk '{ print gensub(/(.*)\..*/,"\\1","g",$3), $4, gensub(/(.*)\..*/,"\\1","g",$5) }' | cut -f 1 -d " " | sort | uniq >> ips_output.txt
		echo -n "b0:c5:54:3d:3f:8f " >> ips_output.txt
		tcpdump -l -n -r $filename ether src b0:c5:54:3d:3f:8f | awk '{ print gensub(/(.*)\..*/,"\\1","g",$3), $4, gensub(/(.*)\..*/,"\\1","g",$5) }' | cut -f 1 -d " " | sort | uniq >> ips_output.txt
		echo -n "b0:c5:54:42:8f:a6 " >> ips_output.txt
		tcpdump -l -n -r $filename ether src b0:c5:54:42:8f:a6 | awk '{ print gensub(/(.*)\..*/,"\\1","g",$3), $4, gensub(/(.*)\..*/,"\\1","g",$5) }' | cut -f 1 -d " " | sort | uniq >> ips_output.txt
		echo -n "b0:c5:54:42:8f:e5 " >> ips_output.txt
		tcpdump -l -n -r $filename ether src b0:c5:54:42:8f:e5 | awk '{ print gensub(/(.*)\..*/,"\\1","g",$3), $4, gensub(/(.*)\..*/,"\\1","g",$5) }' | cut -f 1 -d " " | sort | uniq >> ips_output.txt
		echo -n "b0:c5:54:42:8f:88 " >> ips_output.txt
		tcpdump -l -n -r $filename ether src b0:c5:54:42:8f:88 | awk '{ print gensub(/(.*)\..*/,"\\1","g",$3), $4, gensub(/(.*)\..*/,"\\1","g",$5) }' | cut -f 1 -d " " | sort | uniq >> ips_output.txt
		echo -n "c4:12:f5:16:40:55 " >> ips_output.txt
		tcpdump -l -n -r $filename ether src c4:12:f5:16:40:55 | awk '{ print gensub(/(.*)\..*/,"\\1","g",$3), $4, gensub(/(.*)\..*/,"\\1","g",$5) }' | cut -f 1 -d " " | sort | uniq >> ips_output.txt
		echo -n "c4:12:f5:16:40:6e " >> ips_output.txt
		tcpdump -l -n -r $filename ether src c4:12:f5:16:40:6e | awk '{ print gensub(/(.*)\..*/,"\\1","g",$3), $4, gensub(/(.*)\..*/,"\\1","g",$5) }' | cut -f 1 -d " " | sort | uniq >> ips_output.txt
		echo -n "c4:12:f5:16:40:3b " >> ips_output.txt
		tcpdump -l -n -r $filename ether src c4:12:f5:16:40:3b | awk '{ print gensub(/(.*)\..*/,"\\1","g",$3), $4, gensub(/(.*)\..*/,"\\1","g",$5) }' | cut -f 1 -d " " | sort | uniq >> ips_output.txt
		echo -n "a0:ab:1b:7c:8b:48 " >> ips_output.txt
		tcpdump -l -n -r $filename ether src a0:ab:1b:7c:8b:48 | awk '{ print gensub(/(.*)\..*/,"\\1","g",$3), $4, gensub(/(.*)\..*/,"\\1","g",$5) }' | cut -f 1 -d " " | sort | uniq >> ips_output.txt
	done
done

# sed -i '/Reply\|Request\|key\|truncated-ip6/d' ips_output.txt
egrep "2020|2021|192" ips_output.txt > ips_output_grepped.txt