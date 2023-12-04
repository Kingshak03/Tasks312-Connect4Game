from flask import Flask,request,make_response,redirect
from datetime import datetime, timedelta



ip_dictionary = {}

def get_ip():
    client_ip = request.headers.get('X-Real-IP')
    #gets the ip check nginx.conf 
    if(client_ip):
        return client_ip
    else:
        return request.remote_addr

def limit_rate(ip_address):
    if(ip_address not in ip_dictionary):
        current_time = datetime.now()
        #zero_datetime = datetime(1, 1, 1, 0, 0, 0, 0)
        record = {'requests': 0, 'blocked_time': current_time, 'request_time_period': current_time,'isBlocked':False, 'first_request_time': current_time}
        ip_dictionary[ip_address] = record
        return success_response()
    else:
        client_record = ip_dictionary[ip_address]
        return handling_function(client_record,ip_address)

def handling_function(client_record,ip_address):
   
    #still supposed to be blocked? 
    current_time = datetime.now()
    blocked_time = client_record['blocked_time']
    blockSec = (current_time - blocked_time).total_seconds()
    number_requests = client_record['requests']

    original_time = client_record['first_request_time']
    totalSec = (current_time - original_time).total_seconds()
    




    if ( 30 >=  blockSec and client_record['isBlocked'] == True):
        return overload_response()
    
    # need to block 
    if (number_requests > 50 and totalSec <= 10):

        return(block_function(client_record))

    #blocked time period is over 
    if( blockSec > 30 and client_record['isBlocked'] == True):
        return(unblock_function(client_record))
    
    # case where more then 50 requests in time more then 10 seconds: 
    if (number_requests > 50 and totalSec > 10):
        return(reset_operations(client_record))
        
    else:
        client_record['requests'] += 1
        client_record['request_time_period'] = current_time
        return success_response()


def reset_operations(client_record):
    current_time = datetime.now()
    client_record['requests'] = 0
    client_record['blocked_time'] = current_time
    client_record['request_time_period'] = current_time
    client_record['isBlocked'] = False
    client_record['first_request_time'] = current_time
    return success_response()

def block_function(client_record):
    current_time = datetime.now()
    client_record['blocked_time'] = current_time
    client_record['isBlocked'] = True
    return overload_response()



def unblock_function(client_record):
    client_record['isBlocked'] = False
    client_record['requests'] = 0
    current_time = datetime.now()
    client_record['first_request_time'] = current_time
    return success_response()



def overload_response():
    response = make_response(redirect('/'), 'Too many requests please try again later.')
    response.status_code = 429
    return response

def success_response():
    response = make_response(redirect('/'), 'Request successful.')
    response.status_code = 200
    return response

