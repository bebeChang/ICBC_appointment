#!/usr/bin/python

import sys
import json
import urllib.request
import urllib.error
import time
import os
import ssl
import http.client
import datetime



# Init from website.
servicePublicId="da8488da9b5df26d32ca58c6d6a7973bedd5d98ad052d62b468d3b04b080ea25"

# Month
expectMonth = "2023-12"

# Fix SSL
if hasattr(ssl, '_create_unverified_context'):
      ssl._create_default_https_context = ssl._create_unverified_context


# Read locations from json files.
def read_location_json(filename):
	with open(filename) as f:
		location_objs = json.load(f)
		ans = {}
		for loc in location_objs:
			obj = loc['pos']
			id = obj['posId']
			ans[id] = obj
		return ans

def send_notification(msg):
	# TODO: add notification to mobile or desktop.
	print(msg)
	#make_bell_sound()

# make a sound in your computer 
def make_bell_sound():
	os.system("say 'ICBC appointment found.'")

def fetch_road_test(token):
    json_body = '{"posIDs":[275,9,8,...],"examType":"5-R-1","examDate":"2023-12-22",...}'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Referer": "https://onlinebusiness.icbc.com/webdeas-ui/booking",
        "User-Agent": "Mozilla/5.0 ...",
        "Authorization": token
    }

    conn = http.client.HTTPSConnection('onlinebusiness.icbc.com')
    conn.request('POST', '/deas-api/v1/web/getAvailableSlots', json_body, headers)
    response = conn.getresponse()
    print('Fetching road test:', response.status, response.reason)  # 打印响应状态和原因
    data = response.read()
    if response.status != 200:
        print('read road test api fail.')
        print(response.status)
        print(response.reason)
        return None
    return json.loads(data)


RED = ""

def fiterByDate(appointments, locations, token):
	ans = []
	for array in appointments:
		for ap in array:
			# check 
			dt = ap['appointmentDt']['date']
			st = ap['startTm']
			et = ap['endTm']
			pos_id = ap['posId']
			loc = locations[pos_id]
			if isAvailable(ap, token):
				# found.
				msg = "%s %s-%s, %s%s" % (dt, st, et, RED, loc['address']) 
				send_notification(msg)
				ans.append(ap)

	return ans

# check slot if available 
def isAvailable(appointment, token):
	dt = appointment['appointmentDt']['date']
	if not dt.startswith(expectMonth):
		return False
	
	if isLock(appointment, token):
		return False

	return True



def isLock(appointment, token):
	appointment['bookedTs'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
	appointment['drvrDriver'] = { "drvrId": 1554703 }
	appointment['instructorDlNum'] = None
	appointment['drscDrvSchl'] = {}
	headers = {"Accept" : "application/json, text/plain, */*", "Content-Type" : "application/json", "Referer" : "https://onlinebusiness.icbc.com/webdeas-ui/booking",\
			 "User-Agent" : " Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36", \
			 "Authorization" : token }
	conn = http.client.HTTPSConnection('onlinebusiness.icbc.com')
	json_body = json.dumps(appointment)
	conn.request('PUT', '/deas-api/v1/web/lock', json_body, headers)
	response = conn.getresponse()
	return response.status == 400


# get login token.
def getToken(user):
    json_body = '{{"drvrLastName":"{}","licenceNumber":"{}","keyword":"{}"}}'.format(*user)
    print("Requesting token with body:", json_body)  # 打印请求体进行检查
    headers = {
        "Expires": "0",
        "Accept": "application/json, text/plain, */*",
        "Cache-control": "no-cache, no-store",
        "Content-Type": "application/json",
        "Referer": "https://onlinebusiness.icbc.com/webdeas-ui/login;type=driver",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
    }
    conn = http.client.HTTPSConnection('onlinebusiness.icbc.com')
    conn.request('PUT', '/deas-api/v1/webLogin/webLogin', json_body, headers)
    response = conn.getresponse()
    print("Response status:", response.status)  # 打印响应状态进行检查
    print("Response reason:", response.reason)  # 打印响应原因进行检查

    if response.status != 200:
        print('Failed to get token:', response.status, response.reason)
        return None
    token = response.getheader('Authorization')
    print('get token', token)
    return token



def main():
    print('start detecting appointments in', expectMonth, '...')
    if len(sys.argv) < 4:
        print("Usage: python3 road_test.py <lastname> <licenseNumber> <keyword>")
        sys.exit(1)

    token = getToken((sys.argv[1], sys.argv[2], sys.argv[3]))
    if token is None:
        print("Error: Unable to obtain token.")
        return

    appointments = fetch_road_test(token)
    if appointments is None:
        print("No appointments found or an error occurred.")
        return

    locations = read_location_json('road_test_positions.json')
    aplist = fiterByDate(appointments, locations, token)
    # ... 后续处理 ...


if __name__ == "__main__":
	# execute only if run as a script
	main()

    
  # python3 road_test.py Chang 3053312 0630












