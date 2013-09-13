#!/usr/bin/env python
"""Tracks and records activity of windows

Returns: a dict entry per window with first_seen, last_seen, closed (if seen), 
window_id, and person ID fields

"""
import re
import sys
from collections import deque
from collections import defaultdict
from pprint import pprint as pp
try:
	import simplejson as json
except:
	import json

curpid = None

def reset():
	global mywins
	mywins = {}

def dump(my_windows):
	for i in my_windows:
		window = json.dumps(my_windows[i])
		print window

reset()

for line in sys.stdin:
	pid = int(line.split('\t',6)[0])
	ts = int(line.split('\t',6)[1]) 
	dtm = json.loads(line.split('\t')[-1])
	dtmd = dtm['data']
	eventid = int(line.split('\t',6)[2])
	if pid != curpid:
		if curpid is not None:
			dump(mywins)
			reset()
		curpid = pid
	if 'micropilot-user-events' == line.split('\t',6)[3]:
		winid = dtmd.get('windowid',None)
		if winid is not None:
			if winid not in mywins:
				mywins[winid] = {'first_seen':ts,'last_seen':ts,'closed':None,'window_id':winid,'pid':pid}
			elif winid in mywins:
				mywins[winid]['last_seen'] = ts
			if 'close' == dtmd.get('action',None):
				mywins[winid]['closed'] = ts

