from flask import Flask, render_template, redirect, request, url_for
from datetime import datetime
import datetime
import time
import serial
import sqlite3 as sql
import threading

# To run the app flask --app web --debug run --port 5001
app = Flask(__name__)
conn = sql.connect("database.db", check_same_thread=False)
c = conn.cursor()
prioritizedReset = ['']
prioritizedShutOff = ['']
# Creates the Table if it doesnt exist
c.execute("""CREATE TABLE IF NOT EXISTS times(
    prioritized text,
    weekdays text,
    weekends text,
    weekdayNights text,
    weekendNights text,
    cancel int
)
""")

# Formats the time to 24 Hours
def formatTime(amPm, tableValName, userTimeInput):
    alarmTime = "{} {}".format(userTimeInput, amPm)
    inTime = datetime.datetime.strptime(alarmTime, "%I:%M %p")
    outTime = datetime.datetime.strftime(inTime, "%H:%M")
    outTimeSplit = outTime.split()
    checkTimeFormat(outTime,tableValName, outTimeSplit)

# Checking for an empty DB-- allows for updating data
def checkValues():
    c.execute("SELECT * FROM times")
    times = c.fetchone()
    if times == None:
        c.execute("INSERT INTO times VALUES (' ', ' ', ' ', ' ', ' ', ' ')")
        print("Created Query")

# This simply prints the values of the DB
def printDB(dbMessage):
    print(dbMessage)
    c.execute("SELECT * FROM times")
    times = c.fetchall()
    for items in times:
        print(items)

# Checks the format of the input, ie. xx:xx if correct, adds to the DB
def checkTimeFormat(outTime, tableValName, outTimeSplit):
    print(outTimeSplit)
    for x in outTimeSplit:
        try:
            if( (type(int(x[0])) == int) and (type(int(x[1])) == int) and (x[2] == ":") and (type(int(x[3]) == int) and (type(int(x[4]) == int)) )):
                updateDB = 'UPDATE times SET {} = (?)'.format(tableValName)
                c.execute(updateDB, (outTime,))

            else:
                # TODO add error handling to the front end
                print("Something went wrong")
        except ValueError as e:
            print("Something went wrong, please make sure its in 24 hour format", e)

# Compares value to database, if different runs moves to format checking
def pullDifferences(prioritized, weekdays, weekends, weekdayNights, weekendNights):
    c.execute("SELECT * FROM times")
    times = c.fetchall()
    for items in times:
        if items[0] != prioritized:
            if (prioritized == ''):
                c.execute('UPDATE times SET prioritized = "None"')
                conn.commit()
            else:
                c.execute("UPDATE times SET prioritized = (?)", (prioritized,))

        if items[1] != weekdays:
            if weekdays == "":
                pass
            else:
                tableValName = "weekdays"
                amPm = "AM"
                userTimeInput = weekdays
                formatTime(amPm, tableValName,userTimeInput)

        if items[2] != weekends:
            if weekends == "":
                pass
            else:
                tableValName = "weekends"
                amPm = "AM"
                userTimeInput = weekends
                formatTime(amPm, tableValName,userTimeInput)

        if items[3] != weekdayNights:
            if weekdayNights == "":
                pass
            else:
                tableValName = "weekdayNights"
                amPm = "PM"
                userTimeInput = weekdayNights
                formatTime(amPm, tableValName,userTimeInput)    

        if items[4] != weekendNights:
            if weekendNights == "":
                pass
            else:
                tableValName = "weekendNights"
                amPm = "PM"
                userTimeInput = weekendNights
                formatTime(amPm, tableValName,userTimeInput)    

def triggerPrioritizedFunc(prioritizedFromDB):
    # Adding 12 Hours to the Time So it will disregard the morning alarm
    prioritizedFromDB = prioritizedFromDB.split()
    for x in prioritizedFromDB:
        firstTwoDigits = (int(x[0] + x[1]))
        secondTwoDigits = x[3] + x[4]
    firstTwoDigits = firstTwoDigits + 12
    if firstTwoDigits >= 24:
        firstTwoDigits = firstTwoDigits - 24
        if firstTwoDigits in range(0,10):
            firstTwoDigits = "0{}".format(firstTwoDigits)
    turnOffTime = "{}:{}:00".format(firstTwoDigits, secondTwoDigits)
    prioritizedReset.pop(0)
    prioritizedReset.insert(0,turnOffTime)

def morningFunc():
    ser.write(b"ON\n") # This turns LED Lights on
    print("Currently running the morning code :)")

def nightTimeFunc():
    ser.write(b"ON\n") # This turns LED Lights on
    print("Currently running the nighttime code: ")
    

def onOff():
    # Turn off the led lights
    ser.write(b"ON\n") # This turns LED Lights on/off
    print("Turn Off")


def prioritizedFunc(prioritizedReset, prioritizedFromDB):
    print("PRIORITIZED! Prioritized will reset at: ", prioritizedReset)
    prioritizedDateTime = (datetime.datetime.strptime(prioritizedFromDB, "%H:%M:%S"))
    addedMinutes = (prioritizedDateTime + datetime.timedelta(minutes=5)).strftime("%H:%M:%S")
    prioritizedShutOff.pop(0)
    prioritizedShutOff.insert(0, addedMinutes)
    print(prioritizedShutOff)
    onOff()


# Setting the alarm when pulling from the DB
def setAlarm():
    c.execute("SELECT * FROM times")
    times = c.fetchall()
    for items in times:
        pass
    if items[5] != 1:
        alarms = 0
    else:
        alarms = 1
    while alarms == 1:
        c.execute("SELECT * FROM times")
        times = c.fetchall()
        for items in times:
            pass
        if items[0] != "None":
            prioritizedFromDB = "{}{}".format(items[0],":00")
        else:
            prioritizedFromDB = items[0]
        weekdaysFromDB = "{}{}".format(items [1],":00"); weekendsFromDB = "{}{}".format(items[2],":00"); weekdayNightsFromDB = "{}{}".format(items[3],":00"); weekendNightsFromDB = "{}{}".format(items[4],":00"); toggleAlarmFromDB = items[5]
        if toggleAlarmFromDB == 0:
            alarms = 0
        dayOfWeek = int((datetime.datetime.now().date()).strftime('%w'))
        itsAWeekend = dayOfWeek == 0 or dayOfWeek == 6
        now = datetime.datetime.now()
        currentTime = now.strftime("%H:%M:%S")
        
        if prioritizedFromDB != "None": # Prioritizing the Prioritized Time
            # If current time is equal to the inputed time, run code
            if prioritizedFromDB == currentTime:
                triggerPrioritizedFunc(prioritizedFromDB)
                prioritizedFunc(prioritizedReset,prioritizedFromDB)

            elif currentTime == prioritizedShutOff[0]:
                onOff() # Turns off after 5 minutes
            
            elif currentTime == prioritizedReset[0]:
                prioritizedReset.pop(0)
                prioritizedReset.insert(0,"")
                c.execute('UPDATE times SET prioritized = "None"')
                conn.commit()
                printDB(dbMessage="Updating Priority to None")
    
        else:
            if itsAWeekend:
                weekendNightsDateTime = (datetime.datetime.strptime(weekendNightsFromDB, "%H:%M:%S"))
                weekendNightsTurnOn = (weekendNightsDateTime - datetime.timedelta(hours=3)).strftime("%H:%M:%S") # Subtracting 3 hours to call the start function
                weekendDateTime = (datetime.datetime.strptime(weekendsFromDB, "%H:%M:%S"))
                weekendTurnOff = (weekendDateTime + datetime.timedelta(minutes=30)).strftime("%H:%M:%S") # Adding 5 minutes to the time to turn off the led lights and speaker TODO: add a shutoff time of 15 seconds for the speaker
                if weekendNightsTurnOn == currentTime:
                    nightTimeFunc()
                elif weekendNightsFromDB == currentTime:
                    onOff()
                
                if weekendsFromDB == currentTime:
                    morningFunc()
                if weekendTurnOff == currentTime:
                    onOff()


            else: # Not a weekend
                # Initializing the db input into a datetime object
                weekdayNightsDateTime = (datetime.datetime.strptime(weekdayNightsFromDB, "%H:%M:%S"))
                weekdayNightsTurnOn = (weekdayNightsDateTime - datetime.timedelta(hours=3)).strftime("%H:%M:%S") # Subtracting 3 hours to call the start function
                print("Weekdaynights turn on: ", weekdayNightsTurnOn)
                weekdayDateTime = (datetime.datetime.strptime(weekdaysFromDB, "%H:%M:%S"))
                weekdayTurnOff = (weekdayDateTime + datetime.timedelta(minutes=30)).strftime("%H:%M:%S") # Adding 5 minutes to the time to turn off the led lights and speaker TODO: add a shutoff time of 15 seconds for the speaker
                print("Weekday mornings shut off", weekdayTurnOff)

                if weekdayNightsTurnOn == currentTime:
                    nightTimeFunc() # Turns on the lights 3 hours before
                elif weekdayNightsFromDB == currentTime:
                    onOff() # Turns off the lights at the time the user specifies

                if weekdaysFromDB == currentTime:
                    morningFunc() 
                elif weekdayTurnOff == currentTime:
                    onOff() # 30 minutes later turn off the lights 
        print(currentTime)
        time.sleep(1)

@app.route('/', methods = ["GET", "POST"])
def index():
    checkValues()
    if request.method == "POST":
        try:
            # Checks if alarms are canceled
            alarmToggle = request.form['toggleAlarms']
            if alarmToggle == "Toggle":
                c.execute("SELECT * FROM times")
                alarms = c.fetchall()
                for x in alarms: 
                    if x[5] == 1:
                        toggle = 0
                    else:
                        toggle = 1
                c.execute("UPDATE times SET cancel = (?)", (toggle,))
                conn.commit()
        except:
            try:
                prioritized = request.form['prioritized']
                weekdays = request.form['weekdays']
                weekends = request.form['weekends']
                weekendNights = request.form['weekendNights']
                weekdayNights = request.form['weekdayNights']
                pullDifferences(prioritized,weekdays,weekends, weekdayNights, weekendNights)
                conn.commit()
            except TypeError as e:
                print("Exception Thrown!", e)
    printDB(dbMessage="Searching db")
    c.execute("SELECT * FROM times")
    data = c.fetchall()
    for items in data:
        if items[5] == 1:
            alarm = "Turn Off Alarms"
        else:
            alarm = "Turn On Alarms"
    t1 = threading.Thread(target=setAlarm)
    if threading.active_count() > 2:
        pass
    else:
        t1.start()
    return render_template('index.html', data = data, alarm = alarm)

@app.route('/database', methods = ['POST', 'GET'])
def postDB():
    c.execute("SELECT * FROM times")
    data = c.fetchall()
    for x in data:
        if x[5] == 1:
            alarm = "On"
        else:
            alarm = "Off"
    return render_template('template.html', data = data, alarm = alarm)

if __name__ == "__main__":
    ser = serial.Serial("/dev/ttyUSB0", 9600, tiemout = 1)
    ser.flush()
    app.run(debug=True, use_reloader=False, port=5001)
# TO RUN ON HOST MACHINE host="0.0.0.0"
