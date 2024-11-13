# Introduction
Hello,
This is TravelClock. TravelClock is a handy tool that allows users to input an origin address, destination address, and desired arrival time and be recommended a perfect time to leave origin address to arrive at destination address at the desired arrival time. This application utilizes two APIs. The first, DistanceMatrix.ai is used to calculate estimated travel time. The second, OpenWeatherAPI is used to determine what the weather is like in area and calculates if travel time will be affected. This clock is no ordinary clock however. This clock creates an alarm clock for users as a reminder to leave at the recommended time. This alarm utilizes live data and adapts to the ever changing landscape of traffic. A 20-minute drive can turn into a 30-minute drive due to weather complications or traffic congestions. So the alarm clock adjusts its time based on these factors. 

# How to Install
### 1. Clone Repository
    git clone https://github.com/dknguyen12/clock-project.git

### 2. Install Dependencies
    pip install -r requirements.txt

### 3. Run clock.py
    python clock.py

### 4. Input Destination and Start Address
    Example: 1354 Stonewall Dr, Oakland, CA

### 5. Input Arrival Time (24-Hour)
    Example: 15:26 (03:26PM)

### 6. Press Enter
    Once enter is pressed, the UI will ask if an alarm clock is wanted, if wanted it will display the recommended time to leave start address.

