# -*- coding: utf-8 -*-
# script by Ludovic Lacoste <ludolacost@gmail.com>
#Id,Tz,From,To,Sched,Hours,Rating,Comment,Framerate,Snore,Noise,Cycles,Event


from datetime import datetime
import urllib2
import shutil
import urlparse
import os


def readSB(f):
    sleeps = list()
    keys = f.readline()
    keys = keys.split(',')

    #set to make sure we don't repeat stuff
    unique_sleeps = set()

    while True:
        line = f.readline()
        if not line: break
        #data rows alwys start with a timestamp such as 1406218286546
        if line.startswith('"1'):
            values = line.split(',')

        d = dict(zip(keys, values))

        # processing certain keys
        d["Comment"] = d["Comment"].strip('"').strip('#home').strip('#newmoon').strip('manually added')
        d["Rating"] = d["Rating"].strip('"')

        if (d["Id"] in unique_sleeps):
            print "duplicate sleepcloud entry: " + d["Id"]
        else:
            sleeps.append(d)
        unique_sleeps.add(d["Id"])

    return sleeps

def sleep2dates(sleep):
    sleep_stop = datetime.strptime(sleep['To'], '"%d. %m. %Y %H:%M"')
    sleep_start = datetime.strptime(sleep['From'], '"%d. %m. %Y %H:%M"')
    return [sleep_start, sleep_stop]

#return true if contains midnight
def containsMidnight(dts0, dts1):
    if (dts0.hour > dts1.hour):
        return True
    else:
        return False

def writeIcal(sleeps, f, cleanFlag = False, prettyFlag = False):
    from icalendar import Calendar, Event
    import md5

    cal = Calendar()

    # header data
    cal.add('calscale', 'Gregorian')
    cal.add('method', 'publish')
    cal.add('x-wr-caldesc', "iCal feed from sleep as android data. see https://github.com/stevenqzhang/sleepasandroid2ical")
    cal.add('prodid', 'calendar')
    cal.add('version', '3.0')
    cal.add('X-WR-CALNAME', 'Sleep As Android Import')
    cal.add('X-WR-TIMEZONE', 'America/Los_Angeles')
    summary_fmt = '{Comment} '
    description_fmt = 'Rating {Rating} \n \n Made with github.com/stevenqzhang/sleepasandroid2ical'

    for sleep in sleeps:
        dts = sleep2dates(sleep)

        event = Event()

        if cleanFlag == False:
            event.add('summary', summary_fmt.format(**sleep))
            event.add('description', description_fmt.format(**sleep))
        else:
            event.add('description', "blank")
            event.add('summary', "blank")

        event.add('dtstart', dts[0])
        event.add('dtend', dts[1])

        event['uid'] = md5.new(str(dts[0])+'SleepBot'+str(dts[1])).hexdigest()

        cal.add_component(event)

    if (prettyFlag):

        lastDtendDay = -1
        for event in cal.subcomponents:


            start = event['dtstart'].dt
            stop = event['dtend'].dt


            # define day boundary
            if(start.day != lastDtendDay):
                f.write("================" +start.strftime("%m-%d-%Y")  + "=============<br/>")

            lastDtendDay = stop.day


            # if sleep start is before midnight, and sleep end is after midnight, there should be ...

            containsMidight = containsMidnight(start, stop)

            if(containsMidight):
                f.write("<font color='green'> GOOD! <br/> ")

            f.write("sleep start" + start.strftime('%X') + "<br/> sleep end:" + stop.strftime('%X') + "<br/><br/>")
            
            if(containsMidight):
                f.write("</font>")
                

    else:
        f.write(cal.to_ical())



# from http://stackoverflow.com/a/2067142/1621636
def download(url, fileName=None):
    def getFileName(url,openUrl):
        if 'Content-Disposition' in openUrl.info():
            # If the response has Content-Disposition, try to get filename from it
            cd = dict(map(
                lambda x: x.strip().split('=') if '=' in x else (x.strip(),''),
                openUrl.info()['Content-Disposition'].split(';')))
            if 'filename' in cd:
                filename = cd['filename'].strip("\"'")
                if filename: return filename
        # if no filename was found above, parse it out of the final URL.
        return os.path.basename(urlparse.urlsplit(openUrl.url)[2])

    r = urllib2.urlopen(urllib2.Request(url))
    try:
        fileName = fileName or getFileName(url,r)
        with open(fileName, 'wb') as f:
            shutil.copyfileobj(r,f)
    finally:
        r.close()

if __name__ == "__main__":
    import sys

    download(sys.argv[1], "temp_csv.txt")
    csvfile = open("temp_csv.txt", 'rb')
    sleeps = readSB(csvfile)

    icalfile = open(sys.argv[2], 'wb')

    cleanFlag = False
    if sys.argv[3] == "-c":
        cleanFlag = True

    #todo get these to parse with blanks
    prettyFlag = False
    if sys.argv[4] == "-p":
        prettyFlag = True

    writeIcal(sleeps, icalfile, cleanFlag, prettyFlag)
