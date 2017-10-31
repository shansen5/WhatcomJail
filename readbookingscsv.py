#!/usr/bin/python

import pdb

import sys
import csv
import sqlite3
import time
from datetime import datetime, date

arguments = sys.argv

def print_usage():
    print ( "USAGE:" )
    print ( "readbookingscsv.py filename" )

if len(arguments) < 2:
    print_usage()
    sys.exit(1)

file = arguments[1]

values_list = list()
line_count = 0
sql = '''INSERT INTO bookings( name_id, name, charges, arrest_type, bail, booking_dt ) \
                VALUES( ?,?,?,?,?,? )'''
db = sqlite3.connect( 'jail2.sqlite' )
with open(file, 'r') as csvfile:
    reader = csv.reader( csvfile, delimiter=',', quotechar='"')
    # name_id, name, charges, arrest_type, bail, date_string (%m/%d/%Y %H:%M)
    for line in reader:
        cursor = db.cursor()
        line_count = line_count + 1
        # pdb.set_trace()
        booking_dt = date.today()
        try:
            booking_dt = datetime.strptime( line[5], '%m/%d/%Y %H:%M' )
        except( ValueError ):
            temp_date = datetime.strptime( line[5], '%m/%d/%Y' )
            booking_dt = temp_date.replace( hour=0, minute=1 )
            print( "Date exception: " + booking_dt.strftime( "%Y-%m-%d %H:%M" ))
        values_list.append(( line[0], line[1], line[2], line[3], float(line[4]), booking_dt.strftime( "%Y-%m-%d %H:%M" )))

        if ( line_count >= 50 ):
            # pdb.set_trace()
            cursor.executemany( sql, values_list )
            db.commit()
            # print( sql )
            # print( values_list[0] )
            cursor.close()
            line_count = 0
            values_list = list()
            print( 'Inserted 50 records' )    

if ( line_count > 0 ):
    cursor = db.cursor()
    cursor.executemany( sql, values_list )
    db.commit()
    cursor.close()
    print( 'Inserted ' + str( line_count ) + ' records' )
    
sys.exit(0)
