import tkinter as tk
from tkinter import messagebox
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
    word_list = ["python", "travel", "weather", "smart", "alarm"]
    chosen_word = random.choice(word_list)
    guessed_word = ["_"] * len(chosen_word)
    attempts = 6
    used_letters = set()

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
            messagebox.showerror("Failure", "Out of attempts! Try again.")
            attempts_label.config(text=f"Attempts Left: {attempts}")

    hangman_window = tk.Toplevel()
    hangman_window.title("Hangman Puzzle")
    tk.Label(hangman_window, text="Solve the Hangman to turn off the alarm!", font=("Helvetica", 14)).pack(pady=10)

    status_label = tk.Label(hangman_window, text=" ".join(guessed_word), font=("Helvetica", 16))
    status_label.pack(pady=10)

    guess_entry = tk.Entry(hangman_window, font=("Helvetica", 14))
    guess_entry.pack(pady=10)

    submit_button = tk.Button(hangman_window, text="Submit", command=check_guess, font=("Helvetica", 12))
    submit_button.pack(pady=10)

    attempts_label = tk.Label(hangman_window, text=f"Attempts Left: {attempts}", font=("Helvetica", 12))
    attempts_label.pack(pady=10)

    used_letters_label = tk.Label(hangman_window, text="Used Letters: ", font=("Helvetica", 12))
    used_letters_label.pack(pady=10)


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
        tk.Label(root, text="Start Address").grid(row=0, column=0)
        self.start_entry = tk.Entry(root)
        self.start_entry.grid(row=0, column=1)
        tk.Label(root, text="Destination Address").grid(row=1, column=0)
        self.destination_entry = tk.Entry(root)
        self.destination_entry.grid(row=1, column=1)
        tk.Label(root, text="Arrival Time (HH:MM)").grid(row=2, column=0)
        self.arrival_entry = tk.Entry(root)
        self.arrival_entry.grid(row=2, column=1)
        self.enter_button = tk.Button(root, text="Enter", command=self.calculate_time)
        self.enter_button.grid(row=3, column=1)
        self.alarm_label = tk.Label(root, text="", fg="red")
        self.alarm_label.grid(row=4, columnspan=2)

    def calculate_time(self):
        start = self.start_entry.get()
        destination = self.destination_entry.get()
        arrival_time_str = self.arrival_entry.get()

        try:
            arrival_time = datetime.strptime(arrival_time_str, "%H:%M").replace(
                year=datetime.now().year, month=datetime.now().month, day=datetime.now().day
            )
            travel_time = get_travel_time(start, destination)
            if travel_time:
                leave_time = calculate_leave_time(arrival_time, travel_time)
                self.alarm_label.config(text=f"Recommended Leave Time: {leave_time.strftime('%H:%M')}")
                if messagebox.askyesno("Set Alarm", "Would you like to set an alarm?"):
                    self.start_alarm_thread(leave_time)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter arrival time in HH:MM format.")

    def start_alarm_thread(self, leave_time):
        def alarm_loop():
            while True:
                current_time = datetime.now()
                if current_time >= leave_time:
                    play_alarm()
                    break
                time.sleep(1)

        threading.Thread(target=alarm_loop, daemon=True).start()


# Main Application
root = tk.Tk()
app = AlarmClockApp(root)
root.mainloop()
