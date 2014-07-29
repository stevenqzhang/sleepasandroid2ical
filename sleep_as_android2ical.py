# -*- coding: utf-8 -*-
# script by Ludovic Lacoste <ludolacost@gmail.com>
#Id,Tz,From,To,Sched,Hours,Rating,Comment,Framerate,Snore,Noise,Cycles,Event


from datetime import datetime
import urllib2

def readSB(f):
    sleeps = list()
    keys = f.readline()
    keys = keys.split(',')

    while True:
        line = f.readline()
        if not line: break
        #data rows alwys start with a timestamp such as 1406218286546
        if line.startswith('"1'):
            values = line.split(',')

        d = dict(zip(keys, values))
        sleeps.append(d)

    return sleeps

def sleep2dates(sleep):
    sleep_stop = datetime.strptime(sleep['To'], '"%d. %m. %Y %H:%M"')
    sleep_start = datetime.strptime(sleep['From'], '"%d. %m. %Y %H:%M"')
    return [sleep_start, sleep_stop]

def writeIcal(sleeps, f, fmt):
    from icalendar import Calendar, Event
    import md5

    cal = Calendar()
    cal.add('prodid', 'StevenZhangCalendar')
    cal.add('version', '2.0')
    cal.add('X-WR-CALNAME', 'Sleep As Android Import')
    cal.add('X-WR-TIMEZONE', 'America/Los_Angeles')

    for sleep in sleeps:
        dts = sleep2dates(sleep)

        event = Event()
        event.add('summary', fmt.format(**sleep))
        event.add('dtstart', dts[0])
        event.add('dtend', dts[1])
        event['uid'] = md5.new(str(dts[0])+'SleepBot'+str(dts[1])).hexdigest()

        cal.add_component(event)

    f.write(cal.to_ical())

if __name__ == "__main__":
    import sys

    csvfile = open(sys.argv[1], 'rb')

    sleeps = readSB(csvfile)

    icalfile = open(sys.argv[2], 'wb')
    writeIcal(sleeps, icalfile, 'Sleep {Comment} \n Rating {Rating} \n SleepAndroid')

