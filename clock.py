import tkinter as tk
from tkinter import messagebox
import requests
from datetime import datetime, timedelta
import threading
import time
from playsound import playsound

DISTANCEMATRIX_API_KEY = 'XBJdEDmtBIwogdfsYrJb0baiOzF6qSKA0m4v98TJDaZyc1Jo6If2gL7yKYTDWMYJ'
WEATHER_API_KEY = '4dcfdb40bf998f293937f62769af9926'
ALARM_SOUND_PATH = '/Users/dk/Desktop/clock project/audio/audio.wav'

def get_travel_time(start, destination):
    # Updated to use DistanceMatrix.ai API
    url = f'https://api.distancematrix.ai/maps/api/distancematrix/json?origins={start}&destinations={destination}&key={DISTANCEMATRIX_API_KEY}'
    response = requests.get(url).json()
    if response['status'] == 'OK':
        travel_duration = response['rows'][0]['elements'][0]['duration']['value']  # in seconds
        return travel_duration
    else:
        messagebox.showerror("Error", "Could not retrieve travel time.")
        return None
        
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

def calculate_leave_time(arrival_time, travel_time):
    return arrival_time - timedelta(seconds=travel_time)
    
def check_for_weather(start):
    weather = get_weather_conditions(start)
    return weather

def check_for_delays_and_weather(start, destination, weather):
    travel_time = get_travel_time(start, destination)
    adjusted_travel_time = adjust_for_weather_conditions(weather, travel_time)
    return adjusted_travel_time
    
class AlarmClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Alarm Clock")
    
        #text box for start address
        tk.Label(root, text="Start Address").grid(row=0, column=0)
        self.start_entry = tk.Entry(root)
        self.start_entry.grid(row=0, column=1)

        #text box for start city
        tk.Label(root, text="City").grid(row=0, column=2)
        self.start_city_entry = tk.Entry(root)
        self.start_city_entry.grid(row=0, column=3)
    
        #text box for destination address
        tk.Label(root, text="Destination Address").grid(row=1, column=0)
        self.destination_entry = tk.Entry(root)
        self.destination_entry.grid(row=1, column=1)
        
        #text box for destination city
        tk.Label(root, text="City").grid(row=1, column=2)
        self.destination_city_entry = tk.Entry(root)
        self.destination_city_entry.grid(row=1, column=3)

        #text box for arrival time entry
        tk.Label(root, text="Arrival Time (HH:MM)").grid(row=2, column=0)
        self.arrival_entry = tk.Entry(root)
        self.arrival_entry.grid(row=2, column=1)
        
        #enter button
        self.enter_button = tk.Button(root, text="Enter", command=self.calculate_time)
        self.enter_button.grid(row=3, column=1)
        
        self.alarm_label = tk.Label(root, text="", fg="red")
        self.alarm_label.grid(row=4, columnspan=2)
    
    def calculate_time(self):
        start = self.start_entry.get()
        destination = self.destination_entry.get()
        arrival_time_str = self.arrival_entry.get()
        
        try:
            arrival_time = datetime.strptime(arrival_time_str, "%H:%M")
            travel_time = get_travel_time(start, destination)
            if travel_time:
                leave_time = calculate_leave_time(arrival_time, travel_time)
                self.alarm_label.config(text=f"Recommended Leave Time: {leave_time.strftime('%H:%M')}")
                
                if messagebox.askyesno("Set Alarm", "Would you like to set an alarm?"):
                    self.start_alarm_thread(start, destination, leave_time)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter arrival time in HH:MM format.")
    
    def start_alarm_thread(self, start, destination, initial_leave_time):
        start = self.start_city_entry.get()
        def alarm_loop(leave_time):
            weather = check_for_weather(start)
            while True:
                travel_time = check_for_delays_and_weather(start, destination, weather)
                potential_new_leave_time = calculate_leave_time(datetime.now() + timedelta(seconds=travel_time), travel_time)
                if abs((potential_new_leave_time - leave_time).total_seconds()) > 300:
                    leave_time = potential_new_leave_time
                    self.alarm_label.config(text=f"Updated Leave Time: {leave_time.strftime('%H:%M')}")
                current_time = datetime.now()
                if current_time >= leave_time:
                    messagebox.showinfo("Alarm", "Time to leave!")
                    playsound(ALARM_SOUND_PATH)
                    break
                time.sleep(60)
        
        threading.Thread(target=alarm_loop, args=(initial_leave_time,), daemon=True).start()
    
root = tk.Tk()
app = AlarmClockApp(root)
root.mainloop()