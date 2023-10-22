@load ./featureUtils.zeek 
@load ./queueUtils.zeek
@load base/protocols/conn/main.zeek
@load base/bif/plugins/Zeek_Login.events.bif.zeek
# @load ./login.zeek

module AdditionalFeatures;

global conn_counter: count = 100;
global uid_set: set[string]; 

redef LogAscii::include_meta = F;
redef LogAscii::separator = ",";
redef LogAscii::set_separator = ";";
redef LogAscii::unset_field = "";



export {
	redef enum Log::ID += { ADDLOG };

	type Additional: record {
	    #framework feature:
	    uid:				string  &log;
	    ts:					time    &log;
	    #general purpose features
	    is_sm_ips_ports:	count	&log	&optional;
	    ct_state_ttl:		count 	&log	&optional;
	    ct_flw_http_mthd:	count   &log	&optional;
	    is_ftp_login:		count	&log	&optional;
	    ct_ftp_login:		count   &log	&optional;
	    #connection features		
	    ct_srv_src:			count   &log	&optional;
	    ct_srv_dst:			count   &log	&optional;
	    ct_dst_ltm:			count   &log	&optional;
	    ct_src_ltm:			count   &log	&optional;
	    ct_src_dport_ltm:	count   &log	&optional;
	    ct_dst_sport_ltm:	count   &log	&optional;
	    ct_dst_src_ltm:		count   &log	&optional;

		#previous features come from NB15, these are my additions
	    is_telnet_login:	count	&log	&optional;

	};
}


event new_packet(c: connection, p: pkt_hdr){

	local duplicate = c$uid in uid_set;

	local is_sm_ips_ports: count;
	local ct_state_ttl: count;
	local ct_flw_http_mthd: count = 0;
	local is_ftp_login: count = 0; 
	local ct_ftp_login: count = 0; 
	local ct_srv_src: count; 
	local ct_srv_dst: count; 
	local ct_dst_ltm: count; 
	local ct_src_ltm: count; 
	local ct_src_dport_ltm: count; 
	local ct_dst_sport_ltm: count; 
	local ct_dst_src_ltm: count; 
	local is_telnet_login: count = 0; 
	

	is_sm_ips_ports = feat_is_sm_ips_ports(c);
	ct_state_ttl = feat_ct_state_ttl(c, p, conn_counter, duplicate);
	ct_srv_src = feat_ct_srv_src(c, conn_counter, duplicate);
	ct_srv_dst = feat_ct_srv_dst(c, conn_counter, duplicate);
	ct_dst_ltm = feat_ct_dst_ltm(c, conn_counter, duplicate);
	ct_src_ltm = feat_ct_src_ltm(c, conn_counter, duplicate);
	ct_src_dport_ltm = feat_ct_src_dport_ltm(c, conn_counter, duplicate);
	ct_dst_sport_ltm = feat_ct_dst_sport_ltm(c, conn_counter, duplicate);
	ct_dst_src_ltm = feat_ct_dst_src_ltm(c, conn_counter, duplicate);
	
	if (c?$http){

		# print fmt("http! %s %s", c$uid, c$http$method);

		# local starttime: time = double_to_time(1608695300.0);
		# local endtime: time = double_to_time(1608695400.0);

		# if (c$start_time <= endtime && c$start_time >= starttime){
		# # if (c$start_time == double_to_time(1608695309.901032)){
		# 	print fmt("uid: %s, ts: %s", c$uid, c$start_time);
		# }

		local ttl: count = p?$ip ? p$ip$ttl : p$ip6$hlim ;
		
		ct_flw_http_mthd = feat_ct_flw_http_mthd(c$http, conn_counter, duplicate); 

	} else if (c?$ftp){
		is_ftp_login = feat_is_ftp_login(c$ftp);
		ct_ftp_login = feat_ct_ftp_login(c$ftp, conn_counter);

	} 

		Log::write( AdditionalFeatures::ADDLOG, [
			$uid = c$uid, 
			$ts = c$start_time, # + c$duration,
			$is_sm_ips_ports = is_sm_ips_ports,
			$ct_state_ttl = ct_state_ttl,
			$ct_flw_http_mthd = ct_flw_http_mthd,
			$is_ftp_login = is_ftp_login,
			$ct_ftp_login = ct_ftp_login,
			$ct_srv_src = ct_srv_src,
			$ct_srv_dst = ct_srv_dst,
			$ct_dst_ltm = ct_dst_ltm,
			$ct_src_ltm = ct_src_ltm,
			$ct_src_dport_ltm = ct_src_dport_ltm,
			$ct_dst_sport_ltm = ct_dst_sport_ltm,
			$ct_dst_src_ltm = ct_dst_src_ltm,
			$is_telnet_login = is_telnet_login]);


	if (c$uid !in uid_set){
		if (|uid_set| > 1000) #reset
			uid_set = set();
		add uid_set[c$uid];
		conn_counter = conn_counter > 0 ? conn_counter-1 : 100; 
	}

	
	
}

const login_failure_msgs: set[string] = {
  "invalid",
  "Invalid",
  "incorrect",
  "Incorrect",
  "failure",
  "Failure",
  # "Unable to authenticate",
  # "unable to authenticate",
  "User authorization failure",
  "Login failed",
  "Login incorrect",
  "INVALID",
  "Sorry.",
  "Sorry,",
} &redef;


#for telnet
event authentication_accepted(name: string, c: connection){
	print "AUTH EVENT TELNET ACC";
	Log::write( AdditionalFeatures::ADDLOG, [$uid = c$uid, $ts=c$start_time, $is_telnet_login = 1]);
}

event authentication_rejected(name: string, c:connection){
	print "AUTH EVENT TELNET REJ";
}
event login_failure(c: connection, user: string, client_user: string, password: string, line: string){
	print "AUTH EVENT TELNET REJ";
	#Log::write( AdditionalFeatures::ADDLOG, [$uid = c$uid, $ts=c$start_time, $pis_telnet_login = 2]);
}



event login_output_line(c: connection, line: string){
	print fmt("TELNET OUT EVENT: %s", line);
}
event login_input_line(c: connection, line: string){
	print fmt("TELNET IN EVENT: %s", line);
}

event zeek_init(){
	local telnet = { 23/tcp };

	Log::create_stream(ADDLOG, [$columns=Additional, $path="additional_features"]);
	#Log::create_stream(Login::Log_LOGIN, [$columns=Login::Info, $path="login"]);

	Analyzer::register_for_ports(Analyzer::ANALYZER_TELNET, telnet );
	
	# Log::disable_stream(Conn::LOG);
	# Log::disable_stream(HTTP::LOG);
	# Log::disable_stream(FTP::LOG);
}



