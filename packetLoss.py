from datetime import datetime
import os
from os import times
import subprocess  # for unix commands
from subprocess import Popen, PIPE  # for unix commands
import re  # regex

# graphing
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# get current time in h:m:s military time format (unused)
def getTime():
    current = datetime.now()
    current = current.strftime("%H:%M:%S")
    return current


# ping the ip address, with a data point being printed once every (interval) (units) over a 
# total of (quantity)(units). 
# Add this information to (filePath)
def ping(quantity, units, filePath):
    interval = 1
    command = (
        "timeout "
        + str(quantity) + " "
        + str(units)
        + " fping 1.1.1.1 -l -b 4096 -p 33.3 -o -D -Q "
        + str(interval)
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
    return darr


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


def graph(x, y, today, filePath, increments, xunits):
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
    if(xunits == 'h'):
        fmt = mdates.HourLocator(interval=increments)
    else:
        fmt = mdates.MinuteLocator(interval=increments)  # alternative minute formatter
    ax.xaxis.set_major_locator(fmt)

    ax.plot(x, y)
    plt.savefig(filePath[:-4], dpi=300)


def execute(quantity, units, increments, xunits):
    # use today's date as txt filename
    today = datetime.today().strftime("%m-%d-%Y")
    fileName = today + "_packetLoss.txt"
    path = "./data"
    
    #create directory ./data if it does not already exist
    if(not os.path.exists(path)):
         createDir = "mkdir " + path   
         subprocess.call(createDir, shell=True)
    path = path + "/" + fileName
    file = open(path, "a+")
    file.close()

    ########################################## # CHANGE VALUES HERE # ##########################################
    hours = 3  # overall time over which data will be collected (hours)
    inter = 300  # time interval for a single data point (seconds), e.g. 5 = 1 data point over 5 seconds
    ping(quantity, units, path)
    combineLines(path)
    n = countLines(path)
    ########################################## # CHANGE VALUES HERE # ##########################################

    darr = [[None for x in range(2)] for y in range(n)]  # data array (darr)
    darr = parseData(path, darr, n)

    # create two separate arrays of proper object types, and store the data in them
    times = [datetime for tempDT in range(n)]
    loss = [0 for tempint in range(n)]
    times = separateArraysTime(darr, times, n)
    loss = separateArraysLoss(darr, loss, n)

    # graphing
    graph(times, loss, today, path)


def main():
    initial = "Express input in this format: \n10m\n^This would track for 10 minutes.\n\n5h\n^This would track for 5 hours, etc.\n\n(Days/seconds are not currently supported as a quantity).\n\nEnter q to quit.\nEnter h to repeat this message."
    error = "There appears to be an issue with the last input. Please try again.\n"
    print("================================================================================")
    print(initial)
    print("================================================================================")
    while True:
        userInput = input("Time to track packet loss (%)?: \n")
        userInput.lower
        userInput.strip
        if userInput == "q":
            exit(0)
        elif userInput == "h":
            print(initial)
        elif re.fullmatch("(\d+)(m|h)", userInput) == None:
            print(error)
        else:
            quantity = re.search("(\d+)", userInput)[0] #how many units of time the program will track packet loss for
            units = re.search("(m|h)", userInput)[0] #units of time for quantity
            axisInput = input("Enter the x-axis gradiations in the same format: \n")
            if re.fullmatch("(\d+)(m|h)", axisInput) == None:
                print(error)
            else:
                increments = re.search("(\d+)", axisInput)[0] #increment distance
                axisUnits = re.search("(m|h)", axisInput)[0] #units of increments
                execute(quantity, units, increments, axisUnits)


if __name__ == "__main__":
    main()
