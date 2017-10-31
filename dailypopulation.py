#!/usr/bin/python

import pdb

import sys
import sqlite3
from datetime import datetime, date, timedelta

arguments = sys.argv

def print_usage():
    print ( "USAGE:" )
    print ( "dailypopulation.py" )

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

if len(arguments) < 1:
    print_usage()
    sys.exit(1)

sql0 = '''SELECT booking_dt as "booking_dt [datetime]", release_dt as "release_dt [datetime]" FROM jail_periods'''
sql1 = '''INSERT INTO daily_population (day, count) VALUES( ?, ?)'''

db = sqlite3.connect( 'jail2.sqlite', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES )
cursor0 = db.cursor()
start_date = date( 2000, 1, 1 )
end_date = date( 2017, 10, 26 )
inmate_days = {}
for inmate_day in daterange( start_date, end_date ):
    day_str = inmate_day.strftime( '%Y-%m-%d' )
    inmate_days[ day_str ] = 0
for stay in cursor0.execute( sql0 ):
    # pdb.set_trace()
    cursor1 = db.cursor()
    booking_dt = stay[0]
    release_dt = stay[1]
    if ( booking_dt is None ):
        continue
    start = datetime.strptime( booking_dt, '%Y-%m-%d %H:%M' ).date()
    if ( release_dt is None ):
        continue
    end = datetime.strptime( release_dt, '%Y-%m-%d %H:%M' ).date() + timedelta(1)
    for inmate_day in daterange( start, end ):
        day_str = inmate_day.strftime( '%Y-%m-%d' )
        inmate_days[ day_str ] = inmate_days[ day_str ] + 1
cursor0.close()

values_list = list()
cursor1 = db.cursor()
for inmate_day in daterange( start_date, end_date ):
    day_str = inmate_day.strftime( '%Y-%m-%d' )
    values_list.append(( inmate_day, inmate_days[ day_str ]))
    # print( day_str + ',' + str( inmate_days[ day_str ] ))
cursor1.executemany( sql1, values_list )
db.commit()
print( 'Inserted ' + str( len( inmate_days )) + ' records' )
cursor1.close()

sys.exit(0)
