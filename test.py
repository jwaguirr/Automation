time = "09:02"
time  = time.split()
arr = []
for x in time:
    twoDigits = (int(x[0] + x[1]))
    lastTwoDigits = x[3] + x[4]
twoDigits = twoDigits + 12
if twoDigits >= 24:
    twoDigits = twoDigits - 24
    print(twoDigits)
    if twoDigits in range(0,10):
        twoDigits = "0{}".format(twoDigits)
time = "{}:{}:00".format(twoDigits, lastTwoDigits)
arr.insert(0,time)
print(arr)
arr.pop(0)
print(arr)