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

sql0 = '''SELECT rowid, name_id, name, release_dt FROM releases'''
sql1 = '''SELECT rowid, booking_dt, matched FROM bookings WHERE booking_dt in (\
            SELECT max(booking_dt) FROM bookings WHERE name_id=? AND \
            booking_dt <= ? ) AND name_id = ?'''
sql1a = '''SELECT rowid, booking_dt, matched FROM bookings WHERE booking_dt in (\
            SELECT max(booking_dt) FROM bookings WHERE name=? AND \
            booking_dt <= ? ) AND name = ?'''
sql2 = '''INSERT into bookings_releases ( booking_row, release_row ) \
            VALUES (?, ?)'''
sql3 = '''UPDATE bookings SET matched=1 WHERE rowid = ?'''

db = sqlite3.connect( 'jail2.sqlite', detect_types=sqlite3.PARSE_DECLTYPES )
cursor0 = db.cursor()
values_list = list()
line_count = 0
cursor0.execute( sql0 )
releases = cursor0.fetchall()
for release in releases:
    # pdb.set_trace()
    cursor1 = db.cursor()
    release_row = release[0]
    name_id = release[1]
    name = release[2]
    release_dt = release[3]
    if ( name_id == '0' ):
        # Match records based on name.  For years prior to use of ids.
        cursor1.execute( sql1a, ( name, release_dt, name ) )
    else:
        # Match records based on ids.
        cursor1.execute( sql1, ( name_id, release_dt, name_id ) )
    booking = None
    bookings = cursor1.fetchall()
    # pdb.set_trace()
    if ( bookings ):
        booking = bookings[0]
        booking_row = booking[0]
    else:
        # If we failed matching by id, also try the name.
        if ( name_id != '0' ):
            cursor1.execute( sql1a, ( name, release_dt, name ) )
        bookings = cursor1.fetchall()
        if ( bookings ):
            booking = bookings[0]
            booking_row = booking[0]
        else:
            print( 'No previous booking found for release of ' + name + \
                ' on ' + release_dt )
            booking_row = None
    if ( booking is None ):
            values_list.append(( None, release_row ))
    else:
        if ( booking[2] == 1 ):
            print( 'Booking found for release of ' + name + ' was already matched' )
            values_list.append(( None, release_row ))
        else:
            cursor2 = db.cursor()
            values_list.append(( booking_row, release_row ))
            cursor2.execute( sql3, ( booking_row, ))
            i = 1
            while ( i < len( bookings )):
                booking = bookings[i]
                booking_row = booking[0]
                values_list.append(( booking_row, release_row ))
                cursor2.execute( sql3, ( booking_row, ))
                i += 1
            cursor2.close()
            db.commit()

    line_count = line_count + 1
    if ( line_count >= 50 ):
        # pdb.set_trace()
        cursor2 = db.cursor()
        cursor2.executemany( sql2, values_list )
        cursor2.close()
        db.commit()
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
