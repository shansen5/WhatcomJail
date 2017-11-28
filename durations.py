#!/usr/bin/python

import pdb

import sys
import sqlite3
from datetime import datetime, date

arguments = sys.argv

def print_usage():
    print ( "USAGE:" )
    print ( "durations.py" )

if len(arguments) < 1:
    print_usage()
    sys.exit(1)

sql0 = '''SELECT id, booking_row, release_row FROM bookings_releases'''
sql1 = '''SELECT julianday( r.release_dt ) - julianday( b.booking_dt ) \
            FROM releases r, bookings b \
            WHERE b.id = ? and r.id = ?'''
sql2 = '''UPDATE bookings_releases SET duration = ? \
            WHERE id = ?'''

db = sqlite3.connect( 'jail2.sqlite', detect_types=sqlite3.PARSE_DECLTYPES )
cursor0 = db.cursor()
values_list = list()
line_count = 0
cursor0.execute( sql0 )
cursor1 = db.cursor()
cursor2 = db.cursor()
bookings_releases = cursor0.fetchall()
for br in bookings_releases:
    br_row = br[0]
    booking_row = br[1]
    release_row = br[2]
    if ( booking_row is None or release_row is None ):
        continue
    # pdb.set_trace()
    cursor1.execute( sql1, ( booking_row, release_row ))
    duration = cursor1.fetchone()
    cursor2.execute( sql2, ( float(duration[0]), br_row ))
db.commit()
cursor0.close()
cursor1.close()
cursor2.close()

sys.exit(0)
