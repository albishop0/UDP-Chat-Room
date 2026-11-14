
import socket
import threading
import msvcrt
import time

SERVER_IP = "0.0.0.0"
SERVER_PORT = 50000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

client_address = None
address_lock = threading.Lock()
display_lock = threading.Lock()

typed_text = ""
running = True


def get_local_ip():
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        temp_socket.connect(("8.8.8.8", 80))
        ip_address = temp_socket.getsockname()[0]
    except OSError:
        ip_address = "127.0.0.1"
    finally:
        temp_socket.close()

    return ip_address


def receive_messages():
    global client_address

    while running:
        try:
            message, address = server_socket.recvfrom(1024)

            with address_lock:
                client_address = address

            decoded_message = message.decode("utf-8")

            if decoded_message == "__JOIN__":
                text = f"\nClient connected: {address}"
            else:
                text = f"\nClient: {decoded_message}"

            with display_lock:
                print(text)
                print("You: " + typed_text, end="", flush=True)

        except OSError:
            break


def read_input():
    global typed_text, running

    print("You: ", end="", flush=True)

    while running:
        if msvcrt.kbhit():
            key = msvcrt.getwch()

            with display_lock:
                if key == "\r":
                    message = typed_text
                    typed_text = ""

                    print()

                    if message:
                        with address_lock:
                            destination = client_address

                        if destination is None:
                            print("No client connected yet.")
                        else:
                            server_socket.sendto(
                                message.encode("utf-8"),
                                destination
                            )

                        if message.lower() == "/quit":
                            running = False
                            print("Closing server...")
                            server_socket.close()
                            break

                    print("You: ", end="", flush=True)

                elif key == "\b":
                    if typed_text:
                        typed_text = typed_text[:-1]
                        print("\b \b", end="", flush=True)

                elif key.isprintable():
                    typed_text += key
                    print(key, end="", flush=True)

        time.sleep(0.01)


print("UDP CHAT SERVER")
print("---------------------------")
print("Server IP Address:", get_local_ip())
print("Server Port:", SERVER_PORT)
print("Waiting for a client...")
print("---------------------------")

receive_thread = threading.Thread(
    target=receive_messages,
    daemon=True
)

receive_thread.start()

try:
    read_input()

except KeyboardInterrupt:
    print("\nServer shutting down.")

finally:
    running = False
    server_socket.close()
