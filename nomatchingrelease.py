#!/usr/bin/python

# import pdb

import sys
import sqlite3
from datetime import datetime, date

arguments = sys.argv

def print_usage():
    print ( "USAGE:" )
    print ( "nomatchingrelease.py from_date" )

# This program is just to add records for those bookings that do not
# have a matching release.  Presumably this means the person is still
# in the jail, but could also be an error such as a missing release.

if len(arguments) < 2:
    print_usage()
    sys.exit(1)

from_date = datetime.strptime( arguments[1], "%m/%d/%Y" ).date()

sql0 = '''SELECT rowid, name_id, name, booking_dt FROM bookings \
            WHERE booking_dt >= ?'''
sql1 = '''SELECT rowid, release_dt FROM releases WHERE release_dt in (\
            SELECT min(release_dt) FROM releases WHERE name_id=? AND \
            release_dt >= ? )'''
sql2 = '''INSERT into bookings_releases ( booking_row, release_row ) \
            VALUES (?, null)'''

db = sqlite3.connect( 'jail2.sqlite', detect_types=sqlite3.PARSE_DECLTYPES )
cursor0 = db.cursor()
values_list = list()
line_count = 0
previous_id = 0
start = from_date.strftime( '%Y-%m-%d 00:00' )
# pdb.set_trace()
for booking in cursor0.execute( sql0, (start, )):
    cursor1 = db.cursor()
    booking_row = booking[0]
    name_id = booking[1]
    release = None
    # only do this for the first booking charge for the same person, same booking date
    if ( name_id != previous_id ):
        previous_id = name_id
        name = booking[2]
        booking_dt = booking[3]
        cursor1.execute( sql1, ( name_id, booking_dt ) )
        release = cursor1.fetchone()
        cursor1.close()
        if ( release is None ):
            # pdb.set_trace()
            print( 'No release found for booking of ' + name + \
                    ' on ' + booking_dt )
            values_list.append(( booking_row, ))
            line_count = line_count + 1
            if ( line_count >= 10 ):
                # pdb.set_trace()
                cursor2 = db.cursor()
                cursor2.executemany( sql2, values_list )
                db.commit()
                cursor2.close()
                line_count = 0
                values_list = list()
                print( 'Inserted 50 records' )    

cursor0.close()

if ( line_count > 0 ):
    cursor2 = db.cursor()
    cursor2.executemany( sql2, values_list )
    db.commit()
    cursor2.close()
    print( 'Inserted ' + str( line_count ) + ' records' )
    
sys.exit(0)
