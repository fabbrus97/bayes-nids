from scapy.all import *
import json
import os
import random
from datetime import datetime

#data in normal traffic dataset was captured from
#9th September 2020 to 10th January 2021
START=1602194400
END=1610233200


map = json.load(open("mac_ips.json"))
macs = list(map["mac_ips"].keys())
ips_real = map["ips"]
ips_fake = ["172.16.238.50", "172.16.238.51", "172.16.238.52", "172.16.238.53", "172.16.238.54", "172.16.238.55", 
            "172.16.238.56", "172.16.238.57", "172.16.238.58", "172.16.238.59", "172.16.238.60", "172.16.238.61"]

available_dates = list(map["dates"].keys())

def get_random_date():
    real_date = random.choice(available_dates)
    while len(map["dates"][real_date].values()) < 8:
        real_date = random.choice(available_dates)
    available_dates.remove(real_date)
    return real_date

def get_older_ts(fake_timestamp, real_date):
    real_date = datetime.date(datetime.fromisoformat(real_date))
    fake_time = datetime.time(datetime.fromtimestamp(fake_timestamp))
    date = datetime.combine(real_date, fake_time)
    return date.timestamp()





for root, subdirs, _ in os.walk("attack_pcap"):
    ips_map = {}
    
    subdir_counter = 1
    for subdir in subdirs:
        files = os.listdir(os.path.join(root, subdir))
        new_date = get_random_date()
        ips_map = map["dates"][new_date]
        file_counter = 1
        for file in files:
            
            print(f"computing file {file_counter}/{len(files)} in subdir {subdir_counter}/{len(subdirs)}")
            file_counter += 1

            mypcap=rdpcap(os.path.join(root, subdir, file))
            print("loading done")
            index = 0
            while index < len(mypcap):
                print("packet", index+1, "of", len(mypcap), end="\r")
                p = mypcap[index]
                #change time
                p.time = get_older_ts(float(p.time), new_date)
                #change ip address
                if "Ether" in p and "IP" in p:
                    if p["IP"].dst == "172.16.238.1" or p["IP"].src == "172.16.238.1":
                        mypcap.remove(p)
                        continue
                    else:
                        src_mac = p["Ether"].src
                        dst_mac = p["Ether"].dst
                            
                        for mac in [src_mac, dst_mac]:
                            if mac in macs:
                                if mac not in ips_map.keys():
                                    ips_map[mac] = [random.choice(ips_real)]
                                    #check if ip is already assigned, and in case it is change it
                                    unique = False
                                    while not unique:
                                        for m, i in ips_map.items():
                                            if m == mac:
                                                continue
                                            if i == ips_map[mac]:
                                                ips_map[mac] = [random.choice(ips_real)]
                                                break
                                            unique = True
                                
                        if src_mac in macs:
                            p["IP"].src = ips_map[src_mac][0]
                        if dst_mac in macs:
                            p["IP"].dst = ips_map[dst_mac][0]
                
                index += 1

            print("FINAL mypcap length:", len(mypcap))
            wrpcap("test_change_ts.pcap", mypcap)

        subdir_counter += 1       

