#!/usr/bin/python

import pdb

import sys
import sqlite3
from datetime import datetime, date

arguments = sys.argv

def print_usage():
    print ( "USAGE:" )
    print ( "computeperiods.py" )

if len(arguments) < 1:
    print_usage()
    sys.exit(1)

sql0 = '''SELECT name_id, name, release_dt FROM releases'''
sql1 = '''SELECT booking_dt FROM bookings WHERE booking_dt in (\
            SELECT max(booking_dt) FROM bookings WHERE name_id=? AND \
            booking_dt <= ? )'''
sql1a = '''SELECT booking_dt FROM bookings WHERE booking_dt in (\
            SELECT max(booking_dt) FROM bookings WHERE name=? AND \
            booking_dt <= ? )'''
sql2 = '''INSERT into jail_periods ( name_id, name, booking_dt, release_dt ) \
            VALUES (?, ?, ?, ? )'''

db = sqlite3.connect( 'jail2.sqlite', detect_types=sqlite3.PARSE_DECLTYPES )
cursor0 = db.cursor()
values_list = list()
line_count = 0
for release in cursor0.execute( sql0 ):
    # pdb.set_trace()
    cursor1 = db.cursor()
    name_id = release[0]
    name = release[1]
    release_dt = release[2]
    if ( name_id == '0' ):
        cursor1.execute( sql1a, ( name, release_dt ) )
    else:
        cursor1.execute( sql1, ( name_id, release_dt ) )
    booking = cursor1.fetchone()
    if ( booking is None ):
        print( 'No previous booking found for release of ' + name + \
                ' on ' + release_dt )
        booking_dt = None
    else:
        booking_dt = booking[0]
    values_list.append(( name_id, name, booking_dt, release_dt ))
    line_count = line_count + 1
    if ( line_count >= 50 ):
        # pdb.set_trace()
        cursor2 = db.cursor()
        cursor2.executemany( sql2, values_list )
        db.commit()
        cursor2.close()
        line_count = 0
        values_list = list()
        print( 'Inserted 50 records' )    
    cursor1.close()

cursor0.close()

if ( line_count > 0 ):
    cursor2 = db.cursor()
    cursor2.executemany( sql2, values_list )
    db.commit()
    cursor2.close()
    print( 'Inserted ' + str( line_count ) + ' records' )
    
sys.exit(0)
