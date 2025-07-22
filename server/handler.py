import json
from question_manager import load_questions
import time
import select

TIME_LIMIT = 5 * 60  # 5 minutes

TIMER_DISPLAY_INTERVAL = 30  # seconds



def handle_client(conn, addr, users):
    print(f"[NEW CONNECTION] {addr} connected.")

    conn.send(b"Username: ")
    username = conn.recv(1024).decode().strip()
    conn.send(b"Password: ")
    password = conn.recv(1024).decode().strip()

    if username not in users or users[username] != password:
        conn.send(b"Invalid credentials. Disconnecting.")
        conn.close()
        return

    conn.send(b"Login successful. Starting exam...\n")
    questions = load_questions()
    score = 0

    answers = [None] * len(questions)
    start_time = time.time()
    current_index = 0
    last_timer_display = 0


    question_sent = False  # before the loop

    while True:
        elapsed = time.time() - start_time
        remaining = TIME_LIMIT - elapsed

        if remaining <= 0:
            conn.send(b"\nTime's up! Submitting your answers...\n")
            break

        if int(elapsed) - last_timer_display >= TIMER_DISPLAY_INTERVAL:
            mins = int(remaining) // 60
            secs = int(remaining) % 60
            conn.send(f"\n⏳ Time Remaining: {mins:02d}:{secs:02d}\n".encode())
            last_timer_display = int(elapsed)

        # ✅ Only send question once per response
        if not question_sent:
            if current_index == len(questions) - 1 and answers[current_index] is not None:
                # Last question already answered – don't show it again
                conn.send(b"\n You've reached the end of the exam.\n")
                conn.send(b"Type 'unanswered' to review unanswered questions.\n")
                conn.send(b"Type 'goto <num>' to jump to a question.\n")
                conn.send(b"Type 'answered' to see answered questions.\n")
                conn.send(b"Type 'submit' to finish the exam.\n")
            else:
                # Show the question
                q = questions[current_index]
                conn.send(f"\nQ{current_index + 1}: {q['question']}\n".encode())

                for opt in q['options']:
                    conn.send(f"{opt}\n".encode())

                if answers[current_index] is not None:
                    conn.send(f"\n✅ You answered: {answers[current_index]}\n".encode())
                    conn.send(b"You can change your answer or use commands (next, prev, skip, goto <num>, unanswered, submit): ")
                else:
                    conn.send(b"Your Answer (A/B/C/D), or type 'next', 'prev', 'skip', 'goto <num>', 'unanswered', or 'submit': ")

                
            question_sent = True

              # mark question/options shown


        ready, _, _ = select.select([conn], [], [], 1.0)
        if ready:
            response = conn.recv(1024).decode().strip().upper()

            if response in ['A', 'B', 'C', 'D']:
                answers[current_index] = response
                current_index = min(current_index + 1, len(questions) - 1)
                question_sent = False
            elif response == "NEXT":
                current_index = min(current_index + 1, len(questions) - 1)
                question_sent = False
            elif response == "PREV":
                current_index = max(current_index - 1, 0)
                question_sent = False
            elif response == "SKIP":
                current_index = min(current_index + 1, len(questions) - 1)
                question_sent = False
            elif response == "SUBMIT":
                conn.send(b"Submitting your answers...\n")
                break
            elif response.startswith("GOTO"):
                parts = response.split()
                if len(parts) == 2 and parts[1].isdigit():
                    qnum = int(parts[1]) - 1
                    if 0 <= qnum < len(questions):
                        current_index = qnum
                        question_sent = False
                    else:
                        conn.send(b"Invalid question number.\n")
                else:
                    conn.send(b"Usage: goto <question_number>\n")
            elif response == "UNANSWERED":
                unanswered = [f"Q{i + 1}" for i, ans in enumerate(answers) if ans is None]
                if unanswered:
                    conn.send(b"\nUnanswered Questions:\n-------------------------\n")
                    conn.send((" , ".join(unanswered) + "\n").encode())
                else:
                    conn.send(b"\nAll questions have been answered!\n")
                question_sent = False
                
                # Prompt again
                # conn.send(b"\nEnter your command (goto <num>, submit, etc.): ")


            else:
                conn.send(b"Invalid input. Use A/B/C/D or valid command.\n")


    # After breaking from the loop (time-up or submit):
    score = 0
    for idx, ans in enumerate(answers):
        if ans == questions[idx]['answer']:
            score += 1

    conn.send(f"\nExam finished. Score: {score} / {len(questions)}\n".encode())
    conn.close()

