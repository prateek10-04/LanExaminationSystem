# def run_exam(sock):
#     buffer = ""
#     while True:
#         try:
#             data = sock.recv(1024).decode()
#             if not data:
#                 break
#             buffer += data
#             print(data, end='')

#             # Wait for complete prompt
#             if "Your Answer" in buffer or "Username:" in buffer or "Password:" in buffer or "You've reached" in buffer or "You can change" in buffer or "Invalid" in buffer:
#                 user_input = input()
#                 sock.send((user_input + "\n").encode())  # FIX: Add newline
#                 buffer = ""
#         except Exception as e:
#             print(f"Error: {e}")
#             break

# import threading

# def receive_messages(sock):
#     buffer = ""
#     while True:
#         try:
#             data = sock.recv(1024).decode()
#             if not data:
#                 break
#             buffer += data
#             print(data, end='')

#             # Prompt for input only when server expects it
#             if any(prompt in buffer for prompt in [
#                 "Your Answer", "Username:", "Password:", 
#                 "You've reached", "You can change", "Invalid"
#             ]):
#                 user_input = input()
#                 sock.send((user_input + "\n").encode())  # Include newline
#                 buffer = ""
#         except Exception as e:
#             print(f"Error: {e}")
#             break

# def run_exam(sock):
#     receiver_thread = threading.Thread(target=receive_messages, args=(sock,))
#     receiver_thread.start()
#     receiver_thread.join()

import threading

def receive_messages(sock, prompt_event, stop_event):
    buffer = ""
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                stop_event.set()  # signal main thread to stop
                break
            print(data, end='')
            buffer += data

            if any(keyword in buffer for keyword in [
                "Your Answer", "Username:", "Password:",
                "You've reached", "You can change", "Invalid"
            ]):
                prompt_event.set()
                buffer = ""
        except:
            stop_event.set()
            break


def run_exam(sock):
    prompt_event = threading.Event()
    stop_event = threading.Event()
    receiver_thread = threading.Thread(target=receive_messages, args=(sock, prompt_event, stop_event))
    receiver_thread.daemon = True
    receiver_thread.start()

    while not stop_event.is_set():
        prompt_event.wait()
        if stop_event.is_set():
            break
        user_input = input()
        try:
            sock.send((user_input + "\n").encode())
        except:
            break
        prompt_event.clear()


