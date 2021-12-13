from datetime import datetime
from os import times
import subprocess  # for unix commands
from subprocess import Popen, PIPE  # for unix commands
import re  # regex

# graphing
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# get current time in h:m:s military time format #unused...
def getTime():
    current = datetime.now()
    current = current.strftime("%H:%M:%S")
    return current


# ping the ip address, with a data point being printed once every (inter) hours over a total of (hours). Add to (filePath)
def ping(hours, inter, filePath):
    command = (
        "timeout "
        + str(hours)
        + "h fping 1.1.1.1 -l -b 4096 -p 33.3 -o -D -Q "
        + str(inter)
        + " 2>&1 | tee "
        + filePath
    )
    subprocess.call(
        command, shell=True
    )  # ping 1.1.1.1 with -b data size every 33.3 ms. // -o=timestamp // -D=delay // -Q=quiet // 2>&1=for pipe // tee=append


# The ping command can only seem to print time and data on separate lines so this combines each timestamp with its data point
def combineLines(filePath):
    temp = "./data/temp.txt"
    removeBlanks = "sed -i" + filePath + " '/^[[:space:]]*$/d'"  # remove blank lines
    paste = "paste -s -d ' \\n' " + filePath + " > " + temp  # combine every other line
    move = "mv  " + temp + " " + filePath  # overwrite old data file with new one
    subprocess.call(paste, shell=True)
    subprocess.call(move, shell=True)
    subprocess.call(removeBlanks, shell=True)


# count number of lines in the data file, use only after combineLines()
def countLines(filePath):
    file = open(filePath, "r")
    i = 0
    for line in file:
        i += 1
    file.close()
    return i


# grab data from txt file and add it to array structure
def parseData(filePath, darr, n):
    file = open(filePath, "r")
    i = 0
    for line in file:
        time = re.search("(\d+):(\d+):(\d+)", str(line))
        loss = re.search("\d+%", str(line))
        darr[i][0] = time.group(0)
        darr[i][1] = loss.group(0)
        darr[i][1] = darr[i][1][:-1]

        i += 1
    file.close()
    return darr  # bad data structure practice...


# convert string timestamps from darr[0] to timestamp objects and add them to a separate array
def separateArraysTime(darr, times, n):
    i = 0
    for i in range(n):
        times[i] = datetime.strptime(darr[i][0], "%X")

    return times


# convert string packet loss values from darr[i][1] to integers and add them to separate array
def separateArraysLoss(darr, loss, n):
    i = 0
    for i in range(n):
        loss[i] = int(darr[i][1])
    return loss


def graph(x, y, today, filePath):
    fig, ax = plt.subplots()
    ax.plot(x, y)

    # titles
    plt.title("Packet Loss % Over Time (" + str(today) + ")")
    plt.xlabel("Time")
    plt.ylabel("Packet Loss (%)")

    # set x-axis ticks to be in HH:MM format
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%I:%M %p"))
    fig.autofmt_xdate()  # beautify x-labels

    # set x-axis to have ticks of 1 hr length
    fmt_hours = mdates.HourLocator(interval=1)
    fmt_min = mdates.MinuteLocator(interval=15)  # alternative minute formatter
    ax.xaxis.set_major_locator(fmt_hours)

    ax.plot(x, y)
    plt.savefig(filePath[:-4], dpi=300)


# use today's date as txt filename
today = datetime.today().strftime("%m-%d-%Y")
fileName = today + "_packetLoss.txt"
filePath = "./data/" + fileName
file = open(filePath, "a+")
file.close()


########################################## # CHANGE VALUES HERE # ##########################################
hours = 3  # overall time over which data will be collected (hours)
inter = 300  # time interval for a single data point (seconds), e.g. 5 = 1 data point over 5 seconds
ping(hours, inter, filePath)
combineLines(filePath)
n = countLines(filePath)
########################################## # CHANGE VALUES HERE # ##########################################


darr = [[None for x in range(2)] for y in range(n)]  # data array (darr)
darr = parseData(filePath, darr, n)

# create two separate arrays of proper object types, and store the data in them
times = [datetime for tempDT in range(n)]
loss = [0 for tempint in range(n)]
times = separateArraysTime(darr, times, n)
loss = separateArraysLoss(darr, loss, n)

# graphing
graph(times, loss, today, filePath)
