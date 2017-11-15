#!/usr/bin/python

import pdb

import sys
import sqlite3
from datetime import datetime, date, timedelta

arguments = sys.argv

def print_usage():
    print ( "USAGE:" )
    print ( "dailypopulation.py from_date to_date" )

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

if len(arguments) < 3:
    print_usage()
    sys.exit(1)

from_date = datetime.strptime( arguments[1], "%m/%d/%Y" ).date()
to_date = datetime.strptime( arguments[2], "%m/%d/%Y" ).date()

sql0 = '''SELECT b.booking_dt as "booking_dt [datetime]", 
        r.release_dt as "release_dt [datetime]", \
        br.release_row, br.duration \
        FROM bookings b, releases r, bookings_releases br WHERE b.rowid = br.booking_row \
        AND r.rowid = br.release_row'''
sql1 = '''INSERT INTO daily_population (day, count) VALUES( ?, ?)'''

db = sqlite3.connect( 'jail2.sqlite', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES )
cursor0 = db.cursor()
inmate_days = {}
for inmate_day in daterange( from_date, to_date ):
    day_str = inmate_day.strftime( '%Y-%m-%d' )
    inmate_days[ day_str ] = 0
previous_release = 0
for stay in cursor0.execute( sql0 ):
    # pdb.set_trace()
    cursor1 = db.cursor()
    if ( stay[2] == previous_release ):
        continue
    previous_release = stay[2]
    booking_dt = stay[0]
    if ( booking_dt is None ):
        continue
    release_dt = stay[1]
    if ( release_dt is None ):
        continue
    duration = float( stay[3] )
    start = datetime.strptime( booking_dt, '%Y-%m-%d %H:%M' ).date()
    if ( start < from_date ):
        start = from_date
    end = datetime.strptime( release_dt, '%Y-%m-%d %H:%M' ).date()
    if ( end > to_date ):
        end = to_date
    print( start, end, duration )
    for inmate_day in daterange( start, end ):
        day_str = inmate_day.strftime( '%Y-%m-%d' )
        inmate_days[ day_str ] = inmate_days[ day_str ] + 1
        print( day_str, str( inmate_days[ day_str ] ))
cursor0.close()

values_list = list()
cursor1 = db.cursor()
for inmate_day in daterange( from_date, to_date ):
    day_str = inmate_day.strftime( '%Y-%m-%d' )
    values_list.append(( inmate_day, inmate_days[ day_str ]))
    # print( day_str + ',' + str( inmate_days[ day_str ] ))
cursor1.executemany( sql1, values_list )
db.commit()
print( 'Inserted ' + str( len( inmate_days )) + ' records' )
cursor1.close()

sys.exit(0)
