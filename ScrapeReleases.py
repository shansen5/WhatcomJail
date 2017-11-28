#!/usr/bin/python3

import pdb

import sys
import sqlite3
from lxml import html
import requests
from datetime import datetime, timedelta

arguments = sys.argv

def print_usage():
    print( "Usage: " )
    print( "ScrapeReleases.py from_date to_date" )

def daterange( d1, d2 ):
    return( d1 + timedelta( days = i ) for i in range(( d2 - d1 ).days + 1 ))

if ( len( arguments ) < 3 ):
    print_usage()
    sys.exit( 1 )

from_date = datetime.strptime( arguments[1], "%m/%d/%Y" ).date()
to_date = datetime.strptime( arguments[2], "%m/%d/%Y" ).date()
url_string = 'http://apps2.whatcomcounty.us/onlineapps/jailrosters/releases/releasev.jsp?date='
sql = '''INSERT INTO releases( name_id, name, description, release_dt ) \
        VALUES( ?,?,?,? )'''
db = sqlite3.connect( 'jail2.sqlite' )
        
def process_day( d ):
    url =  url_string + d.strftime( '%m/%d/%Y' )
    page = requests.get( url )
    # print( 'Processing page: ', url )
    tree = html.fromstring(page.content)
    records = tree.xpath( 'body/table[2]/tr/td[2]/table/tr[1]/td/table/tr[3]/td/table/tr' )
    # print ( 'Number of releases: ', len( records ) - 2 )

    rec_num = 0
    id = ''
    name = ''
    description = ''
    values_list = list()
    line_count = 0
    for child in records:
        if ( rec_num < 2 ):
            rec_num = rec_num + 1
        else:
            #The following reverses the id string, to obscure the identity slightly.
            id = child[0].text[::-1].strip()
            name = child[1].text.strip()
            description = child[2].text.strip()
            date_string = child[3].text + ' ' + child[4].text
            try:
                release_dt = datetime.strptime( date_string, "%Y / %m / %d %H:%M" )
            except ValueError:
                release_dt = datetime.strptime( child[3].text, "%Y / %m / %d" )
            values_list.append(( id, name, description, release_dt ))
            line_count = line_count + 1
            if ( line_count >= 50 ):
                cursor = db.cursor()
                cursor.executemany( sql, values_list )
                db.commit()
                cursor.close()
                line_count = 0
                values_list = list()
                print( "Inserted 50 records" )
    
    if ( line_count > 0 ):
        cursor = db.cursor()
        cursor.executemany( sql, values_list )
        db.commit()
        cursor.close()
        print( 'Inserted ' + str( line_count ) + ' records' )

for d in daterange( from_date, to_date ):
    process_day( d )

