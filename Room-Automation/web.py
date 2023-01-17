from flask import Flask, render_template, redirect, request, url_for
from datetime import datetime
import time
import sqlite3 as sql
import threading

# To run the app flask --app web --debug run --port 5001
app = Flask(__name__)
conn = sql.connect("database.db", check_same_thread=False)
c = conn.cursor()
arr = [""]
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
    inTime = datetime.strptime(alarmTime, "%I:%M %p")
    outTime = datetime.strftime(inTime, "%H:%M")
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
def pullDifferences(prioritized, weekdays, weekends, weekdayNights, weekendNights, priorityAmPm):
    if priorityAmPm == None:
        pass
    c.execute("SELECT * FROM times")
    times = c.fetchall()
    for items in times:
        if items[0] != prioritized:
            if (prioritized == "None"):
                c.execute('UPDATE times SET prioritized = "None"')
                conn.commit()
            else:
                tableValName = "prioritized"
                amPm = priorityAmPm
                userTimeInput = prioritized
                formatTime(amPm,tableValName,userTimeInput)

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
    arr.pop(0)
    arr.insert(0,turnOffTime)
    print(arr)
    # Running The Actual Code-- Turning on LED Lights, Opening Blinds, Connecting to Speaker, and Possibly Moving Bed

def morningFunc():
    print("Currently running the morning code :)")

def nightTimeFunc():
    print("Currently running the nighttime code :)")

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
        dayOfWeek = int((datetime.now().date()).strftime('%w'))
        itsAWeekend = dayOfWeek == 0 or dayOfWeek == 6
        now = datetime.now()
        currentTime = now.strftime("%H:%M:%S")
        
        if prioritizedFromDB != "None": # Prioritizing the Prioritized Time
            if prioritizedFromDB == currentTime:
                triggerPrioritizedFunc(prioritizedFromDB)
                print(prioritizedFromDB)
            elif prioritizedFromDB == arr[0]:
                arr.insert(0,"")
                c.execute('UPDATE times SET prioritized = "None"')
                conn.commit()
                pass
        else:
            if itsAWeekend:
                if weekendsFromDB == currentTime:
                    morningFunc()
                elif weekendNightsFromDB == currentTime:
                    nightTimeFunc()

            else: # Not a weekend
                if weekdaysFromDB == currentTime:
                    morningFunc()
                elif weekdayNightsFromDB == currentTime:
                    nightTimeFunc()
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
                try:
                    priorityAmPm = request.form['prioritizedTime']
                except:
                    priorityAmPm = None
                weekdays = request.form['weekdays']
                weekends = request.form['weekends']
                weekendNights = request.form['weekendNights']
                weekdayNights = request.form['weekdayNights']
                pullDifferences(prioritized,weekdays,weekends, weekdayNights, weekendNights, priorityAmPm)
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
    app.run(debug=True, use_reloader=False, port=5001)
# TO RUN ON HOST MACHINE host="0.0.0.0"
