from datetime import datetime
import datetime

now = (datetime.datetime.strptime("13:01:00", "%H:%M:%S"))
now = (now - datetime.timedelta(hours=3)).strftime("%H:%M:%S")
print(now)

