""""

Author:Dvir Zilber

Program name:client.py

Description: A program that sende the server a command and recives back the desired data then prints it.

"""


import socket
import logging

SERVER_IP = '127.0.0.1'
SERVER_PORT = 33926
MAX_PACKET = 1024



def pack_message(message: str) -> bytes:
    """
    Packs a message into protocol format: LENGTH(4 bytes) + MESSAGE(bytes)
    - The message is encoded using UTF-8
    - The length is the number of bytes (chars)
    """

    # Convert the message to bytes
    msg_bytes = message.encode()

    # Calculate length in bytes
    length = len(msg_bytes)

    # Convert length to a fixed 4-digit string, padded with zeros(when its smaller the 1000 which is in most casses)
    # Example: 12 → "0012"
    length_str = str(length).zfill(4)

    # Convert length to bytes
    length_bytes = length_str.encode()

    # Return the combined packet
    return length_bytes + msg_bytes



def unpack_message(sock) -> str:
    """
    Reads a full protocol message from a socket.
    1. Reads the first 4 bytes (message length)
    2. Reads exactly that number of bytes
    3. Decodes everything with UTF-8
    """

    # Read the first 4 bytes → the length header
    length_bytes = sock.recv(4)
    if not length_bytes:
        return None  # Connection closed

    # Decode the header (string of digits)
    length_str = length_bytes.decode()

    # Convert to integer (number of bytes to read)
    msg_length = int(length_str)

    # Read exactly msg_length bytes
    data = sock.recv(msg_length)

    # Decode and return the message text
    return data.decode()






def main():
    """
    Connects to the server, sends user commands, receives responses, and handles communication.
    The user can enter commands: DIR, DELETE, SCRENNSHOT,EXECUTE,COPY or EXIT.
    Logs events such as successful connection, command sending, and response reception.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:

        client_socket.connect((SERVER_IP, SERVER_PORT))
        logging.info('Client connected successfully') #giving a logg message
        print('Connected to server at'+ SERVER_IP + str(SERVER_PORT))

        while True:
            cmd = input("Enter command (DIR, DELETE, SCRENNSHOT,EXECUTE,COPY or EXIT) and a path, with spaces between them: ")

            if cmd == "EXIT":#if cmd == 'exit' then leave the while loop
                print("see ya later")
                break


            else:
                cmd = pack_message(cmd)

                client_socket.send(cmd)#sending the command to the server
                logging.info('Command sent to server successfully')

                response = unpack_message(client_socket)#getting a response from the server
                logging.info('Response received from server')
                print("Server response:", response)

    except Exception as e:

        print("Error:", e)
    finally:
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    """
    Initializes the logging configuration and runs the main client function.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=
        [
            logging.FileHandler('logg_of_client'),
            # logging.StreamHandler() only when there is a need to show the logs to the user
        ]
    )
    main()
