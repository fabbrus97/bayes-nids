import json

with open("ips_output_grepped.txt") as ips_file:
    lines = ips_file.readlines()
    lines = [l[:-1] for l in lines]

    map = {
        "dates": {},
        "mac_ips": {},
        "ips": list()
    }
    
    ip_list = set()

    CUR_DATE = ""
    CUR_MAC = ""
    counter = 1
    for line in lines:
        print(counter, "/", len(lines))
        counter += 1
        try:
            # print("LINE:", line)
            if line.find("2020") > -1 or line.find("2021") > -1:
                line = line.split(" ")
                line = line[-1]
                CUR_DATE = line
                map["dates"][CUR_DATE] = {}
            else:
                #lets consume the mac addresses to find an ip
                
                if not line.find("170") > -1:
                    #the line does not contain an ip address
                    continue
                
                line = line.split(" ")

                if len(line) > 1:
                    CUR_MAC = line[-2]
                    map["dates"][CUR_DATE][CUR_MAC] = []
                
                line = line[-1]
                if len(line.split(".")) < 4:
                    #malformed ip
                    continue
                
                # print("date:", CUR_DATE, "mac:", CUR_MAC, "line:", line)
                # print("map:", map)

                #adding the ip address to the map
                map["dates"][CUR_DATE][CUR_MAC].append(line)
                ip_list.add(line)
        except:
            pass
    
    for _, val in map["dates"].items():
        for mac, ips in val.items():
            if mac not in map["mac_ips"]:
                map["mac_ips"][mac] = set()
            for ip in val[mac]:
                map["mac_ips"][mac].add(ip)
            # print(map["mac_ips"])

    for mac in map["mac_ips"].keys():
        map["mac_ips"][mac] = list(map["mac_ips"][mac])
    map["ips"] = list(ip_list)

    json.dump(map, open("mac_ips.json", "w"), indent=2)
