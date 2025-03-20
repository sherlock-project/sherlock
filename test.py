import pyautogui, keyboard, pygame, time, random, os, webbrowser
import threading

# **Initialize sound system**
pygame.mixer.init()
sounds = ["creepy_whisper.mp3", "error_beep.mp3"]

# **Step 1: Open WhatsApp Web (Only Once)**
def open_whatsapp():
    webbrowser.open("https://web.whatsapp.com/")
    time.sleep(3)  # Shorter delay
    threading.Thread(target=phantom_typing, daemon=True).start()  # Move to Phantom Typing immediately

# **Step 2: Phantom Typing in Notepad (Only Once)**
def phantom_typing():
    messages = [
        "charchit ..I am watching you...", 
        "You can't stop me...atharva", 
        "Who’s there? is it purab?", 
        "Your system is under my control, ommm...", 
        "It's too late now...",
        "Why are you looking at the screen like that?",
        "I'm inside your system."
    ]

    os.system("notepad")  # Open Notepad
    time.sleep(1)

    # **Type multiple lines at different speeds**
    for _ in range(random.randint(5, 7)):  
        pyautogui.write(random.choice(messages), interval=random.uniform(0.02, 0.05))
        pyautogui.press("enter")
        time.sleep(random.uniform(0.2, 0.5))  # Faster typing

    time.sleep(2)  # Shorter delay before closing
    pyautogui.hotkey("alt", "f4")  # Close Notepad

    # Start Google searches and haunted effects **after Notepad closes**
    threading.Thread(target=random_google_search, daemon=True).start()
    threading.Thread(target=haunted_mouse, daemon=True).start()
    threading.Thread(target=random_sounds, daemon=True).start()

# **Step 3: Open Random Google Searches (Continuously in Parallel)**
def random_google_search():
    searches = [
        "Am I being hacked?",
        "Why is my computer acting weird?",
        "My keyboard is typing by itself!",
        "Is my computer haunted?",
        "How to remove a hacker from my PC?",
        "Why is my mouse moving on its own?"
    ]
    
    while True:
        if keyboard.is_pressed("esc"): break
        time.sleep(random.randint(2, 4))  # Faster searches
        webbrowser.open(f"https://www.google.com/search?q={random.choice(searches)}")

# **Step 4: Make Mouse Move Randomly**
def haunted_mouse():
    while True:
        if keyboard.is_pressed("esc"): break
        pyautogui.moveTo(random.randint(100, 1200), random.randint(100, 800), duration=0.2)
        time.sleep(random.uniform(0.5, 1.5))  # Faster movement

# **Step 5: Play Random Sounds**
def random_sounds():
    while True:
        if keyboard.is_pressed("esc"): break
        time.sleep(random.randint(2, 6))  # Faster sounds
        pygame.mixer.music.load(random.choice(sounds))
        pygame.mixer.music.play()

# **Start the workflow**
open_whatsapp()  # WhatsApp opens first, then shifts to Phantom Typing

keyboard.wait("esc")  # Press ESC to stop everything
