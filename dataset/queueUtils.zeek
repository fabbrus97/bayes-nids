global connQueue: vector of Conn::Info = vector();
global HTTPQueue: vector of HTTP::Info = vector();
global FTPQueue: vector of FTP::Info = vector();

function sortConn(a: Conn::Info, b: Conn::Info): int{
    return a$ts > b$ts ? 1 : -1;
}

function sortHTTP(a: HTTP::Info, b: HTTP::Info): int{
    return a$ts > b$ts ? 1 : -1;
}

function sortFTP(a: FTP::Info, b: FTP::Info): int{
    return a$ts > b$ts ? 1 : -1;
}

function getItem(): any{
    # print "getting item...";

    # local starting_time: time = current_time();
    # sort(connQueue, sortConn);
    # sort(HTTPQueue, sortHTTP);
    # sort(FTPQueue, sortFTP);
    # local ending_time: time = current_time();
    # print fmt("total time to sort queue: %f seconds", ending_time - starting_time);


    local maxtime: time = current_time();    
    local firstConn = |connQueue| > 0 ? connQueue[0]$ts : maxtime;
    local firstFTP = |FTPQueue| > 0 ? FTPQueue[0]$ts : maxtime;
    local firstHTTP =  |HTTPQueue| > 0 ? HTTPQueue[0]$ts : maxtime;
	
    # print fmt("firstConn: %D, firstHTTP: %D, firstFTP: %D", firstConn, firstHTTP, firstFTP);

    local _conn: any;

    if ( firstConn < firstFTP && firstConn < firstFTP){
	_conn = copy(connQueue[0]);
	connQueue = connQueue[1:];
        return _conn;
    } else if ( firstFTP < firstConn && firstFTP < firstHTTP){
	_conn = copy(FTPQueue[0]);
        FTPQueue = FTPQueue[1:];
        return _conn;    
    } else {
        _conn = copy(HTTPQueue[0]);
        HTTPQueue = HTTPQueue[1:];
        return _conn;
    }
}

#return true if the queue is "full" (ready to be elaborated)
function addQueue(conn: any): bool{
	if (conn is Conn::Info){
        connQueue += conn as Conn::Info;
	} else if (conn is HTTP::Info){
		HTTPQueue += conn as HTTP::Info;
	} else if (conn is FTP::Info){
		FTPQueue += conn as FTP::Info;
	}

	#Since packets do not arrive in order, it is possible that the 101st, 102nd... packets
	# have a timestamp lower than the one of the 100th; so, if we just order 100 packets, we 
	# would put the 101, 102... in a new list, when they should have been put in the previous list.
	# for this reason, 125 packets are collected and the first 100 (after sorting the list) are 
	# used. It is unlikely that the 26th packet belongs to the old list.
	if (|connQueue| + |HTTPQueue| + |FTPQueue| == 2000){ #TODO use a variable MAX_QUEUE_SIZE
        #TODO 125 with print: 6-7 seconds; 1250 with print: ~70 seconds (about 80% of packets)
        #     125 without print: 4-5 seconds; 1250 without print: 46 seconds
        #     2000 without print: 82 seconds (90% of packets)
		return T; 
	}
    return F; 

}
