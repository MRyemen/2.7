""""

Author:Dvir Zilber

Program name:Service.py

Description: A program that connects a client to the server recives a command and sends back the requested data.

"""
import string
from logging import exception
from pathlib import Path
import glob
import socket
import logging
import os
import shutil
import subprocess
from PIL import ImageGrab





SERVER_IP = '0.0.0.0'
SERVER_PORT = 33926
MAX_PACKET = 1024
PHOTO_LOCTION = r"C:\Users\Admin\PycharmProjects\PythonProject1\server_screenshot.jpg"


# ================= PROTOCOL ===================
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




# ================ COMMAND PARSER ================
def parse_message(massage):
    """
    Splits a massage 'COMMAND ARG' into (command, arg)
    """
    massage = massage.strip()
    try:
        parts = massage.split(" ", 1)  # splits by the space between the command and the path.
        command = parts[0].upper()
        if len(parts[1]) > 0:
            arg = parts[1]
        else:
            arg = None
        return command, arg
    except:
        massage = massage.upper()
        return massage, None #returns path as none because wasnt able to split meaninig that the user probebly typed only command


# ================= COMMANDS ====================
def dir(directory_path: str):
    try:
        path = Path(directory_path)

        if not path.is_dir():
            return "ERROR: Directory does not exist"
            logging.error('path does not exist')

        if path is None:
            return "ERROR: Path does not exist"


        files = [str(f.name) for f in path.glob("*")]


        if not files:
            return "EMPTY"

        return "\n".join(files)

    except Exception as e:
        logging.error(f'there has accourd an unkown error: {e}')
        return f"ERROR: {e}"





def delete_file(directory_path: str) -> str:
    """
       deletes a file (that has been giving to het by test delete to prevent from files i dont want to delete, be deleted)
       and doing so with import os
    """
    try:
        path = Path(directory_path)

        if not path.exists():
            return "ERROR|File does not exist"
            logging.error("ERROR|File does not exist")

        if not path.is_file():
            return "ERROR|Path is not a file"
            logging.error('"ERROR|Path is not a file"')

        os.remove(path)
        return "File deleted successfully"

    except Exception as e:
        return f"ERROR|{str(e)}"






def test_delete():
    # creation of test file
    #becuse i dont want to acssedently delete an important file, i create a temp one
    test_name = "delete_test.txt"
    with open(test_name, "w") as f:
        f.write("temp")

    result = delete_file(test_name)
    print(result)
    return result





def copy_file(massage: str):
    """
    Copies a file from src to dst safely.
    Returns 'OK' on success or 'ERROR: <message>' on failure.
    The client must send:  'src_path,dst_path'
    """

    try:
        # Split incoming massage into src and dst
        path = massage.split(",", 1)
    except Exception:
        logging.error("ERROR|Could not split massage, massage is not built properly for 'copy'")
        return "ERROR|Could not split massage, massage is not built properly for 'copy'"

    try:
        src_path = Path(path[0])
        dst_path = Path(path[1])
        """
        # check if source exists
        if not src_path:
            return "ERROR: Source file does not exist"

        # ensure destination folder exists
        if not dst_path.parent.exists():
            return "ERROR: Destination directory does not exist"
        """

        shutil.copyfile(src_path, dst_path)
        logging.info(f"File copied from {src_path} to {dst_path}")

        return "OK|File copied successfully"

    except Exception as e:
        logging.error(f"Copy error: {str(e)}")
        return f"ERROR: {str(e)}"




def execute_program(exe_path: str):
    """
    Executes a program on the server using the full path given by the client.
    Returns an OK/ERROR message for the client.
    """

    try:
        exe = Path(exe_path)

        # Check if file exists
        if not exe.is_file():
            return "ERROR|Executable file not found"

        # Try running the program
        subprocess.Popen(str(exe))
        logging.info(f"Executed program: {exe_path}")

        return "OK|Program started successfully"

    except Exception as e:
        logging.error(f"EXECUTE error: {str(e)}")
        return f"ERROR|Failed to execute: {str(e)}"




def take_screenshot():
    """
    Takes a screenshot and saves it in a fixed path on the server.
    Returns an OK/ERROR message for the client.
    """
    SCREENSHOT_PATH = Path(PHOTO_LOCTION)
    try:
        # Make sure directory exists
        SCREENSHOT_PATH.parent.mkdir(exist_ok=True)

        # Take the screenshot using PIL ImageGrab
        image = ImageGrab.grab()

        # Save the screenshot
        image.save(SCREENSHOT_PATH)

        logging.info(f"Screenshot saved to: {SCREENSHOT_PATH}")

        return f"OK|Screenshot saved to: +{SCREENSHOT_PATH}"

    except Exception as e:
        logging.error(f"Screenshot error: {e}")
        return f"ERROR|{e}"



# =============== CLIENT HANDLING ================
def handle_client(client_socket):
    """
    Receives commands from the connected client and sends back the requested data.
    Handles commands: TIME, NAME, RAND, EXIT.
    Closes the connection when 'EXIT' is received or the connection is lost.
    """

    while True:
        dec_massage = unpack_message(client_socket)  # getting the massage after it has been read by the amount of bytes

        if not dec_massage:#checkes if the client has disconnected
            break

        cmd, path = parse_message(dec_massage)  # getting the command + the path

        if cmd == 'DIR':
            response = dir(path)
            logging.info('command is' "DIR")
            assert(type(response)== str)


        elif cmd == 'DELETE':
            response = test_delete()
            logging.info('command is' "DELETE")
            assert (type(response) == str)


        elif cmd == 'COPY':
            response = copy_file(path)
            logging.info('command is' "COPY")
            assert (type(response) == str)


        elif cmd == 'EXECUTE':
            response = execute_program(path)
            logging.info('command is' "EXECUTE")
            assert (type(response) == str)


        elif cmd == 'SCREENSHOT':
            response = take_screenshot()
            logging.info('command is' "TAKE_SCREENSHOT")


        elif cmd == 'SENDPHOTO':
            response = 'Photo loction: ' + PHOTO_LOCTION + '\n'
            logging.info('command is' "SENDPHOTO")


        elif cmd == 'EXIT':
            response = 'Bye!'
            break

        else:
            response = 'Unknown command'

        response = pack_message(response)
        client_socket.send(response)

    response = pack_message(response)
    client_socket.send(response)
    client_socket.close()



# ================== MAIN ====================
def main():
    """
    Starts the TCP server, listens for incoming connections, and handles each client.
    Logs when the server is listening and when clients connect or disconnect.
    """
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen(5)
        print("Server is listening...")
        logging.info('Server is listening...')
    except:
        logging.info('Server is NOT listening...')

    while True:
            client_socket, client_addr = server_socket.accept()
            print("Client connected:", client_addr)
            handle_client(client_socket)
            print("Client disconnected")






if __name__ == '__main__':
    """
    Configures the logging settings and starts the main server loop.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=
        [
            logging.FileHandler('logg_of_server'),
            # logging.StreamHandler() (only when there is a need to show the logs to the user)
        ]
    )

    main()