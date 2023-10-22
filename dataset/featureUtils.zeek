#module Utils;

#export {

    global cnt_ftp_flows_w_cmd: set[string] = {};
    global http_counter: count = 0; 
    const  ttl_window  = vector(55, 105, 155, 205, 255); 
    global ttl_counter: table[string] of table[count] of vector of count = table(); #e.g. icmp: 3: (0,    0,  0,   0,   0,   0,   0);
    global cnt_conn_features: table[string] of count = table();

    function add_table(key: string, conn_counter: count, duplicate: bool): count{
        cnt_conn_features = conn_counter > 0 ? cnt_conn_features : table([key] = 0);
        
        if (key !in cnt_conn_features)
            cnt_conn_features[key] = 0;

        if (!duplicate)
            cnt_conn_features[key] += 1;

        return cnt_conn_features[key];
    }

    #feature 36
    function feat_is_sm_ips_ports(conn: connection): count
    {
        local val = conn$id$orig_h == conn$id$resp_h && conn$id$orig_p == conn$id$resp_p;
        return val ? 1 : 2;
    }

    #feature 37
    function feat_ct_state_ttl(c: connection, p: pkt_hdr, conn_counter: count, duplicate: bool): count{

        ttl_counter = conn_counter > 0 ? ttl_counter : table();


        local protocol: string = "none"; #conn?$service ? conn$service: "none" ; #TODO change protocol with state (acc, rej, ...)
        local status: count = 0;
        local ttl: count = 0;
        if (p?$tcp ){
            protocol = "tcp";
        } else if (p?$udp){
            protocol = "udp";
        } else if (p?$icmp){
            protocol = "icmp";
            status = p$icmp$icmp_type;
            ttl = p?$ip ? p$ip$ttl : p$ip6$hlim ;
        }

        if (p?$ip){
            ttl = p$ip$ttl;
            status = c$orig$state;
        } else if (p?$ip6){
            ttl = p$ip6$hlim; 
            status = c$orig$state; #c$resp$state
        } 
        
        if (!(protocol in ttl_counter)){
            ttl_counter[protocol] = table();
            ttl_counter[protocol][status] = vector(0,0,0,0,0,0);
        } else {
            if (!(status in ttl_counter[protocol])){
                ttl_counter[protocol][status] = vector(0,0,0,0,0,0);
            }
        }

        # print fmt("there are %d stati for protocol %s", |ttl_counter[protocol]|, protocol);

        if (ttl>ttl_window[-1]){
            if (!duplicate)
                ttl_counter[protocol][status][6] += 1;
            return ttl_counter[protocol][status][5];
        } else {
            for (index in ttl_window){
                if (ttl <= ttl_window[index]){
                    if (!duplicate)
                        ttl_counter[protocol][status][index] += 1;
                    return ttl_counter[protocol][status][index];
                }
            }
        }

        
    }
    
    #feature 38
    function feat_ct_flw_http_mthd(conn: HTTP::Info, conn_counter: count, duplicate: bool): count
    {
        http_counter = conn_counter > 0 ? http_counter : 0;
	if (!conn?$method)
	    return http_counter;
        if (conn_counter > 0 && (conn$method == "POST" || conn$method == "GET")){
            if (!duplicate)
                http_counter += 1;
        }
        return http_counter;
    }
    
    #feature 39
    function feat_is_ftp_login(conn: FTP::Info): count{
	# if (conn?$user)
	# 	print fmt("ftp login user: %s", conn$user);
	# else
	# 	print "ftp no user provided";
	# if (conn?$password)
	# 	print fmt("ftp login pwd: %s", conn$password);
	# else
	# 	print "ftp no pwd provided";
        local val = conn?$user && conn?$password && conn$user == "anonymous" && conn$password == "anonymous";
        return val ? 1 : 2;
    }
    
    #feature 40
    function feat_ct_ftp_login(conn: FTP::Info, conn_counter: count): count{
        cnt_ftp_flows_w_cmd = conn_counter > 0 ? cnt_ftp_flows_w_cmd : set();
        if (conn?$command){
            add cnt_ftp_flows_w_cmd[conn$uid]; #not added if already present
        }
        return |cnt_ftp_flows_w_cmd|; 
    }
    
    #feature 41
    function feat_ct_srv_src(conn: connection, conn_counter:count, duplicate: bool): count{
        if (!conn?$service){
		    return 0;
	    }

    	local key: string = fmt("%s:%s", conn$service, conn$id$orig_h);

        return add_table(key, conn_counter, duplicate); 

    }
    
    #feature 42
    function feat_ct_srv_dst(conn: connection, conn_counter: count, duplicate: bool): count{
        if (!conn?$service){
		    return 0;
	    }

        local key: string = fmt("%s:%s", conn$service, conn$id$resp_h);

        return add_table(key, conn_counter, duplicate); 
    }
    
    #feature 43
    function feat_ct_dst_ltm(conn: connection, conn_counter: count, duplicate: bool): count{
        return add_table(fmt("%s", conn$id$resp_h), conn_counter, duplicate); 
    }
    
    #feature 44
    function feat_ct_src_ltm(conn: connection, conn_counter: count, duplicate: bool): count{
        return add_table(fmt("%s", conn$id$orig_h), conn_counter, duplicate); 
    }
    
    #feature 45
    function feat_ct_src_dport_ltm(conn: connection, conn_counter: count, duplicate: bool): count{
        local key: string = fmt("%s:%s", conn$id$orig_h, conn$id$resp_p);
        
        return add_table(key, conn_counter, duplicate); 
    }
    
    #feature 46
    function feat_ct_dst_sport_ltm(conn: connection, conn_counter: count, duplicate: bool): count{
        local key: string = fmt("%s:%s", conn$id$resp_h, conn$id$orig_p);
        
        return add_table(key, conn_counter, duplicate); 

    }
    
    #feature 47
    function feat_ct_dst_src_ltm(conn: connection, conn_counter: count, duplicate: bool): count{
        local key: string = fmt("%s:%s", conn$id$orig_h, conn$id$resp_h);

        return add_table(key, conn_counter, duplicate); 
    }

#}
