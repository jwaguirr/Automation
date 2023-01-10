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

def checkValues():
    # Checking for an empty Arr
    c.execute("SELECT * FROM times")
    times = c.fetchone()
    if times == None:
        c.execute("INSERT INTO times VALUES (' ', ' ', ' ')")
        print("Created Query")

def replaceValues(prioritized, weekdays, weekends):
    # Inserting Values into the DB
    c.execute("""UPDATE times SET 
            prioritized = (?),
            weekdays = (?),
            weekends = (?)
            """, (prioritized, weekdays, weekends))
    conn.commit()
    printDB(dbMessage="Final Commit")

def printDB(dbMessage):
    print(dbMessage)
    c.execute("SELECT * FROM times")
    times = c.fetchall()
    for items in times:
        print(items)

@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            checkValues()
            prioritized = request.form['prioritized']
            weekdays = request.form['weekdays']
            weekends = request.form['weekends']
            replaceValues(prioritized,weekdays,weekends)
            conn.commit()
            print('Succesfully Commited')
        except TypeError as e:
            print("Exception Thrown!", e)
    printDB(dbMessage="Searching db")
    return render_template('index.html')

@app.route('/database', methods = ['POST', 'GET'])
def postDB():
    c.execute("SELECT * FROM times")
    data = c.fetchall()
    print(data)
    return render_template('template.html', data = data)
if __name__ == "__main__":
    app.run()