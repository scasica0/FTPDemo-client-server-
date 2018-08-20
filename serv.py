# *****************************************************
# Description:   Simple FTP Server
# *****************************************************

import socket 
import sys
import commands
import os

def get_function(clientSocket, fileName, addr):

    # check if fileName is valid
    if not os.path.isfile(fileName):
        # file does not exist
        print 'FAILURE- the file: "', fileName, '" does not exist on this server'
        clientSocket.send('n')

    else:
        # tell client that file is valid and continue
        clientSocket.send('y')

        # wait for emphemeral port information from client

        # The buffer to the port information message
        portSizeBuff = ""

        # The buffer containing the port number
        port = ""

        # The size of the incoming message about the port
        portSize = 0

        portSizeBuff = recvHeader(clientSocket, 10)

        # Get the port information message's size
        portSize = int(portSizeBuff)

        # Receive the port's actual number
        port = recvHeader(clientSocket,portSize)
        port = int(port)

        # Clients address
        host = addr[0]

        # The new data socket
        dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        # Connect to emphemeral port
        dataSocket.connect((host,port)) 

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
                totalToSend = len(fileData)    

                # The number of bytes sent
                bytesSent = 0
            
                # Send the data
                while len(fileData) > bytesSent:
                    bytesSent += dataSocket.send(fileData[bytesSent:])
        
            # The file has been read
            else:
                break

        # Success/Failure message
        if bytesSent == totalToSend:
            print 'SUCCESS - get '
            print "Sent: ", fileName
            print 'Total size sent: (', bytesSent, ' bytes)'
        else:
            print 'FAILURE - get '
            print "Attempted to send: ", fileName
            print 'Total size sent: (', bytesSent, ' bytes)'

        # Close the socket and the file
        fileObj.close()
        dataSocket.close()
    print '\n'

def put_function(clientSocket, fileName, addr):

    # wait for confirmation if desired file exists
    confirmation = ""
    confirmation = clientSocket.recv(1)

    # continue if file exists
    if confirmation != 'y':
        print 'FAILURE- the file: "', fileName, '" does not exist on client' 

    else:
        # wait for emphemeral port information from client

        # The buffer to the port information message
        portSizeBuff = ""

        # The buffer containing the port number
        port = ""

        # The size of the incoming message about the port
        portSize = 0

        portSizeBuff = recvHeader(clientSocket, 10)

        # Get the port information message's size
        portSize = int(portSizeBuff)

        # Receive the port's actual number
        port = recvHeader(clientSocket,portSize)
        port = int(port)

        # Clients address
        host = addr[0]

        # The new data socket
        dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        # Connect to emphemeral port
        dataSocket.connect((host,port)) 

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
        fileSizeBuff = recvHeader(dataSocket, 10)
        
        # Get the file size
        fileSize = int(fileSizeBuff)
        
        # Receive the file
        recvBuff = recvHeader(dataSocket,fileSize)

        # save the receive buffer into fileData
        fileData = recvBuff

        # Write the data received to the new file
        fileObj.write(fileData)

        # Close the socket and the file
        fileObj.close()
        dataSocket.close()

        # Success/Failure message
        if fileSize ==  len(fileData):
            print 'SUCCESS - put '
            print 'Received: ' , fileName
            print 'Total size received: (', len(fileData), ' bytes)'
        else:
            print 'FAILURE - put '
            print "Attempted to receive: ", fileName
            print 'Total size received: (', len(fileData), ' bytes)'
    print '\n'

def ls_function(clientSocket):
    serverDirectory = ""

    # Run ls command, get output, and save it to serverDirectory
    for line in commands.getstatusoutput('ls -l'):
        serverDirectory += str(line)
        serverDirectory += "\n"

    # Save size of serverDirectory 
    dataSize = str(len(serverDirectory))

    # Prepend 0's to the size string until the size is 10 bytes
    while len(dataSize) < 10:
        dataSize = "0" + dataSize
    
    # Prepend the size of the data to the file data.
    serverDirectory = dataSize + serverDirectory

    # The number of bytes sent
    bytesSent = 0
        
    # Send the directory
    while len(serverDirectory) > bytesSent:
        bytesSent += clientSocket.send(serverDirectory[bytesSent:])

    if bytesSent == int (len(serverDirectory)):
        print 'SUCCESS - ls '
    else:
        print 'FAILURE - ls '
    print '\n'

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
    if len(sys.argv) != 2:
        print "USAGE: ", sys.argv[0], "<PORT NUMBER>"
        exit(0)

    # Get the port number 
    port = int(sys.argv[1]) 

    # Create A TCP socket
    listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    # Bing the socket to the port 
    listenSocket.bind(('',port)) 

    # Start listening for incoming connections
    listenSocket.listen(1) 


    # Accept connections forever.
    while True:
        
        print "\nWaiting for connections..."
            
        # Accept connections
        clientSocket, addr = listenSocket.accept()
        
        print "\nAccepted connection from client: ", addr
        print "\n"

        # Client Command Interface
        condition = True

        # While quit is not chosen
        while condition:

            # receive command size (save as "cmd")
            cmdSizeBuff = ""
            cmd = ""
            cmdSize = 0
            cmdSizeBuff = recvHeader(clientSocket, 10)
            cmdSize = int(cmdSizeBuff)
            cmd = recvHeader(clientSocket,cmdSize)

            if cmd == "get":  
                # receive filename 
                fileNameBuff = ""
                fileName = ""
                fileNameSize = 0
                fileNameBuff = recvHeader(clientSocket, 10)
                fileNameSize = int(fileNameBuff)
                fileName = recvHeader(clientSocket,fileNameSize)

                get_function(clientSocket,fileName,addr)

            elif cmd == "put":
                # receive filename 
                fileNameBuff = ""
                fileName = ""
                fileNameSize = 0
                fileNameBuff = recvHeader(clientSocket, 10)
                fileNameSize = int(fileNameBuff)
                fileName = recvHeader(clientSocket,fileNameSize)

                put_function(clientSocket,fileName,addr)

            elif cmd == "ls":
                ls_function(clientSocket)

            elif cmd == "quit":  
                condition = False
                print 'Client: ', addr, ' has disconnected'
                print '\n'

            else:
                print 'FAILURE- Invalid Command: "', cmd,  '" Received'

        # Close our side
        clientSocket.close()
            
