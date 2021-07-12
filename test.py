import socket
import pyautogui
import time
import _thread

import pyperclip


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP



screenWidth, screenHeight = pyautogui.size()
currentMouseX, currentMouseY = pyautogui.position()

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

localIP = "0.0.0.0"

UDPLocalPort = 1028
TCPLocalPort = 1029

bufferSize = 512
hostName = socket.gethostname()

print("Host name: " + hostName + ", IP: " + get_ip())


hostNameInBytes = str.encode(hostName)


def init_udp_server():
    # Create a datagram socket

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip

    UDPServerSocket.bind((localIP, UDPLocalPort))

    print("UDP server up and listening")

    # Listen for incoming datagrams
    moveCount = 0
    while (True):

        # try:

            bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

            print(len(bytesAddressPair))
            message = bytesAddressPair[0]

            address = bytesAddressPair[1]

            clientMsg = "Message from Client:{}".format(message)
            clientIP = "Client IP Address:{}".format(address)

            print(clientMsg)
            print(clientIP)

            if message.startswith('getName'.encode()):
                UDPServerSocket.sendto(hostNameInBytes, address)

            elif message.startswith('move'.encode()):

                start = time.time()
                stringMessage = message.decode()
                stringTokens = stringMessage.split(" ")
                xpos = int(stringTokens[1])
                ypos = int(stringTokens[2])
                currentMouseX, currentMouseY = pyautogui.position()

                nextMouseX = currentMouseX + xpos
                nextMouseY = currentMouseY + ypos

                nextMouseX = clamp(nextMouseX, 0, screenWidth)
                nextMouseY = clamp(nextMouseY, 0, screenHeight)

                pyautogui.moveTo(nextMouseX, nextMouseY, logScreenshot=False, _pause=False)
                end = time.time()
                print(end - start)

            elif message.startswith('click'.encode()):
                print("Click....")
                pyautogui.click()

            elif message.startswith('setText'.encode()):
                print("setText....")
                stringMessage = message.decode()
                lastReceiveWord = stringMessage[len("setText "):]
                # pyautogui.write(lastReceiveWord)
                pyperclip.copy(lastReceiveWord)
                pyautogui.hotkey("ctrl", "v")

        # except Exception as err:
        #     exception_type = type(err).__name__
        #     print("ERROR UDP: ", exception_type)

def init_tcp_server():
    # Create a TCP/IP socket
    TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = (localIP, 1029)
    TCPServerSocket.bind(server_address)
    TCPServerSocket.listen(1)
    print("TCP server up and listening")

    while True:
        try:
            connection, client_address = TCPServerSocket.accept()

            print('connection from', client_address)

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
                print('received "%s"' % data)
                if data:
                    print('sending data back to the client')
                    # connection.sendall(hostNameInBytes)
                    connection.sendto(hostNameInBytes, client_address)
                else:
                    print('no more data from', client_address)
                    break
            # Clean up the connection
            connection.close()
            print("Connection close")

        except Exception as err:
            exception_type = type(err).__name__
            print("ERROR: ", exception_type)


try:
    # _thread.start_new_thread(init_udp_server, ())
    _thread.start_new_thread(init_tcp_server, ())

except:
    print("Error TCP: unable to start thread")

# while 1:
#     pass
init_udp_server()
