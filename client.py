#!/usr/bin/python
#
#   IRC CLIENT PROGRAM 
#


import socket
import sys
import re
import select


#
# USAGE:
# server userlist
# server leave
#
# chatroom create
# chatroom list [<chatroom name>]
# chatroom leave <chatroom name>
# chatroom join <chatroom name>
# chatroom message <chatroom name> <message>
#
def usage():
    print "\nIRC Application"

    print 'USAGE:'
    print "\thelp"
    print "\tserver userlist"
    print "\tserver leave"
    print "\tserver name <username>"
    print "\tchatroom create"
    print "\tchatroom list [<chatroom name>]"
    print "\tchatroom leave <chatroom name>"
    print "\tchatroom join <chatroom name>"
    print "\tchatroom message <chatroom name> <message>"
    print "\tclient message <client name> <message>\n"

def print_msg(msg):
    print ("%s \n" %msg)


# 
# Analyse the data for commands and arguments
#
def validate_data(data):
    if(data is None):
        return 'close'

    valid_chatroom_arg = ['create','list']
    data_arr=data.split(' ')
        
    if (data_arr[0] == 'server'):
            # addressed to server
        if(data_arr[1] == 'leave'):
            return 'close'
        elif(data_arr[1] == 'userlist'):
            return 0
        elif(data_arr[1] == 'name' and len(data_arr)==3):
            return 0
        else:
            return -1
            
    elif (data_arr[0] == 'chatroom'):
            # addressed to chatroom
        if(data_arr[1] in valid_chatroom_arg):
            return 0
        elif((data_arr[1] == 'leave' or data_arr[1] == 'join') and len(data_arr)==3):
            return 0
        elif(data_arr[1] == 'message' and len(data_arr)>=4):
            return 0
        else:
            return -1

    elif (data_arr[0] == 'client'):
        if(data_arr[1] == 'message' and len(data_arr)>=4):
            return 0
        else:
            return -1
              
    elif (data_arr[0] == 'help'):
        usage()
        return 0 
    else:
        return -1


#############MAIN#####################################
def main():

    hostip = socket.gethostbyname('hostname')
    port = 9000
    addr = (hostip, port)
    global socket_list
    global conn
    
   #sysinput = TCPClient(sys.stdin)  
    shutdown = False   

    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 	#create socket
        conn.connect((hostip,port))  # connect with server

    except Exception as e:
        print_msg("Connection Terminating. Closing Client")
        sys.exit(0)

    finally:
        msg=conn.recv(1024)         # receive message from server with username
        print_msg(msg)
        uname = re.search('user[0-9]+',msg)	# extract user name from server's message
        username = uname.group(0)

        while (shutdown == False):
            try:
                socket_list = [sys.stdin, conn]
                read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
                for sock in read_sockets:
                    if(sock == conn):
                        msg = conn.recv(1024)
                        if(not msg or msg == 'exit' or msg == 'close'):
                           shutdown = True
                           print_msg('Server shutdown')
                           break
                        else:
                           print_msg(msg)
 
                    else:
                        line = sys.stdin.readline()
                        line = line.rstrip()
                        sent = validate_data(line)

                        if(sent == 'close'):
                            print_msg("Closing connection")
                            conn.send('server leave')
                            sys.stdout.flush()
                            shutdown = True
                            break
            
                        elif(sent == -1):
                            print_msg('Invalid command provided. Please refer help')
                            usage()
            
                        elif(sent == 0):
                            conn.send(line)
                            sys.stdout.flush()

            except KeyboardInterrupt:
                conn.send('server leave')
                sys.stdout.flush()
                shutdown = True
        
        conn.shutdown(socket.SHUT_RDWR)    
        conn.close()
        sys.exit()


if __name__ == '__main__':
    
    try:
        main()
    except KeyboardInterrupt:
        print_msg('Interrupt received. Closing Client')
        conn.send('server leave')
        sys.stdout.flush()
        conn.shutdown(socket.SHUT_RDWR)    
        conn.close()
        sys.exit(0)


