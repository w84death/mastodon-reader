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
    with open("credentials.json") as file:
        credentials = json.load(file)
    return credentials

credentials = load_credentials()

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

def stop():
    global keep_running
    keep_running = False

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

def start(welcome_label):
    speak(welcome_message)
    threading.Thread(target=main, args=(welcome_label,)).start()

if __name__ == '__main__':
    root = tk.Tk()
    root.title('P1X Mastodon Reader')
    root.resizable(False, False)

    img = ImageTk.PhotoImage(Image.open('header_image.gif'))  # replace 'header_image.gif' with your image file
    panel = tk.Label(root, image=img)
    panel.pack(side="top", fill="both", expand="yes")

    welcome_message = "Welcome to P1X Mastodon Reader by Krzysztof Krystian Jankowski"
    welcome_label = tk.Label(root, text=welcome_message)
    welcome_label.pack()

    start_button = tk.Button(root, text="Start", command=lambda: start(welcome_label))
    start_button.pack()

    stop_button = tk.Button(root, text="Stop", command=stop)
    stop_button.pack()

    root.mainloop()
