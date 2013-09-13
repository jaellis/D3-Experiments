#!/usr/bin/env python
"""This script is designed to take processed data from the tabber2.py code
	and return various statistics about the data
"""

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
	"""Calculate percentage of tab opens attributable to each open type
	Args:
		opens: dict of open types and number opened via each method
	Return:
		nothing; just prints percentages
	"""
	sm=0
	for i in opens:
		sm+=opens[i]['num_tabs']
	for ii in opens:
		print ii," accounts for ",round((float(opens[ii]['num_tabs'])/sm)*100)," percent of all opens"
		# print "...and",ii,"had an average of",round(opens[ii]['pageshows']/float(opens[ii]['num_tabs'])),"pageshows per tab"
		# print "...and",ii,"averaged",opens[ii]['num_children']/float(opens[ii]['num_children']),"children"

def windowopennewtabs():
	"""Stand-alone function that takes lines from stdin and separates tabs based on their container window
	Args:
		none
	Returns:
		prints statistics about tabs that were opened by "new window open" in the first window versus later (2nd, 3rd, etc.) windows 
	"""

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
				vvpgshw+=me['total_actions']['tab-pageshow']
			elif me['window_id'] is not None and me['window_id']== 3:
				qq+=1
				qqpgshw+=me['total_actions']['tab-pageshow']
	print vv,"new window opens NOT IN first window, or",round(float(vv)/aa)*100,"percent"
	print round(float(vvpgshw)/vv)," pageshows per tab when NOT IN first window"
	print qq," new window opens IN first window, or ",round(float(qq)/aa)*100," percent"
	print round(float(qqpgshw)/qq)," pageshows per tab when IN first window"
	print aa," total tabs here"

def personal_percentages(group_data):
	"""Takes group data and calculates percent of each open type per user
	"""
	group_redux={}
	birth_forms_percentages={}
	final={}
	for v in group_data:
		personalsum=0
		personalpercentages={}
		for mv in group_data[v]:
			personalsum+=group_data[v][mv]
		for mv2 in group_data[v]:
			personalpercentages[mv2] = group_data[v][mv2]/float(personalsum)*100
		group_redux[v]=personalpercentages
	for v2 in group_redux:
		for vv in group_redux[v2]:
			if vv not in birth_forms_percentages:
				birth_forms_percentages[vv]=[]
			birth_forms_percentages[vv].append(group_redux[v2][vv])
		final[vv] = sum(birth_forms_percentages[vv])/float(len(birth_forms_percentages[vv])*100)
	return final

def overall_tab_open_types_percentage(opensoverall):
	""" Print percentage of all tabs that were opened with each method
	Args: 
		opensoverall: defaultdict of open types and their aggregates
	"""
	totaltabs=0
	for s in opensoverall:
		totaltabs+=opensoverall[s]
	for o in opensoverall:
		print o,"accounts for",opensoverall[o]/float(totaltabs)*100
	print totaltabs,"total tabs"

def tabopens_percent_within_group(who_opens_how):
	"""Prints the percentage of each group that has used a particular open method
	(unique users per group)
	"""
	print "\n\nWho opens How?"
	for d in who_opens_how:
		print "Percentage of each group that uses",d
		for s in who_opens_how[d]:
			print s,":",round(float(len(who_opens_how[d][s]))/uniqueusertypes[s]*100)
	for user in uniqueusertypes:
		print "\n\nData for "+ str(uniqueusertypes[user]) + " " + user + "'s:"
		usertypeopens = opensbyuser[user]
		openpercentages(usertypeopens)

def breakdown_opens_by_usertype(opensbyuser):
	""" Print stats of tab-open method by user type """
	for utype in opensbyuser:
		print utype + ":\n"
		this_utype_sum=0
		for bornbymethod in opensbyuser[utype]:
			this_utype_sum+=opensbyuser[utype][bornbymethod]['num_tabs']
		for bbm in opensbyuser[utype]:
			print bbm,"accounts for",(opensbyuser[utype][bbm]['num_tabs']/float(this_utype_sum))*100,"percent of tab opens"
			print bbm,"opened tabs create, on average,",opensbyuser[utype][bbm]['num_children']/float(opensbyuser[utype][bbm]['num_tabs']),"tabs"
			print bbm,"opened tabs have, on average,",opensbyuser[utype][bbm]['pageshows']/float(opensbyuser[utype][bbm]['num_tabs']),"page loads"

tabid = None
usertypes = json.load(open("usertypes.json"))
uniqueusertypes={}
mysteries = 0
opensoverall=defaultdict(int)
eachuser_opentypes={}
who_opens_how={}
usergroup_percentage_within = {}
percent_of_a_group_opening={}
seen_pids={}

""" Get unique usertypes and counts for each """
for l in usertypes:
	eachuser_opentypes[l]=defaultdict(int)
	if usertypes[l] not in uniqueusertypes:
		uniqueusertypes[usertypes[l]] = 1
	uniqueusertypes[usertypes[l]]+=1
print uniqueusertypes
### Initialize for open-type breakdown within group
for i in uniqueusertypes:
	usergroup_percentage_within[i] = {}

for line in sys.stdin:
	# pid = int(line.split('\t',6)[0])
	# ts = int(line.split('\t',6)[1])
	# dtm = json.loads(line.split('\t')[-1])

	me = json.loads(line)

	""" Breakdown of open-types by user group """
	if me['pid'] not in usergroup_percentage_within[usertypes[str(me['pid'])]]:
		usergroup_percentage_within[usertypes[str(me['pid'])]][me['pid']] = defaultdict(int)
	usergroup_percentage_within[usertypes[str(me['pid'])]][me['pid']][me['born_by']]+=1

	### Add to sum (tabs per open type)
	opensoverall[me['born_by']]+=1

	### Add to sum (tabs per open type), within each user
	eachuser_opentypes[str(me['pid'])][me['born_by']]+=1


	if me['born_by'] not in who_opens_how:
		who_opens_how[me['born_by']]={}
		for k in uniqueusertypes:
			who_opens_how[me['born_by']][k]=[]
	if me['pid'] not in who_opens_how[me['born_by']][str(usertypes[str(me['pid'])])]:
		who_opens_how[me['born_by']][str(usertypes[str(me['pid'])])].append(me['pid'])
	try:
		utype = usertypes[str(me['pid'])]
		if utype not in opensbyuser:
			opensbyuser[utype] = {}
		bb = me.get("born_by","null result")
		if bb not in opensbyuser[utype]:
			opensbyuser[utype][bb] = {'num_tabs':0,'num_children':0,'pageshows':0}
		### add to open-type entry under a particular user
		opensbyuser[utype][bb]['num_tabs']+=1
		opensbyuser[utype][bb]['num_children']+=len(me['children'])
		opensbyuser[utype][bb]['pageshows']+=me['total_actions']['tab-pageshow']

		if bb is 'new window open' and me['window_id'] is not None and me['window_id']!= 3:
			bb = "Not First Window"
		elif bb is 'new window open' and me['window_id'] is not None and me['window_id']== 3:
			bb = "First Window"
	except:
		### If pid not in usertypes
		mysteries+=1

breakdown_opens_by_usertype(opensbyuser)

""" Calculate percent of opens made with each method per user """
# for h in eachuser_opentypes:
# 	mysum = 0
# 	for dh in eachuser_opentypes[h]:
# 		mysum+=eachuser_opentypes[h][dh]
# 	for pdh in eachuser_opentypes[h]:
# 		eachuser_opentypes[h][pdh] = float(eachuser_opentypes[h][pdh])/mysum*100


fh=open("each_user_tabopens.json","w")
fh.write(json.dumps(eachuser_opentypes))
fh.close()
windowopennewtabs()