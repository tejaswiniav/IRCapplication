# IRC python application

# Introduction
Internet Relay Chat (IRC) is a chat application modeled for multi user teleconferencing. It is a client-server application and uses TCP protocol for communication. Users are clients. In order for the clients to connect with each other, they have to be connected to the server all the time. Thus, clients communicate via server. It is responsible for maintaining the communication link between the clients.
This application lets users to communicate in chat rooms and also in private.  Users can talk to each other via exchange of text messages. Users can participate in multiple chat rooms.

## Server
It is the central connection point for the application. The clients can talk to each other by connecting to the server. In order for the application to run, server has to stay up all the time.
## Client
They are hosts or users participants of the application. Each client is identified by a unique username. They may communicate with other participating clients via chat rooms or private chats.
## Chat Room
Chat room is a group where multiple users can join and communicate with each other. Like client, even a chat room has a unique name. A client broadcasts message to all the clients participating in the chat room. The chat room must contain at least one client. It can be created by a client and joined by others using its unique name.
