import tkinter as tk
from tkinter import Tk, Label, Entry, Button, Frame, messagebox
import requests
from datetime import datetime, timedelta
import threading
import time
from playsound import playsound
import random

DISTANCEMATRIX_API_KEY = 'XBJdEDmtBIwogdfsYrJb0baiOzF6qSKA0m4v98TJDaZyc1Jo6If2gL7yKYTDWMYJ'
WEATHER_API_KEY = '4dcfdb40bf998f293937f62769af9926'
ALARM_SOUND_PATH = '/Users/dk/Desktop/clock_project/audio/audio.wav'

# Utility Functions
def get_travel_time(start, destination):
    url = f'https://api.distancematrix.ai/maps/api/distancematrix/json?origins={start}&destinations={destination}&key={DISTANCEMATRIX_API_KEY}'
    response = requests.get(url).json()
    if response['status'] == 'OK':
        travel_duration = response['rows'][0]['elements'][0]['duration']['value']
        return travel_duration
    else:
        messagebox.showerror("Error", "Could not retrieve travel time.")
        return None


def calculate_leave_time(arrival_time, travel_time):
    return arrival_time - timedelta(seconds=travel_time)


def get_weather_conditions(location):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}'
    response = requests.get(url).json()
    if response['cod'] == 200:
        weather_main = response['weather'][0]['main']
        return weather_main
    else:
        messagebox.showerror("Error", "Could not retrieve weather data")
        return None


def adjust_for_weather_conditions(weather, travel_time):
    if weather in ["Rain", "Snow", "Fog"]:
        travel_time += travel_time * 0.13
    return travel_time


def check_for_weather(start):
    return get_weather_conditions(start)


def check_for_delays_and_weather(start, destination, weather):
    travel_time = get_travel_time(start, destination)
    return adjust_for_weather_conditions(weather, travel_time)


# Hangman Puzzle
def hangman_puzzle():
    def initialize_new_game():
        """Initializes a new Hangman game with a new word."""
        nonlocal chosen_word, guessed_word, attempts, used_letters
        chosen_word = random.choice(word_list)
        guessed_word = ["_"] * len(chosen_word)
        attempts = 6
        used_letters.clear()

        # Update UI
        status_label.config(text=" ".join(guessed_word))
        attempts_label.config(text=f"Attempts Left: {attempts}")
        used_letters_label.config(text="Used Letters: ")

    word_list = ["python", "travel", "weather", "smart", "alarm"]
    chosen_word = ""
    guessed_word = []
    attempts = 6
    used_letters = set()

    # Initialize the Hangman window
    hangman_window = tk.Toplevel()
    hangman_window.title("Hangman Puzzle")
    tk.Label(hangman_window, text="Solve the Hangman to turn off the alarm!", font=("Helvetica", 14)).pack(pady=10)

    # Define UI elements (placed before usage)
    status_label = tk.Label(hangman_window, text="", font=("Helvetica", 16))
    status_label.pack(pady=10)

    guess_entry = tk.Entry(hangman_window, font=("Helvetica", 14))
    guess_entry.pack(pady=10)

    submit_button = tk.Button(hangman_window, text="Submit", font=("Helvetica", 12))
    submit_button.pack(pady=10)

    attempts_label = tk.Label(hangman_window, text="", font=("Helvetica", 12))
    attempts_label.pack(pady=10)

    used_letters_label = tk.Label(hangman_window, text="", font=("Helvetica", 12))
    used_letters_label.pack(pady=10)

    # Bind submit button to check_guess function
    def check_guess():
        nonlocal attempts
        guess = guess_entry.get()
        guess_entry.delete(0, tk.END)

        if len(guess) != 1 or not guess.isalpha():
            messagebox.showerror("Input Error", "Enter a single alphabet.")
            return

        guess = guess.lower()

        if guess in used_letters:
            messagebox.showerror("Repeated Guess", f"You've already guessed '{guess}'. Try another letter.")
            return

        used_letters.add(guess)
        used_letters_label.config(text=f"Used Letters: {', '.join(sorted(used_letters))}")

        if guess in chosen_word:
            for i, letter in enumerate(chosen_word):
                if letter == guess:
                    guessed_word[i] = guess
            status_label.config(text=" ".join(guessed_word))
        else:
            attempts -= 1
            attempts_label.config(text=f"Attempts Left: {attempts}")

        if "_" not in guessed_word:
            messagebox.showinfo("Success", "You've solved the Hangman puzzle! Alarm stopped.")
            hangman_window.destroy()
        elif attempts == 0:
            messagebox.showerror("Failure", "Out of attempts! Starting a new puzzle.")
            initialize_new_game()

    # Set the button command after defining check_guess
    submit_button.config(command=check_guess)

    # Initialize the UI for the first game
    initialize_new_game()



# Play Alarm Function
def play_alarm():
    threading.Thread(target=playsound, args=(ALARM_SOUND_PATH,), daemon=True).start()
    hangman_puzzle()


# Alarm Clock App
class AlarmClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Alarm Clock")

        # Entry fields
        Label(root, text="Start Address").grid(row=0, column=0)
        self.start_entry = Entry(root)
        self.start_entry.grid(row=0, column=1)
        Label(root, text="Destination Address").grid(row=1, column=0)
        self.destination_entry = Entry(root)
        self.destination_entry.grid(row=1, column=1)
        Label(root, text="Arrival Time (HH:MM)").grid(row=2, column=0)
        self.arrival_entry = Entry(root)
        self.arrival_entry.grid(row=2, column=1)
        self.enter_button = Button(root, text="Enter", command=self.calculate_time)
        self.enter_button.grid(row=3, column=1)

        self.alarm_label = Label(root, text="", fg="red")
        self.alarm_label.grid(row=4, columnspan=2)

        # Frame for displaying active alarms
        Label(root, text="Active Alarms:").grid(row=5, column=0, sticky="w")
        self.alarm_frame = Frame(root)
        self.alarm_frame.grid(row=6, column=0, columnspan=2, sticky="ew")

        self.active_alarms = {}  # Dictionary to store alarms

    def calculate_time(self):
        start = self.start_entry.get()
        destination = self.destination_entry.get()
        arrival_time_str = self.arrival_entry.get()

        try:
            arrival_time = datetime.strptime(arrival_time_str, "%H:%M").replace(
                year=datetime.now().year, month=datetime.now().month, day=datetime.now().day
            )
            leave_time = arrival_time - timedelta(minutes=30)  # Simulate travel time calculation
            self.alarm_label.config(text=f"Recommended Leave Time: {leave_time.strftime('%H:%M')}")
            if messagebox.askyesno("Set Alarm", "Would you like to set an alarm?"):
                self.add_alarm(leave_time, arrival_time, start, destination)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter arrival time in HH:MM format.")

    def add_alarm(self, leave_time, arrival_time, start, destination):
        alarm_id = str(leave_time)  # Use leave_time as the alarm ID
        if alarm_id not in self.active_alarms:
            # Create an event to signal the thread to stop
            stop_event = threading.Event()

            # Create a thread for the alarm
            alarm_thread = threading.Thread(
                target=self.start_alarm_thread, args=(leave_time, alarm_id, stop_event), daemon=True
            )
            alarm_thread.start()

            # Add alarm details to the dictionary
            self.active_alarms[alarm_id] = {
                "leave_time": leave_time,
                "arrival_time": arrival_time,
                "start": start,
                "destination": destination,
                "thread": alarm_thread,
                "stop_event": stop_event,
            }

            # Update the alarm list in the GUI
            self.update_alarm_list()

    def start_alarm_thread(self, leave_time, alarm_id, stop_event):
        while not stop_event.is_set():
            current_time = datetime.now()
            if current_time >= leave_time:
                play_alarm()
                del self.active_alarms[alarm_id]  # Remove alarm after it triggers
                self.update_alarm_list()
                break
            time.sleep(1)

    def update_alarm_list(self):
        # Clear the frame
        for widget in self.alarm_frame.winfo_children():
            widget.destroy()

        # Add alarms to the frame
        for alarm_id, alarm_data in self.active_alarms.items():
            leave_time = alarm_data["leave_time"]
            arrival_time = alarm_data["arrival_time"]
            start = alarm_data["start"]
            destination = alarm_data["destination"]

            # Display alarm details
            alarm_label = Label(
                self.alarm_frame,
                text=f"Alarm: {leave_time.strftime('%H:%M')} | Arrival: {arrival_time.strftime('%H:%M')} | From: {start} | To: {destination}",
            )
            alarm_label.pack(side="top", anchor="w", padx=5, pady=2)

            # Add delete button
            delete_button = Button(
                self.alarm_frame,
                text="Delete",
                command=lambda alarm_id=alarm_id: self.delete_alarm(alarm_id),
            )
            delete_button.pack(side="top", anchor="e", padx=5, pady=2)

    def delete_alarm(self, alarm_id):
        # Stop the alarm thread by setting its stop_event
        if alarm_id in self.active_alarms:
            self.active_alarms[alarm_id]["stop_event"].set()  # Signal the thread to stop
            del self.active_alarms[alarm_id]
            self.update_alarm_list()


def play_alarm():
    threading.Thread(target=playsound, args=(ALARM_SOUND_PATH,), daemon=True).start()


# Main Application
root = Tk()
app = AlarmClockApp(root)
root.mainloop()

