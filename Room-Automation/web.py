from flask import Flask, render_template, redirect, request, url_for
import sqlite3 as sql

app = Flask(__name__)
conn = sql.connect("database.db", check_same_thread=False)
c = conn.cursor()

# Creates the Table if it doesnt exist
c.execute("""CREATE TABLE IF NOT EXISTS times(
    prioritized text,
    weekdays text,
    weekends text
)
""")

# Checking for an empty DB-- allows for updating data
def checkValues():
    c.execute("SELECT * FROM times")
    times = c.fetchone()
    if times == None:
        c.execute("INSERT INTO times VALUES (' ', ' ', ' ')")
        print("Created Query")

# This simply prints the values of the DB
def printDB(dbMessage):
    print(dbMessage)
    c.execute("SELECT * FROM times")
    times = c.fetchall()
    for items in times:
        setAlarm(items)
        print(items)

# Checks the format of the input, ie. xx:xx if correct, adds to the DB
def checkTimeFormat(var, val, com):
    for x in var:
        try:
            if( (type(int(x[0])) == int) and (type(int(x[1])) == int) and (x[2] == ":") and (type(int(x[3]) == int) and (type(int(x[4]) == int)) and (len(x) == 5))):
                print("Made it")
                updateDB = 'UPDATE times SET {} = (?)'.format(val)
                c.execute(updateDB, (com,))

            else:
                # TODO add error handling to the front end
                print("Something went wrong")
        except ValueError as e:
            print("Something went wrong, please make sure its in 24 hour format", e)
#    setAlarm()

# Compares value to database, if different runs moves to format checking
def pullDifferences(prioritized, weekdays, weekends ):
    c.execute("SELECT * FROM times")
    times = c.fetchall()
    for items in times:
        if items[0] != prioritized:
            if (prioritized == "None"):
                c.execute('UPDATE times SET prioritized = "None"')
                conn.commit()
            else:
                val = "prioritized"
                var = prioritized.split()
                com = prioritized
                checkTimeFormat(var,val,com)

        if items[1] != weekdays:
            if weekdays == "":
                pass
            else:
                val = "weekdays"
                var = weekdays.split()
                com = weekdays
                checkTimeFormat(var,val,com)

        if items[2] != weekends:
            if weekends == "":
                pass
            else:
                val = "weekends"
                var = weekends.split()
                com = weekends
                checkTimeFormat(var,val,com)

# Setting the alarm when pulling from the DB
def setAlarm(items):
    prioritizedFromDB = items[0]; weekdaysFromDB = items [1]; weekendsFromDB = items[2]
    if(prioritizedFromDB != "None"):
        #TODO add actual alarm feature
        pass

@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            checkValues()
            prioritized = request.form['prioritized']
            weekdays = request.form['weekdays']
            weekends = request.form['weekends']
            pullDifferences(prioritized,weekdays,weekends)
            conn.commit()
        except TypeError as e:
            print("Exception Thrown!", e)
    printDB(dbMessage="Searching db")
    c.execute("SELECT * FROM times")
    data = c.fetchall()
    return render_template('index.html', data = data)

@app.route('/database', methods = ['POST', 'GET'])
def postDB():
    c.execute("SELECT * FROM times")
    data = c.fetchall()
    return render_template('template.html', data = data)

if __name__ == "__main__":
    app.run()