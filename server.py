#!/usr/bin/python
#
#   IRC SERVER PROGRAM
#


import socket
import sys
import re
import select


def print_msg(msg):
    print ("%s \n" %msg)


#
# send message to a connection
#
def send_msg(message, conn):
    conn.send(message)


#
# broadcast message to a group
# def group_msg(<userlist>, <message>, <sender_socket>, <group_name>)
#
def group_msg(users, message, sock, group):
    global socket_list
    uname = socket_list[sock]
    message = uname + ': ' + message
    if(group != None):
        message = group + ':' + message
    
    for destsock, destuname in socket_list.iteritems():
        if(destuname in users and destuname != uname and destuname != 'ipsock'):
            send_msg(message, destsock)



#
# Communication with server function
#
def cmm_server(client_cmd, sock):
    global socket_list
    
    uname = socket_list[sock]
    if (client_cmd[1]=='userlist'):     # List of users connected to the server
        userlist = socket_list.values()
        userlist.remove('server')
        userlist.remove('ipsock')
        msg = ''
        for u in userlist:
            msg = msg + u + ', '
        msg = msg.rstrip(', ')
        send_msg(msg,sock)

    elif (client_cmd[1]=='leave'):      # Client is leaving server
        print_msg("Connection closed for %s" %uname)
        client_close(sock)
        group_msg(socket_list.values(), uname + ' disconnected', server, None)  # broadcast message to all users when new user joins

    elif (client_cmd[1] == 'name'):
        if(client_cmd[2] in socket_list.values()):
            send_msg('This username is already taken. Please try a different name',sock)
        else:
            socket_list[sock] = client_cmd[2]
            send_msg("Your new name is %s" %client_cmd[2],sock)


def print_group(roomname):
    global chatroom 
    msg = roomname + ' -> '

    for u in chatroom[roomname]:
        msg = msg + u + ', '
    return msg.rstrip(', ')

#
# Communication with server function
#
def cmm_chatroom(client_cmd, sock):
    global chatroom
    global roomnum
    global socket_list
    flag = 0
    uname = socket_list[sock]

    if(client_cmd[1] == 'create'):          # create chatroom
        if(len(client_cmd) == 3):          # if chatroom is specified, create chatroom with given name.
            if(client_cmd[2] in chatroom.keys()):
                send_msg('This chatroom already exists. You may want to join it',sock)
                flag = 1
            else:        
                roomname = client_cmd[2]
        else:
            roomname = 'chatroom' + str(roomnum)
            roomnum = roomnum + 1
            
        if(flag == 0):
            print_msg("created chatroom %s" %roomname)
            chatroom[roomname] = []
            chatroom[roomname].append(uname)
            msg = "created chatroom %s" %roomname
            send_msg(msg,sock)

    elif(client_cmd[1] == 'list'):          # return the list of chatrooms to the client
        if(len(client_cmd) == 2):          # if no chatroom is listed, then return all the chatrooms to the client.
            #print_msg("listing all the chatrooms:")
            grp = ''
            for k in chatroom.keys():
                grp = grp + print_group(k) + "\n"
            grp = grp.rstrip()
            send_msg(grp,sock)
        
        elif(client_cmd[2] in chatroom.keys()):     # list only the specified chatroom
            send_msg(print_group(client_cmd[2]),sock)
        
        else:                                       # incorrect chatroom is listed, then error out
            send_msg("Incorrect chatroom specified",sock)

    elif(client_cmd[1] == 'join'):          # join the client to the specified chatroom

        if(client_cmd[2] not in chatroom.keys()):
            send_msg("This chatroom does not exist",sock)

        elif(uname in chatroom[client_cmd[2]]):
            send_msg("You are already a part of this chatroom",sock)

        else:
            msg = uname + " joined chatroom " + client_cmd[2]   # notify users in the group, when a member joins
            group_msg(chatroom[client_cmd[2]], msg, server, None)

            chatroom[client_cmd[2]].append(socket_list[sock])
            msg = "Joined chatroom %s" %client_cmd[2]
            send_msg(msg, sock)

    elif(client_cmd[1] == 'leave'):         # remove client from specified chatroom
        if(client_cmd[2] in chatroom.keys()):           # check if the specified chatroom exists
            if(uname in chatroom[client_cmd[2]]):
                chatroom[client_cmd[2]].remove(uname)

                msg = uname + " left chatroom " + client_cmd[2]   # notify users in group when a member leaves
                group_msg(chatroom[client_cmd[2]], msg, server, None)
            else:
                send_msg('You are not participating in this chatroom',sock)
            
            if(len(chatroom[client_cmd[2]]) == 0):      # If there are no users in the chatroom, delete it
                del chatroom[client_cmd[2]]
            msg = "Left chatroom %s" %client_cmd[2]
            send_msg(msg,sock)
        
        else:
            send_msg('This chatroom does not exist',sock)

        #chatroom message chatroom1 hello world
    elif(client_cmd[1] == 'message'):       # send message to all the users in the group
        if(client_cmd[2] in chatroom.keys() and (uname in chatroom[client_cmd[2]])):
            group_msg(chatroom[client_cmd[2]], client_cmd[3], sock, client_cmd[2])

        elif(client_cmd[2] not in chatroom.keys()):
            send_msg('This chatroom does not exist',sock)
        
        elif(uname not in chatroom[client_cmd[2]]):
            send_msg('You are not participating in this chatroom',sock)


#
# Communication with a specific user function
#
def cmm_user(client_cmd, sock):
    global socket_list
    uname = socket_list[sock]

    if(client_cmd[1] == 'message'):          # message a client
        if(client_cmd[2] == uname):
          send_msg('You are sending message to yourself, not allowed',sock) 
 
        elif(client_cmd[2] in socket_list.values() and (client_cmd[2] != 'server' or client_cmd[2] != uname or client_cmd[2] != 'ipsock')):
            msg = uname + ': ' + client_cmd[3]

            for destsock, destuname in socket_list.iteritems():
                if(destuname == client_cmd[2]):
                   # print_msg(msg)
                    send_msg(msg, destsock)
                    break
        else:
            send_msg('Incorrect user name mentioned',sock)


#
# Validate the stdinput lines.
#
def validate_data(data):
    
    if(data is None):
        return 'close' 
    if(data == 'shutdown'):
        return 'close'
    
 
#
# Analyse received data for commands and arguments
#
def analyse_data(data, sock):

    data_arr=data.split(' ', 3)

    if (data_arr[0] == 'server'):   # addressed to server
        cmm_server(data_arr, sock)
        return 0
    elif (data_arr[0] == 'chatroom'):   # addressed to chatroom
        cmm_chatroom(data_arr, sock)
        return 0
    elif (data_arr[0] == 'client'):   # addressed to a specific user
        cmm_user(data_arr, sock)
        return 0

# 
# Close client connection
#
def client_close(sock):
    global chatroom

    for key, value in chatroom.iteritems():         # remove the user from the all the chatrooms
        if(socket_list[sock] in value):
            value.remove(socket_list[sock])
    chatroom = {k:v for k,v in chatroom.iteritems() if v}
    uname = socket_list[sock]
    del socket_list[sock]
    print_msg("%s closed connection" %uname)
    sock.close()


#
# close server socket
#
def server_close(sock):
    print_msg('Closing Server')
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


def shutdown():

    for s in socket_list.keys():
        if(s != server and socket_list[s] != 'ipsock'):
            #s.send('exit')
            s.close()
            del socket_list[s]
    server_close(server)
    sys.exit()



#########MAIN###########
def main():

    hostip = socket.gethostbyname('hostname')
    port = 9000
    server_addr = (hostip,port)
    global number
    global roomnum
    global chatroom
    global server
    global socket_list


    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        #print_msg('Created socket')

        #print "Starting server on %s port %s" %server_addr
        server.bind(server_addr) 				# bind socket with hostname and port no.
        print_msg("Started server")

    except Exception as e:
        print_msg('Error in creating socket')
        sys.exit(0)

    finally:
        #print 'Starting to accept connection'
        server.listen(10)					# start listening its port for clients

        socket_list = {server : 'server', sys.stdin : 'ipsock'}
        number = 1
        roomnum = 1

        chatroom = {}  # dictionary of chatroom associated with list of users
        useraddr = {}


        while (1):
            try:
                read_sockets,write_sockets,error_sockets = select.select(socket_list.keys(),[],[])

                for sock in read_sockets:
                    if(sock == server):
                        client, address = sock.accept()
                        if(client not in socket_list.values()):
                            uname = 'user' + str(number)			# assign user number to the incoming user
                            msg = 'Connected. Username is %s' %uname
                            
                            group_msg(socket_list.values(), uname + " connected", server, None)  # broadcast message to all users when new user joins
                            
                            socket_list[client] = uname
                            number = number + 1
                            print_msg("%s connected : (%s, %s)" %(uname,address[0],address[1]))
                            client.send(msg)
                    elif(socket_list[sock] == 'ipsock'):
                        line = None
                        line = sys.stdin.readline()
                        line = line.rstrip()
                        to_send = validate_data(line)
                        if(to_send == 'close'):
                            group_msg(socket_list.values(), "Shutting down", server, None)  # broadcast message to all users when shutting down
                            shutdown()
                    else:
                        try:
                            data = sock.recv(1024)
                        except Exception as e:
                            print_msg('Terminating')
                            sock.close()
                            del socket_list[sock]
                            break

                        finally:
                            if(data == None or data == ''):
                                data = "server leave"
                            else:
                                data = data.rstrip()              # remove the trailing new line char
                                ret = analyse_data(data,sock)

            except KeyboardInterrupt:
                shutdown()

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print_msg('Closing Server')
        shutdown()
