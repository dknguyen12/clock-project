import tkinter as tk
from tkinter import Tk, Label, Entry, Button, Frame, messagebox, ttk
import requests
from datetime import datetime, timedelta
import threading
import time
from playsound import playsound
import random
import pygame

DISTANCEMATRIX_API_KEY = 'XBJdEDmtBIwogdfsYrJb0baiOzF6qSKA0m4v98TJDaZyc1Jo6If2gL7yKYTDWMYJ'
WEATHER_API_KEY = '4dcfdb40bf998f293937f62769af9926'
ALARM_SOUND_PATH = '/Users/dk/Desktop/clock proejct/audio/audio.wav'

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
    # If travel_time is already a timedelta, subtract directly
    if isinstance(travel_time, timedelta):
        return arrival_time - travel_time
    # Otherwise, assume travel_time is in seconds and convert it
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
def play_alarm(app):
    # Play the alarm sound and schedule the Hangman puzzle on the main thread
    threading.Thread(target=lambda: playsound(ALARM_SOUND_PATH), daemon=True).start()
    app.root.after(0, hangman_puzzle)


# Alarm Clock App
class AlarmClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Alarm Clock")

        # Real-time clock label
        self.clock_label = Label(root, font=("Helvetica", 14), fg="green")
        self.clock_label.grid(row=0, column=0, columnspan=4, pady=10)
        self.update_clock()

        # Entry fields for start address and city
        Label(root, text="Start Address").grid(row=1, column=0)
        self.start_entry = Entry(root)
        self.start_entry.grid(row=1, column=1)

        Label(root, text="Start City").grid(row=1, column=2)
        self.start_city_entry = Entry(root)
        self.start_city_entry.grid(row=1, column=3)

        # Entry fields for destination address and city
        Label(root, text="Destination Address").grid(row=2, column=0)
        self.destination_entry = Entry(root)
        self.destination_entry.grid(row=2, column=1)

        Label(root, text="Destination City").grid(row=2, column=2)
        self.destination_city_entry = Entry(root)
        self.destination_city_entry.grid(row=2, column=3)

        # Arrival time entry
        Label(root, text="Arrival Time (HH:MM)").grid(row=3, column=0)
        self.arrival_entry = Entry(root)
        self.arrival_entry.grid(row=3, column=1)

        self.enter_button = Button(root, text="Enter", command=self.calculate_time)
        self.enter_button.grid(row=4, column=1)

        self.alarm_label = Label(root, text="", fg="red")
        self.alarm_label.grid(row=5, columnspan=2)

        # Frame for displaying active alarms
        Label(root, text="Active Alarms:").grid(row=6, column=0, sticky="w")
        self.alarm_frame = Frame(root)
        self.alarm_frame.grid(row=7, column=0, columnspan=4, sticky="ew")

        self.task_button = tk.Button(root, text="Add Task", command=self.open_task_window)
        self.task_button.grid(row=8, column=0, pady=10)

        self.active_alarms = {}  # Dictionary to store alarms

    def update_clock(self):
        # Update the clock label with the current time
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=f"Current Time: {current_time}")
        self.root.after(1000, self.update_clock)

    def calculate_time(self):
        # Get inputs from the GUI
        start_address = self.start_entry.get()
        start_city = self.start_city_entry.get()
        start = f"{start_address}, {start_city}"

        destination_address = self.destination_entry.get()
        destination_city = self.destination_city_entry.get()
        destination = f"{destination_address}, {destination_city}"

        arrival_time_str = self.arrival_entry.get()

        try:
            # Parse the arrival time
            arrival_time = datetime.strptime(arrival_time_str, "%H:%M").replace(
                year=datetime.now().year, month=datetime.now().month, day=datetime.now().day
            )

            # Fetch travel time
            travel_time = get_travel_time(start, destination)

            # Fetch and apply weather conditions (using start city)
            weather = get_weather_conditions(start_city) if start_city else None
            if travel_time:
                if weather:
                    travel_time = adjust_for_weather_conditions(weather, travel_time)
                leave_time = calculate_leave_time(arrival_time, travel_time)

                # Display calculated leave time
                self.alarm_label.config(text=f"Recommended Leave Time: {leave_time.strftime('%H:%M')}")

                # Confirm alarm setup
                if messagebox.askyesno("Set Alarm", "Would you like to set an alarm?"):
                    self.add_alarm(leave_time, arrival_time, start, destination)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter arrival time in HH:MM format.")

    def add_alarm(self, leave_time, arrival_time, start, destination):
        # Fetch travel time to store in alarm data
        travel_time = get_travel_time(start, destination)
        if travel_time is None:
            return  # Exit if travel time could not be calculated
        
        # Generate a unique ID for the alarm using leave_time and a random value
        alarm_id = f"{leave_time}_{random.randint(1000, 9999)}"

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
            "travel_time": timedelta(seconds=travel_time),  # Store travel time here
            "thread": alarm_thread,
            "stop_event": stop_event,
        }

        # Update the alarm list in the GUI
        self.update_alarm_list()

    def start_alarm_thread(self, leave_time, alarm_id, stop_event):
        while not stop_event.is_set():
            current_time = datetime.now()
            if current_time >= leave_time:
                self.trigger_alarm(alarm_id)
                break
            time.sleep(1)

    def trigger_alarm(self, alarm_id):
        if alarm_id in self.active_alarms:
            del self.active_alarms[alarm_id]
            self.update_alarm_list()

        self.root.after(0, lambda: play_alarm(self))

    def update_alarm_list(self):
        for widget in self.alarm_frame.winfo_children():
            widget.destroy()

        for alarm_id, alarm_data in self.active_alarms.items():
            leave_time = alarm_data["leave_time"]
            arrival_time = alarm_data["arrival_time"]
            start = alarm_data["start"]
            destination = alarm_data["destination"]

            alarm_label = Label(
                self.alarm_frame,
                text=f"Alarm: {leave_time.strftime('%H:%M')} | Arrival: {arrival_time.strftime('%H:%M')} | From: {start} | To: {destination}",
                anchor="w",
            )
            alarm_label.pack(fill="x", padx=5, pady=2)

            delete_button = Button(
                self.alarm_frame,
                text="Delete",
                command=lambda alarm_id=alarm_id: self.delete_alarm(alarm_id),
            )
            delete_button.pack(fill="x", padx=5, pady=2)

    def delete_alarm(self, alarm_id):
        if alarm_id in self.active_alarms:
            self.active_alarms[alarm_id]["stop_event"].set()
            del self.active_alarms[alarm_id]
            self.update_alarm_list()

    def adjust_alarm_times(self):
        """Adjust alarms based on tasks and restart threads."""
        for alarm_id, alarm_data in self.active_alarms.items():
            total_task_time = sum(task["duration"] for task in alarm_data.get("tasks", []))
            adjusted_leave_time = calculate_leave_time(
                alarm_data["arrival_time"],
                alarm_data["travel_time"] + timedelta(minutes=total_task_time),
            )
            
            # Update leave time
            alarm_data["leave_time"] = adjusted_leave_time

            # Stop the current thread
            if "stop_event" in alarm_data:
                alarm_data["stop_event"].set()

            # Create a new stop_event
            stop_event = threading.Event()

            # Restart the thread with the updated leave time
            alarm_thread = threading.Thread(
                target=self.start_alarm_thread,
                args=(adjusted_leave_time, alarm_id, stop_event),
                daemon=True,
            )
            alarm_thread.start()

            # Update the dictionary with the new thread and stop_event
            alarm_data["thread"] = alarm_thread
            alarm_data["stop_event"] = stop_event

        self.update_alarm_list()

    def open_task_window(self):
        """Opens a new window to add tasks."""
        task_window = tk.Toplevel(self.root)
        task_window.title("Add Task")

        # Task label entry
        tk.Label(task_window, text="Task Label").grid(row=0, column=0, padx=5, pady=5)
        task_label_entry = tk.Entry(task_window)
        task_label_entry.grid(row=0, column=1, padx=5, pady=5)

        # Task duration entry
        tk.Label(task_window, text="Duration (minutes)").grid(row=1, column=0, padx=5, pady=5)
        task_duration_entry = tk.Entry(task_window)
        task_duration_entry.grid(row=1, column=1, padx=5, pady=5)

        # Dropdown menu for alarms
        tk.Label(task_window, text="Select Alarm").grid(row=2, column=0, padx=5, pady=5)
        alarm_dropdown = ttk.Combobox(task_window, values=list(self.active_alarms.keys()), state="readonly")
        alarm_dropdown.grid(row=2, column=1, padx=5, pady=5)

        # Submit button
        def submit_task():
            label = task_label_entry.get()
            try:
                duration = int(task_duration_entry.get())
            except ValueError:
                messagebox.showerror("Input Error", "Please enter a valid duration in minutes.")
                return

            selected_alarm = alarm_dropdown.get()

            if not label or not selected_alarm:
                messagebox.showerror("Input Error", "All fields are required.")
                return

            # Add task to the selected alarm
            if "tasks" not in self.active_alarms[selected_alarm]:
                self.active_alarms[selected_alarm]["tasks"] = []

            self.active_alarms[selected_alarm]["tasks"].append({"label": label, "duration": duration})
            self.adjust_alarm_times()
            self.update_alarm_list()
            task_window.destroy()

        tk.Button(task_window, text="Submit", command=submit_task).grid(row=3, column=0, columnspan=2, pady=10)

    def update_alarm_list(self):
        """Update the alarm list with tasks."""
        for widget in self.alarm_frame.winfo_children():
            widget.destroy()

        for alarm_id, alarm_data in self.active_alarms.items():
            leave_time = alarm_data["leave_time"]
            arrival_time = alarm_data["arrival_time"]
            start = alarm_data["start"]
            destination = alarm_data["destination"]

            alarm_label = tk.Label(
                self.alarm_frame,
                text=f"Alarm: {leave_time.strftime('%H:%M')} | Arrival: {arrival_time.strftime('%H:%M')} | From: {start} | To: {destination}",
                anchor="w",
            )
            alarm_label.pack(fill="x", padx=5, pady=2)

            # Display tasks
            if "tasks" in alarm_data:
                for task in alarm_data["tasks"]:
                    task_label = tk.Label(
                        self.alarm_frame,
                        text=f"  - Task: {task['label']} ({task['duration']} min)",
                        anchor="w",
                    )
                    task_label.pack(fill="x", padx=20, pady=1)

            delete_button = tk.Button(
                self.alarm_frame,
                text="Delete",
                command=lambda alarm_id=alarm_id: self.delete_alarm(alarm_id),
            )
            delete_button.pack(fill="x", padx=5, pady=2)

class WelcomePage:
    def __init__(self, root):
        self.root = root
        self.root.title("Welcome to Smart Alarm Clock")

        # Welcome message
        self.message_label = Label(
            root,
            text="Welcome to the Smart Alarm Clock!",
            font=("Helvetica", 16),
            fg="blue"
        )
        self.message_label.pack(pady=20)

        # Real-time clock label
        self.clock_label = Label(root, font=("Helvetica", 14))
        self.clock_label.pack(pady=10)

        # Open App button
        self.open_app_button = Button(
            root,
            text="Open App",
            font=("Helvetica", 12),
            command=self.open_alarm_clock_app
        )
        self.open_app_button.pack(pady=20)

        # Start the clock update
        self.update_clock()

    def update_clock(self):
        # Update the clock label with the current time
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=f"Current Time: {current_time}")
        self.root.after(1000, self.update_clock)

    def open_alarm_clock_app(self):
        # Destroy the welcome page and open the alarm clock app
        self.root.destroy()
        self.launch_alarm_clock_app()

    def launch_alarm_clock_app(self):
        # Create a new root for the Alarm Clock App
        alarm_root = Tk()
        app = AlarmClockApp(alarm_root)
        alarm_root.mainloop()

# Main Application
root = Tk()
welcome_page = WelcomePage(root)
root.mainloop()