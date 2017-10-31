#!/usr/bin/python3

import pdb

import sys
from lxml import html
import requests
from datetime import datetime, timedelta

arguments = sys.argv

def print_usage():
    print( "Usage: " )
    print( "ScrapeBookings.py from_date to_date" )

def daterange( d1, d2 ):
    return( d1 + timedelta( days = i ) for i in range(( d2 - d1 ).days + 1 ))

if ( len( arguments ) < 3 ):
    print_usage()
    sys.exit( 1 )

from_date = datetime.strptime( arguments[1], "%m/%d/%Y" ).date()
to_date = datetime.strptime( arguments[2], "%m/%d/%Y" ).date()
url_string = 'http://apps2.whatcomcounty.us/onlineapps/jailrosters/bookings/booking.jsp?date='

def process_day( d ):
    url =  url_string + d.strftime( '%m/%d/%Y' )
    page = requests.get( url )
    # print( 'Processing page: ', url )
    tree = html.fromstring(page.content)
    records = tree.xpath( 'body/table[2]/tr/td[2]/table/tr[1]/td/table/tr[3]/td/table/tr' )
    # print ( 'Number of bookings: ', len( records ) - 1 )

    first = True
    id = ''
    name = ''
    charges = ''
    arrest_type = ''
    bail = 0
    for child in records:
        if ( first ):
            first = False
        else:
            #The following reverses the id string, to obscure the identity slightly.
            id = child[0].text[::-1].strip()
            name = child[1].text.strip()
            charges = child[3].text.strip()
            arrest_type = child[4].text.strip()
            bail = float( child[5].text )
            date_string = child[6].text + ' ' + child[7].text
            try:
                booking_dt = datetime.strptime( date_string, "%Y/%m/%d %H:%M" )
                print( '"' + id + '","' + name + '","' + charges + '","' + arrest_type + '","' +str( bail ) + '","' + booking_dt.strftime( "%m/%d/%Y %H:%M" ) + '"' )
            except ValueError:
                try:
                    booking_dt = datetime.strptime( child[6].text, "%Y/%m/%d" )
                    print( '"' + id + '","' + name + '","' + charges + '","' + arrest_type + '","' + str( bail ) + '","' + booking_dt.strftime( "%m/%d/%Y" ) + '"' )
                except ValueError:
                    print( '"' + id + '","' + name + '","' + charges + '","' + str( bail ) + '","1/1/1900"' )
            # print ( "dt_string: ", date_string )
            # print ( "ID: ", id )
            # print ( "Name: ", name )
            # print ( "Charges: ", charges )
            # print ( "Arrest Type: ", arrest_type )
            # print ( "Bail: ", str( bail ))
            # print ( "Booking Date/Time: ", booking_dt.strftime( "%m/%d/%Y %H:%M" ))
    

for d in daterange( from_date, to_date ):
    process_day( d )

#    INSERT INTO persons(id, name) 
#        SELECT 84900, 'BANUELOS, KRYSTINE MONIQUE'
#                FROM dual
#                        WHERE NOT EXISTS (SELECT * FROM persons
#                                                             WHERE id = 84900)
