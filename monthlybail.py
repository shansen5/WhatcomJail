#!/usr/bin/python

import pdb

import sys
import sqlite3
from datetime import datetime, date, timedelta

arguments = sys.argv

total_bail = 0
total_count = 0
total_time = 0
counts = 0

def print_usage():
    print ( "USAGE:" )
    print ( "monthlybail.py from_date to_date" )


if len(arguments) < 3:
    print_usage()
    sys.exit(1)

sql0 = '''select count(*), b.name, b.booking_dt, sum( b.bail ), \
            julianday( r.release_dt ) - julianday( b.booking_dt ) \
          from bookings b, releases r, bookings_releases br \
          where b.rowid = br.booking_row and r.rowid = br.release_row \
            and b.booking_dt > ? and b.booking_dt < ? \
            and upper(r.description) like 'TIME SERVED%' group by b.booking_dt, b.name'''
                        
db = sqlite3.connect( 'jail2.sqlite', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES )
cursor0 = db.cursor()

from_date = datetime.strptime( arguments[1], "%m/%d/%Y" ).date()
to_date = datetime.strptime( arguments[2], "%m/%d/%Y" ).date()

yr = from_date.year
mo = from_date.month
prev_yr = yr
prev_mo = mo
averages = {}
# The records from the cursor will come in order sorted by the date.
for booking in cursor0.execute( sql0, ( from_date, to_date )):
    count = booking[0]
    booking_dt = datetime.strptime( booking[2], '%Y-%m-%d %H:%M' )
    bail = booking[3]
    duration = booking[4]
    if ( bail == 0 ):
        continue
    booking_mo = booking_dt.month
    booking_yr = booking_dt.year
    if ( booking_yr < yr or ( booking_yr == yr and booking_mo < mo )):
        print( 'Unusual - ' + booking + ' - ' + str( mo ) + '/' + str( yr ))
        continue
    if ( booking_yr > yr or booking_mo > mo ):
        mon_str = str( yr ) + '-' + "%02d" % mo
        averages[ mon_str ] = ( total_bail / counts, 
                float( total_count ) / counts, total_time / counts, counts )
        print( mon_str + ', ' + str(averages[ mon_str ][0]) + ', ' + 
                str(averages[ mon_str ][1]) + ', ' + 
                str(averages[ mon_str ][2]) + ', ' + str(averages[ mon_str ][3] ))
        yr = booking_yr
        mo = booking_mo
        total_bail = 0
        total_count = 0
        total_time = 0
        counts = 0
    counts += 1
    total_bail += bail
    total_count += count
    total_time += duration
    # pdb.set_trace()
mon_str = str( yr ) + '-' + "%02d" % mo
averages[ mon_str ] = ( total_bail / counts, 
        float( total_count ) / counts, total_time / counts, counts )
print( mon_str + ', ' + str(averages[ mon_str ][0]) + ', ' + 
        str(averages[ mon_str ][1]) + ', ' + 
        str(averages[ mon_str ][2] ) + ', ' + str(averages[ mon_str ][3] ))


cursor0.close()

sys.exit(0)
