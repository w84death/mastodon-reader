import time
import json
import threading
from mastodon import Mastodon
from gtts import gTTS
from bs4 import BeautifulSoup
import os
import tkinter as tk
from PIL import ImageTk, Image

# Variable to control the main loop
keep_running = True

def load_credentials():
    if not os.path.isfile("credentials.json"):
        return {"error": "ERROR: **credentials.json** file does not exist.\nPlease create this file by copying and renaming credentials.dist.json file. Restart application."}
    with open("credentials.json") as file:
        credentials = json.load(file)
    return credentials

credentials = load_credentials()

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

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("temp.mp3")
    os.system("mpg123 temp.mp3")
    os.remove("temp.mp3")


def main(welcome_label):
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

                # Update the label text
                welcome_label.config(text=text_to_speak)

                # Speak out the notification
                speak(text_to_speak)

        # Wait for 10 seconds before checking for new notifications
        time.sleep(10)

def start(welcome_text, start_button, stop_button):
    if "error" in credentials:
        return
    start_button.pack_forget()
    stop_button.pack(side="left", padx=8, pady=8)
    speak(welcome_message)
    threading.Thread(target=main, args=(welcome_text,)).start()

def stop(stop_button, start_button):
    global keep_running
    keep_running = False
    stop_button.pack_forget()
    start_button.pack(side="right", padx=8, pady=8)

if __name__ == '__main__':
    root = tk.Tk()
    root.title('P1X Mastodon Reader')
    root.resizable(False, False)

    img = ImageTk.PhotoImage(Image.open('header_image.gif'))  # replace 'header_image.gif' with your image file
    panel = tk.Label(root, image=img)
    panel.pack(side="top", fill="both", expand="yes")

    welcome_text = tk.Text(root, width=55, height=6)
    welcome_text.insert(tk.END, welcome_message)
    welcome_text.pack(padx=8, pady=16)

    start_button = tk.Button(root, text="Start reading notifications", command=lambda: start(welcome_text, start_button, stop_button))
    start_button.pack(side="right", padx=8, pady=8)

    stop_button = tk.Button(root, text="Stop", command=lambda: stop(stop_button, start_button))
    stop_button.pack_forget()

    root.mainloop()
