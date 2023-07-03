import time
import json
import threading

import subprocess
from mastodon import Mastodon
from bs4 import BeautifulSoup
import os
import tkinter as tk
from PIL import ImageTk, Image
from queue import Queue

# Variable to control the main loop
keep_running = True

def load_credentials():
    if not os.path.isfile("credentials.json"):
        return {"error": "ERROR: **credentials.json** file does not exist.\nPlease create this file by copying and renaming credentials.dist.json file. Restart application."}
    with open("credentials.json") as file:
        credentials = json.load(file)
    return credentials

credentials = load_credentials()
audio_queue = Queue()

welcome_message = "Welcome to P1X Mastodon Reader\nCoded by Krzysztof Krystian Jankowski"
if "error" in credentials:
    welcome_message += "\n\n"+credentials["error"]
else:
    mastodon = Mastodon(
        client_id=credentials["client_key"],
        client_secret=credentials["client_secret"],
        access_token=credentials["access_token"],
        api_base_url=credentials["api_base_url"]
    )

def strip_html(html):
    soup = BeautifulSoup(html, features="html.parser")
    return soup.get_text()

def speak_thread(welcome_widget):
        def run():
            import tempfile
            while True:
                text = audio_queue.get().strip()  # Strip leading/trailing whitespace
                if any(char.isalnum() for char in text):  # If the text contains any alphanumeric characters
                    welcome_widget.delete("1.0", "end")
                    welcome_widget.insert("1.0", text)
                    subprocess.run(['spd-say', '-p', '-20', '-l', 'us', text])
                audio_queue.task_done()


        thread = threading.Thread(target=run)
        thread.start()


def main(welcome_widget):
    global keep_running
    last_notification_id = None

    while keep_running:
        notifications = mastodon.notifications(since_id=last_notification_id)

        if notifications:
            last_notification_id = notifications[0]['id']

            for notification in notifications:
                notification_type = notification['type']
                account_name = notification['account']['acct']

                text_to_speak = f"You have a new {notification_type} notification from {account_name}"

                if notification_type == 'mention':
                    content = strip_html(notification['status']['content'])
                    text_to_speak += f". Message: {content}"

                # Speak out the notification
                audio_queue.put(text_to_speak)

        # Wait for 10min before checking for new notifications
        time.sleep(10*60)

def start(welcome_text, start_button, stop_button, emoji_label):
    if "error" in credentials:
        return
    start_button.pack_forget()
    stop_button.pack(side="left", padx=8, pady=8)
    audio_queue.put(welcome_message)
    threading.Thread(target=main, args=(welcome_text,)).start()
    emoji_label.config(text="(o.O )")

def stop(stop_button, start_button, emoji_label):
    global keep_running
    keep_running = False
    stop_button.pack_forget()
    start_button.pack(side="right", padx=8, pady=8)
    emoji_label.config(text="(-.- )")

if __name__ == '__main__':
    root = tk.Tk()
    root.title('P1X Mastodon Reader')
    root.resizable(False, False)

    emoji_label = tk.Label(root,text="(-.- )",font=("TkDefaultFont", 48))
    emoji_label.pack(pady=8)

    welcome_text = tk.Text(root, width=55, height=6)
    welcome_text.insert(tk.END, welcome_message)
    welcome_text.pack(padx=8, pady=16)

    speak_thread(welcome_text)

    start_button = tk.Button(root, text="Start reading notifications", command=lambda: start(welcome_text, start_button, stop_button, emoji_label))
    start_button.pack(side="right", padx=8, pady=8)

    stop_button = tk.Button(root, text="Stop", command=lambda: stop(stop_button, start_button, emoji_label))
    stop_button.pack_forget()

    root.mainloop()
