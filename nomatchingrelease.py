#!/usr/bin/python

import pdb

import sys
import sqlite3
from datetime import datetime, date

arguments = sys.argv

def print_usage():
    print ( "USAGE:" )
    print ( "nomatchingrelease.py" )

# This program is just to add records for those bookings that do not
# have a matching release.  Presumably this means the person is still
# in the jail, but could also be an error such as a missing release.

if len(arguments) < 1:
    print_usage()
    sys.exit(1)

sql0 = '''SELECT name_id, name, booking_dt FROM bookings WHERE booking_dt >= "2014-01-01 00:00"'''
sql1 = '''SELECT release_dt FROM releases WHERE release_dt in (\
            SELECT min(release_dt) FROM releases WHERE name_id=? AND \
            release_dt >= ? )'''
sql2 = '''INSERT into jail_periods ( name_id, name, booking_dt, release_dt ) \
            VALUES (?, ?, ?, ? )'''

db = sqlite3.connect( 'jail2.sqlite', detect_types=sqlite3.PARSE_DECLTYPES )
cursor0 = db.cursor()
values_list = list()
line_count = 0
previous_id = 0
for booking in cursor0.execute( sql0 ):
    # pdb.set_trace()
    cursor1 = db.cursor()
    name_id = booking[0]
    # There may be multiple charges in the booking.  Skip all but the first.
    if ( name_id == previous_id ):
        continue
    previous_id = name_id
    name = booking[1]
    booking_dt = booking[2]
    cursor1.execute( sql1, ( name_id, booking_dt ) )
    release = cursor1.fetchone()
    if ( release is None ):
        # pdb.set_trace()
        print( 'No release found for booking of ' + name + \
                ' on ' + booking_dt )
        release_dt = None
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
