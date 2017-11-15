#!/usr/bin/python

import pdb

import sys
import sqlite3
from datetime import datetime, date, timedelta

arguments = sys.argv

def print_usage():
    print ( "USAGE:" )
    print ( "monthlypopulation.py from_month from_year to_month to_year" )

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def month_year_iter( start_month, start_year, end_month, end_year ):
    ym_start= 12*start_year + start_month - 1
    ym_end= 12*end_year + end_month
    for ym in range( ym_start, ym_end ):
        y, m = divmod( ym, 12 )
        yield y, m+1


if len(arguments) < 5:
    print_usage()
    sys.exit(1)

sql0 = '''SELECT avg(count) FROM daily_population WHERE strftime('%Y-%m', day) like ?'''

db = sqlite3.connect( 'jail2.sqlite', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES )
cursor0 = db.cursor()
month_counts = {}
from_month = int( arguments[1] )
from_year = int( arguments[2] )
to_month = int( arguments[3] )
to_year = int( arguments[4] )

for (yr,mo) in month_year_iter( from_month, from_year, to_month, to_year ):
    # pdb.set_trace()
    mon_str = str(yr) + '-' + "%02d" % mo
    cursor0.execute( sql0, (mon_str,) ) 
    result = cursor0.fetchone()
    if ( result[0] != None ):
        print( mon_str + "," + str( result[0] ))
cursor0.close()

sys.exit(0)
