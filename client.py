
import socket
import threading
import msvcrt
import time

SERVER_IP = input("Enter Server IP Address: ")
SERVER_PORT = int(input("Enter Server Port: "))

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (SERVER_IP, SERVER_PORT)

client_socket.sendto(
    "__JOIN__".encode("utf-8"),
    server_address
)

print("\nConnected to the UDP chat server!")
print("Type /quit to exit.")
print("---------------------------")

display_lock = threading.Lock()
typed_text = ""
running = True


def receive_messages():
    while running:
        try:
            message, address = client_socket.recvfrom(1024)

            with display_lock:
                print("\nServer: " + message.decode("utf-8"))
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
                        client_socket.sendto(
                            message.encode("utf-8"),
                            server_address
                        )

                        if message.lower() == "/quit":
                            running = False
                            print("Disconnecting...")
                            client_socket.close()
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


receive_thread = threading.Thread(
    target=receive_messages,
    daemon=True
)

receive_thread.start()

try:
    read_input()

except KeyboardInterrupt:
    print("\nClient shutting down...")

finally:
    running = False
    client_socket.close()
