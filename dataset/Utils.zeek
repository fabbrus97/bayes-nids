#module Utils;

#export {

    global cnt_ftp_flows_w_cmd: set[string] = {};
    global http_counter: count = 0; 
    global cnt_sm_srv_src: table[string] of count; # = table();

    #feature 36
    function feat_is_sm_ips_ports(conn: Conn::Info): bool
    {
        return conn$id$orig_h == conn$id$resp_h && conn$id$orig_p == conn$id$resp_p;
    }

    #feature 37
    function feat_ct_state_ttl(conn: Conn::Info): count{
        
    }
    
    #feature 38
    function feat_ct_flw_http_mthd(conn: HTTP::Info, conn_counter: count): count
    {
        conn_counter = conn_counter > 0 ? conn_counter : 0;
        if (conn_counter > 0 && (conn$method == "POST" || conn$method == "GET")){
            http_counter += 1;
        } 
    }
    
    #feature 39
    function feat_is_ftp_login(conn: FTP::Info): bool{
	if (conn?$user)
		print fmt("ftp login user: %s", conn$user);
	else
		print "ftp no user provided";
	if (conn?$password)
		print fmt("ftp login pwd: %s", conn$password);
	else
		print "ftp no pwd provided";
        return conn?$user && conn?$password && conn$user == "anonymous" && conn$password == "anonymous";
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
    function feat_ct_srv_src(conn: Conn::Info, conn_counter:count): count{
        if (!conn?$service){
		return 0;
	}
	local key: string = fmt("%s:%s", conn$service, conn$id$orig_h);
        if (conn_counter == 100){
            cnt_sm_srv_src = table( [key] = 1 );
        } else if (key in cnt_sm_srv_src){
            cnt_sm_srv_src[key] += 1;
        } else {
            cnt_sm_srv_src[key] = 1;
        }

        return cnt_sm_srv_src[key];
    }
    
    #feature 42
    function feat_ct_srv_dst(conn: Conn::Info, conn_counter: count): count{
        if (!conn?$service){
		return 0;
	}
        local key: string = fmt("%s:%s", conn$service, conn$id$resp_h);
        if (conn_counter == 100){
            cnt_sm_srv_src = table( [key] = 1 );
        } else if (key in cnt_sm_srv_src){
            cnt_sm_srv_src[key] += 1;
        } else {
            cnt_sm_srv_src[key] = 1;
        }

        return cnt_sm_srv_src[key];
    }
    
    #feature 43
    function feat_ct_dst_ltm(conn: Conn::Info): count{
        
    }
    
    #feature 44
    function feat_ct_src_ltm(conn: Conn::Info): count{
        
    }
    
    #feature 45
    function feat_ct_src_dport_ltm(conn: Conn::Info): count{
        
    }
    
    #feature 46
    function feat_ct_dst_sport_ltm(conn: Conn::Info): count{
        
    }
    
    #feature 47
    function feat_ct_dst_src_ltm(conn: Conn::Info): count{
        
    }

#}
