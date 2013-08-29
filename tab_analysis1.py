#!/usr/bin/env python
import re
import sys
import logging
from collections import deque
from collections import defaultdict
from pprint import pprint as pp
try:
	import simplejson as json
except:
	import json

## Initialize
opens = {}
opensbyuser = {}

def openpercentages(opens):
	sm=0
	for i in opens:
		sm+=opens[i]['num tabs']
	for ii in opens:
		print ii," accounts for ",round((float(opens[ii]['num tabs'])/sm)*100)," percent of all opens"
		# print "...and",ii,"had an average of",round(opens[ii]['pageshows']/float(opens[ii]['num tabs'])),"pageshows per tab"
		# print "...and",ii,"averaged",opens[ii]['num children']/float(opens[ii]['num children']),"children"

def windowopennewtabs():
	vv=0
	vvpgshw=0
	qq=0
	qqpgshw=0
	aa=0
	for line in sys.stdin:
		me = json.loads(line)
		if 'new window open' == me['born_by']:
			aa+=1
			if me['window_id'] is not None and me['window_id']!= 3:
				vv+=1
				vvpgshw+=me['actions']['tab-pageshow']
			elif me['window_id'] is not None and me['window_id']== 3:
				qq+=1
				qqpgshw+=me['actions']['tab-pageshow']
	print vv," new window opens NOT IN first window, or ",round(float(vv)/aa*100)," percent"
	print round(float(vvpgshw)/vv)," pageshows per tab when NOT IN first window, or"
	print qq," new window opens IN first window, or ",round(float(qq)/aa*100)," percent"
	print round(float(qqpgshw)/qq)," pageshows per tab when IN first window, or"
	print aa," total tabs here"

def statsbyopentype(opens,me,bb):
	if bb in opens[uu]:
		opensbyuser[bb]['num tabs']+=1
		opensbyuser[bb]['pageshows']+=me['actions']['tab-pageshow']
		opensbyuser[bb]['num children']+=len(me['children'])
	else:
		opensbyuser[bb]= {'num tabs': 1, 'pageshows':0, 'num children':0}
		opensbyuser[bb]['pageshows']+=me['actions']['tab-pageshow']
		opensbyuser[bb]['num children']+=len(me['children'])
	return opens

def statsbyusertypes(opens,me,uu,bb):
	if bb in opensbyuser[uu]:
		opensbyuser[uu][bb]['num tabs']+=1
		opensbyuser[uu][bb]['pageshows']+=me['actions']['tab-pageshow']
		opensbyuser[uu][bb]['num children']+=len(me['children'])
	else:
		opensbyuser[uu][bb] = {'num tabs':1,'pageshows':0,'num children':0}
		opensbyuser[uu][bb]['pageshows']+=me['actions']['tab-pageshow']
		opensbyuser[uu][bb]['num children']+=len(me['children'])
	return opensbyuser


recents = deque([],30)
### Streaming Script
tabid = None
usertypes = json.load(open("usertypes.json"))
uniqueusertypes={}
mysteries = 0
opensoverall=defaultdict(int)
eachuser_opentypes={}
who_opens_how={}
for l in usertypes:
	eachuser_opentypes[l]=defaultdict(int)
	if usertypes[l] not in uniqueusertypes:
		uniqueusertypes[usertypes[l]] = 1
	elif usertypes[l] in uniqueusertypes:
		uniqueusertypes[usertypes[l]]+=1
print uniqueusertypes
for line in sys.stdin:
	# pid = int(line.split('\t',6)[0])
	# ts = int(line.split('\t',6)[1])
	# dtm = json.loads(line.split('\t')[-1])
	# recents.append([dtm])
	# if len(recents) > 10:
	# 	# print recents[-10][0]
	# 	tabid = recents[-10][0].get('tabid',None)	
	# if tabid == 13704331361511 and 1079450378 == pid:
	# 	print recents
	# 	break
	# if int(line.split('\t',6)[1]) in range(1370463482265-1000,1370463482265+1000) and 1180274566 == int(line.split('\t',6)[0]):
	# 	dtm = json.loads(line.split('\t')[-1])
	# 	print(dtm['data'])
	me = json.loads(line)
	### scatter: offspring by lifespan ###
	# if me['pid'] not in usertypes:
	opensoverall[me['born_by']]+=1
	eachuser_opentypes[str(me['pid'])][me['born_by']]+=1
	if me['born_by'] not in who_opens_how:
		who_opens_how[me['born_by']]={}
		for k in uniqueusertypes:
			who_opens_how[me['born_by']][k]=[]
	if me['pid'] not in who_opens_how[me['born_by']][str(usertypes[str(me['pid'])])]:
		who_opens_how[me['born_by']][str(usertypes[str(me['pid'])])].append(me['pid'])
	try:
		uu = usertypes[str(me['pid'])]
		if uu not in opensbyuser:
			opensbyuser[uu] = {}
		bb = me.get("born_by","null result")
		if bb not in opensbyuser[uu]:
			opensbyuser[uu][bb] = {'num tabs':1,'num children':0,'pageshows':0}
		mm = me.get("pid","null result")
		if bb is 'new window open' and me['window_id'] is not None and me['window_id']!= 3:
			bb = "Not First Window"
		elif bb is 'new window open' and me['window_id'] is not None and me['window_id']== 3:
			bb = "First Window"
		opensbyuser = statsbyusertypes(opens,me,uu,bb)
	except:
		print me['pid']
		mysteries+=1
# pp(opensbyuser)
# pp(who_opens_how)
for h in eachuser_opentypes:
	mysum = 0
	for dh in eachuser_opentypes[h]:
		mysum+=eachuser_opentypes[h][dh]
	for pdh in eachuser_opentypes[h]:
		eachuser_opentypes[h][pdh] = float(eachuser_opentypes[h][pdh])/mysum*100
print "\n\nWho opens How?"
for d in who_opens_how:
	print "Percentage of each group that uses",d
	for s in who_opens_how[d]:
		print s,":",round(float(len(who_opens_how[d][s]))/uniqueusertypes[s]*100)
# for user in uniqueusertypes:
# 	print "\n\nData for "+ str(uniqueusertypes[user]) + " " + user + "'s:"
# 	usertypeopens = opensbyuser[user]
# 	openpercentages(usertypeopens)
print mysteries,"Free Willy tabs"
totaltabs=0
for s in opensoverall:
	totaltabs+=opensoverall[s]
for o in opensoverall:
	print o,"accounts for",opensoverall[o]/float(totaltabs)*100
# for k in 
fh=open("each_user_tabopens.json","w")
fh.write(json.dumps(eachuser_opentypes))
fh.close()
# windowopennewtabs()

