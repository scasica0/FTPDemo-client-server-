# *****************************************************
# Description:   Client for FTP server
# *****************************************************

import socket 
import sys
import commands
import os

def get_function(clientSocket,host,port,fileName):
    # Send get command
    sendMsg (clientSocket, "get")

    # Send fileName
    sendMsg (clientSocket, fileName)

    # wait for confirmation if desired file exists
    confirmation = ""
    confirmation = clientSocket.recv(1)

    # continue if file exists
    if confirmation != 'y':
        print 'ERROR- the file: "', fileName, '" does not exist on server'
 
    else:

        # Generate emphemeral port
        welcomeSocket = emphemeral()

        # Wait for server to connect
        welcomeSocket.listen(1)

        print "Waiting for data connection..."

        # Send server emphemeral port number
        portNumberBuff = ""
        portNumberBuff = welcomeSocket.getsockname()[1]
        portNumber = str(portNumberBuff)
        sendMsg (clientSocket, portNumber)
            
        # Accept connections
        serverSocket, addr = welcomeSocket.accept()
        
        print "Accepted data connection from server: ", addr

        # Receive the file
        # The buffer to all data received from the client.
        fileData = ""
        
        # The temporary buffer to store the received data.
        recvBuff = ""
        
        # The size of the incoming file
        fileSize = 0    
        
        # The buffer containing the file size
        fileSizeBuff = ""
          
        # Create the new file    
        fileObj = open(fileName, "w") 

        # Receive the first 10 bytes indicating the size of the file
        fileSizeBuff = recvHeader(serverSocket, 10)
        
        # Get the file size
        fileSize = int(fileSizeBuff)

        # Receive the file
        recvBuff = recvHeader(serverSocket,fileSize)

        # save the receive buffer into fileData
        fileData = recvBuff
        
        # write the data received to the file
        fileObj.write(fileData)

        # Close the sockets and the file
        welcomeSocket.close()
        serverSocket.close()
        fileObj.close()

        print 'Received: ' , fileName
        print 'Total size received: (', len(fileData), ' bytes)'
        
def put_function(clientSocket,host,port,fileName):
    # Send put command
    sendMsg (clientSocket, "put")

    # Send fileName
    sendMsg (clientSocket, fileName)

    # check if fileName is valid
    if not os.path.isfile(fileName):
        # file does not exist
        print 'ERROR- ', fileName, ' does not exist'
        clientSocket.send('n')

    else:
        # tell client that file is valid and continue
        clientSocket.send('y')

        # Generate emphemeral port
        welcomeSocket = emphemeral()

        # Wait for server to connect
        welcomeSocket.listen(1)

        print "Waiting for data connection..."

        # Send server emphemeral port number
        portNumberBuff = ""
        portNumberBuff = welcomeSocket.getsockname()[1]
        portNumber = str(portNumberBuff)
        sendMsg (clientSocket, portNumber) 
            
        # Accept connections
        serverSocket, addr = welcomeSocket.accept()
        
        print "Accepted data connection from server: ", addr

        # Open the file
        fileObj = open(fileName, "r")

        # The number of bytes sent
        bytesSent = 0

        # The file data
        fileData = None

        # Keep sending until all is sent
        while True:
        
            # Read 65536 bytes of data
            fileData = fileObj.read(65536)
        
            # Make sure we did not hit EOF
            if fileData:
                
                # Get the size of the data read and convert it to string
                dataSizeStr = str(len(fileData))
            
                # Prepend 0's to the size string until the size is 10 bytes
                while len(dataSizeStr) < 10:
                    dataSizeStr = "0" + dataSizeStr
        
                # Prepend the size of the data to the file data.
                fileData = dataSizeStr + fileData    
            
                # The number of bytes sent
                bytesSent = 0
            
                # Send the data
                while len(fileData) > bytesSent:
                    bytesSent += serverSocket.send(fileData[bytesSent:])
        
            # The file has been read
            else:
                break

        print 'Sent ', fileName
        print 'Total size sent: (', bytesSent, ' bytes)'
        
        # Close the sockets and the file
        serverSocket.close()
        fileObj.close()
        welcomeSocket.close()

def ls_function(clientSocket,host,port):
    # Send lls command
    sendMsg (clientSocket, "ls")

    # The size of the incoming data
    dataSize = 0    
    
    # The buffer containing the data size
    dataSizeBuff = ""

    # The temporary buffer to store the received data.
    recvBuff = ""

    # The buffer to all data received from the client.
    serverDirectory = ""
    
    # Receive the first 10 bytes indicating the size of the file
    dataSizeBuff = recvHeader(clientSocket, 10)

    # Get the file size
    dataSize = int(dataSizeBuff)

    while len(serverDirectory) != dataSize:
        # Receive what client has sent
        recvBuff = clientSocket.recv(dataSize)

        # The other socket has unexpectedly closed its socket
        if not recvBuff:
            break

        # Save the file data
        serverDirectory += recvBuff
    
    # Print the server's directory
    print 'Server Directory:'
    print serverDirectory
    

def lls_function():
    # Run ls command, get output, and print it
    print 'Client Directory:'
    for line in commands.getstatusoutput('ls -l'):
        print line
    

def quit_function(clientSocket): #COMPLETE
    # Send quit command
    sendMsg (clientSocket, "quit")

def emphemeral(): #COMPLETE
    # Create a socket
    welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to port 0
    welcomeSocket.bind(('',0))

    return welcomeSocket

def recvHeader(socket, numBytes):

    # The buffer
    recvBuff = ""
    
    # The temporary buffer
    tmpBuff = ""
    
    # Keep receiving till all is received
    while len(recvBuff) < numBytes:
        
        # Attempt to receive bytes
        tmpBuff =  socket.recv(numBytes)
        
        # The other side has closed the socket
        if not tmpBuff:
            break
        
        # Add the received bytes to the buffer
        recvBuff += tmpBuff
    
    return recvBuff

def sendMsg (socket, message):
    messageSize = ""

    # Get the size of the data read and convert it to string
    messageSize = str(len(message))

	# Prepend 0's to the size string until the size is 10 bytes
    while len(messageSize) < 10:
		messageSize = "0" + messageSize

	# Prepend the size of the data to the file data.
    message = messageSize + message	

	# The number of bytes sent
    numSent = 0
	
	# Send the command message
    while len(message) > numSent:
		numSent += socket.send(message[numSent:])


if __name__ == '__main__':

    # Check the command line arguments
    if len(sys.argv) != 3:
        print "-ERROR- USAGE: ", sys.argv[0], " <SERVER_MACHINE> <SERVER_PORT> "
        exit(0)

    # Get the host name (or IP)
    host = sys.argv[1]

    # Get the server's port number 
    port = int(sys.argv[2])

    # The client socket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    # Connect to the server */
    clientSocket.connect((host,port))
    print '\nConnected to server at', host, '; Port: ', port, '\n'

    # List valid client commands
    print 'Command List Usage: \n\tget <FILE_NAME> -> downloads file <file name> from the server'
    print '\tput <FILE_NAME> -> uploads file <file name> to the server'
    print '\tls -> lists files on the server'
    print '\tlls -> lists files on the client'
    print '\tquit -> disconnects from the server and exits \n'

    # Client Command Interface
    condition = True

    # While quit is not chosen
    while condition:
        ans = raw_input ('FTP> ') 
        if len(ans.partition(' ')) == 2:
            cmd = ans
        else:
            cmd, temp, fileName = ans.partition(' ')

        if cmd == 'get':  
            get_function(clientSocket,host,port,fileName)
            print "\n"

        elif cmd == 'put':
            put_function(clientSocket,host,port,fileName)
            print "\n"

        elif cmd == 'ls':
            ls_function(clientSocket,host,port)
            print "\n"

        elif cmd == 'lls':
            lls_function()
            print "\n"

        elif cmd == 'quit':  
            quit_function(clientSocket)

            # Exit Command Interface
            condition = False

        else:
            print '-ERROR- Invalid Command'
            print 'Command List Usage: \n\tget <FILE_NAME> -> downloads file <file name> from the server'
            print '\tput <FILE_NAME> -> uploads file <file name> to the server'
            print '\tls -> lists files on the server'
            print '\tlls -> lists files on the client'
            print '\tquit -> disconnects from the server and exits'
            print '\n'
            

    # Close the connection to the server
    clientSocket.close() 

        
