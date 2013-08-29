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

### ...Engage  ####
activthresh = 180000
tabdeact = {'ts': 0}
lastclick = {'ts': 0}
lasttabopen = {'ts': 0}
lasttracking = {'ts': 0}
rightclickmenu = {'ts': 0}
lasttbpgshw = {'ts': 0}
lasttabactivate = {'ts': 0}
lastaction = {'ts': 0,'type':None}
clickthenopen = False
newtabbutton = False
cmd_click = False
cmdt = False
windowreactivate = False
datsum = 0
# recents = deque([],15)
mytabs = {}
curpid = None
curts = None
actionlist = ['tab-pageshow','scroll','wheel','mouseup','click','urlbar','searchbar','drag']
allopens = {}
prestcount=0
alltabcount=0
opentabs = {}
unknowneventopen=0

def opentypesums(mytabs,pid,datsum,allopens):
	def spinout(opn,sumz):
		for aa in opn:
			print aa," accounts for ",round((opn[aa]/float(sumz))*100)," percent of opens"

	opens={}
	pidsum = 0
	for i in mytabs:
		if mytabs[i]['born_by'] in opens:
			opens[mytabs[i]['born_by']]+=1
			allopens[mytabs[i]['born_by']]+=1
		else:
			opens[mytabs[i]['born_by']]=1
			allopens[mytabs[i]['born_by']]=1
	for b in opens:
		pidsum += opens[b]
	print "\n <<<<  pid #",pid," ",pidsum,"tabs  >>>> \n"
	spinout(opens,pidsum)
	print "\n all subjects thus far... \n"
	for a in allopens:
		datsum += allopens[a]
	print "running total: ",datsum
	spinout(allopens,datsum)
	return allopens, datsum

def reset():
	## New PID found!
	global mytabs
	mytabs = {}
	global curts
	curts = None
	global lastaction
	lastaction = {'ts': 0,'type':None}
	global opentabs
	opentabs = {}
	global my_windows
	my_windows = {}

def reset_tabopen_listeners():
	global lasttabopen 
	lasttabopen = {'ts': 0}
	global tabdeact
	tabdeact = {'ts': 0}
	global lasttracking
	lasttracking = {'ts': 0}
	global lasttbpgshw
	lasttbpgshw = {'ts': 0}
	global clickthenopen
	clickthenopen = False
	global cmd_click
	cmd_click = False
	global cmdt
	cmdt = False
	global newtabbutton
	newtabbutton = False
	global rightclickmenu
	rightclickmenu = {'ts': 0}
	global lasttabactivate
	lasttabactivate = {'ts': 0}
	global lastclick
	lastclick = {'ts': 0}
	global newwin
	newwin = False
	global tabready
	tabready = {'ts': 0}
	global windowreactivate
	windowreactivate = False
	global click_parent
	click_parent = {'ts': 0}

def store_and_reset_activity(mytabs,myname):
	scroll_and_wheel = mytabs[myname]['actions']['scroll'] + mytabs[myname]['actions']['wheel']
	mouseup_and_click = mytabs[myname]['actions']['mouseup'] + mytabs[myname]['actions']['click']
	mytabs[myname]['activity_periods'][mytabs[myname]['last_start_of_active_per']] = {'clicks': mouseup_and_click,'scroll/wheel':scroll_and_wheel,'tab-pageshow': mytabs[myname]['actions']['tab-pageshow'],'url_bar': mytabs[myname]['actions']['urlbar'],'search_bar':mytabs[myname]['actions']['searchbar']} 
	mytabs[myname]['actions'] = {'tab-pageshow': 0,'scroll':0,'wheel':0,'mouseup':0,'click':0,'urlbar':0,'searchbar':0,'click':0}
	return mytabs

def emptytab(idnum,ts,pid):
	currtab = {}
	currtab['name'] = idnum
	currtab['born_on'] = ts
	currtab['window_id'] = None
	currtab['actions'] = {'tab-pageshow': 0,'scroll':0,'wheel':0,'mouseup':0,'click':0,'urlbar':0,'searchbar':0,'click':0}
	currtab['activity_periods'] = {}
	currtab['inactivity'] = []
	currtab['mother'] = None
	currtab['mother_url'] = None
	currtab['born_by'] = None
	currtab['pid'] = pid
	currtab['index'] = None
	currtab['children'] = []  ## append dicts to children
	currtab['urls_through_time'] = []
	currtab['last_url'] = None
	currtab['death'] = None
	currtab['lifespan'] = None
	currtab['last_action'] = 0
	currtab['last_start_of_active_per'] = 0
	return currtab

def playthedirge(mytabs,data,alias,pid):
	for t in data['tabids']:
		if not t in mytabs:
			mytabs[t] = emptytab(t,data['ts'],pid)
			mytabs[t]['born_by'] = 'I am a ghost! No Birth!'
		mytabs[t]['death'] = ts
		mytabs[t]['lifespan'] = int(ts) - int(mytabs[t]['born_on'])
	return mytabs

def populatetab(mytabs,mother,daughter,data,thismethod):
	mytabs = signbirthcert(mytabs,mother,daughter,thismethod,data)
	mytabs[daughter]['index'] = data.get('index',None)
	mytabs[daughter]['window_id'] = data.get('windowid',None)
	return mytabs

def signbirthcert(mytabs,mother,daughter,thismethod,data):
	mytabs = checkbirth(mytabs,daughter,thismethod)
	if mytabs[daughter]['mother'] == None:
		mytabs[daughter]['mother'] = mother
	if mother != None and mother in mytabs:
		mytabs[mother]['children'].append(daughter)
		mytabs[daughter]['mother_url'] = mytabs[mother]['last_url']
	elif mother != None and mother not in mytabs:
		mytabs[mother] = emptytab(mother,data['ts'],mytabs[daughter]['pid'])
		mytabs = populatetab(mytabs,None,mother,data,'created_pre-ST')
	return mytabs

def checkbirth(mytabs,daughter,thismethod):
	if mytabs[daughter]['born_by'] != None:
		mytabs[daughter]['born_by_orig'] = mytabs[daughter]['born_by']
	mytabs[daughter]['born_by'] = thismethod	
	return mytabs

## tabactivityovetime: If the most recent activity_periods has occured outside of the activity_periods window (last action + activity_periods threshold),
## this marks a period of inactivity retroactively
def tabactivityovetime(mytabs,act,myname,ts):
	if ts > mytabs[myname]['last_action'] + activthresh and mytabs[myname]['last_action'] != 0:
		mytabs[myname]['inactivity'].append(mytabs[myname]['last_action'])
		mytabs = store_and_reset_activity(mytabs,myname)
		mytabs[myname]['activity_periods'][ts] = None
		mytabs[myname]['last_start_of_active_per'] = ts
	mytabs[myname]['last_action'] = ts
	return mytabs

def urlsthroughtime(mytabs,ts,dtmd,myname):
	if not re.search('about:',dtmd['url']):
		try:
			loc = re.search(re.escape('//')+"(.+)"+re.escape('/'),dtmd['url']).group()
		except:
			loc = dtmd['url']
		if mytabs[myname]['last_url'] != loc:
			mytabs[myname]['urls_through_time'].append({'ts': ts,'url': loc })
			mytabs[myname]['last_url'] = loc
	return mytabs

reset_tabopen_listeners()

for line in sys.stdin:
	# tabfirstseen=False
	pid = int(line.split('\t',6)[0])
	ts = int(line.split('\t',6)[1]) 
	dtm = json.loads(line.split('\t')[-1])
	dtmd = dtm['data']
	if pid != curpid:
		for a in mytabs:
			singletab = mytabs[a]
			d = json.dumps(singletab)
			print d
			alltabcount+=1
		reset()
		curpid = pid        
	## timestamp check for hadoop
	if ts < curts:
		raise Exception("Timestamps are not in order!")
	else:
		curts = ts 
	# Add tab to mytabs dict if not already present
	if type(dtmd) is bool:
		continue
	if 'tabid' in dtmd:
		alias = dtmd['tabid']
	if 'url' in dtmd:
		try:
			mytabs = urlsthroughtime(mytabs,ts,dtmd,alias)
		except:
			continue
			# print "url visited before tab exists"
	if 'action' in dtmd:
		if dtmd.get('tabid',None) not in opentabs and 'tabid' in dtmd:
			mytabs[dtmd['tabid']] = emptytab(dtmd['tabid'],ts,pid)
			mytabs = populatetab(mytabs,None,dtmd['tabid'],dtmd,'created_pre-ST')
			prestcount+=1
		if 'tabids' in dtmd:
			for i in dtmd['tabids']:
				if i not in opentabs:
					mytabs[i] = emptytab(i,ts,pid)
					mytabs = populatetab(mytabs,None,i,dtmd,'created_pre-ST')
					prestcount+=1
		### Tab Birth Method listeners ####
		if 'tab-open' == dtmd['action']:# and alias != None:
			opentabs[dtmd['tabid']]=True
			if lasttabopen['ts'] != 0 and clickthenopen is True and (int(ts) - 500) > lasttabopen['ts'] and lasttabactivate['ts']==0 and tabdeact['ts']==0:
				mytabs[lasttabopen['tabid']] = emptytab(lasttabopen['tabid'],ts,pid)
				mytabs = populatetab(mytabs,click_parent['tabid'],lasttabopen['tabid'],dtmd,'cmd_click')
				reset_tabopen_listeners()
			lasttabopen = dtmd
			if 0 == dtmd['index']:
				mytabs[alias] = emptytab(alias,ts,pid)
				mytabs = populatetab(mytabs,None,alias,dtmd,'new_window_open')
				reset_tabopen_listeners()
			if rightclickmenu['ts']!=0:
				mytabs[alias] = emptytab(alias,ts,pid)
				mytabs = populatetab(mytabs,rightclickmenu['tabid'],alias,dtmd,'context-openlinkintab')
				reset_tabopen_listeners()
			if newtabbutton is True:
				mytabs[alias] = emptytab(alias,ts,pid)
				mytabs = populatetab(mytabs,xulmom,alias,dtmd,'new_tab_button')
				reset_tabopen_listeners()
			if cmdt is True:
				mytabs[alias] = emptytab(alias,ts,pid)
				mytabs = populatetab(mytabs,cmdtmom,alias,dtmd,'command_+_T')
				reset_tabopen_listeners()
			# if windowreactivate == True:
			# 	mytabs[alias] = emptytab(alias,ts,pid)
			# 	mytabs = mytabs = populatetab(mytabs,None,alias,dtmd,'window_reactivate')
			# 	reset_tabopen_listeners()
			# if lasttbpgshw['ts']!=0 and lastclick['ts']!=0:
			# 	mytabs[lasttabopen['tabid']] = emptytab(lasttabopen['tabid'],ts,pid)
			# 	mytabs = populatetab(mytabs,lastclick.get('tabid',None),lasttabopen['tabid'],dtmd,'cmd_click')
			# 	reset_tabopen_listeners()
			if lastclick['ts']!=0 and (lastclick['ts'] - lasttabopen['ts']) < 200:
				clickthenopen = True
				click_parent = lastclick
		if 'tab-ready' == dtmd['action'] and lasttracking['ts']!=0:
			mytabs[alias] = emptytab(alias,ts,pid)
			mytabs = populatetab(mytabs,None,alias,dtmd,'new_window_open')
			reset_tabopen_listeners()
		if (lasttabopen['ts']!= 0 and (ts > lasttabopen['ts']+1000) and clickthenopen == True and tabdeact['ts']==0) or ('tab-ready' == dtmd['action'] and clickthenopen == True):
			mytabs[lasttabopen['tabid']] = emptytab(lasttabopen['tabid'],ts,pid)
			mytabs = populatetab(mytabs,click_parent.get('tabid',None),lasttabopen['tabid'],dtmd,'cmd_click')
			reset_tabopen_listeners()
		if 'tab-pageshow' == dtmd['action']:
			lasttbpgshw = dtmd
		elif 'open' == dtmd['action']:
			newwin = True
		elif 'tracking' == dtmd['action']:
			lasttracking = dtmd
		elif 'context-openlinkintab' == dtmd['action']:
			rightclickmenu = dtmd
		elif 'mouseup' == dtmd['action']:
			lastclick = dtmd
		elif 'tab-deactivate' == dtmd['action']:
			tabdeact = dtmd
			mytabs[dtmd['tabid']]['inactivity'].append(ts)
			mytabs = store_and_reset_activity(mytabs,dtmd['tabid'])
		elif 'deactivate' == dtmd['action']:
			for i in dtmd['tabids']:
				mytabs[i]['inactivity'].append(ts)
				mytabs = store_and_reset_activity(mytabs,i)
			reset_tabopen_listeners()
		elif 'tab-activate' == dtmd['action']:
			lasttabactivate = dtmd
			if lasttabopen['ts']!=0:
				# if clickthenopen == True and ((dtmd['ts']-lasttabopen['ts']) < 200 or tabdeact['ts']!=0): #and ((tabdeact['ts']-dtmd['ts'] < 500 and tabdeact['ts'] != 0):
				# 	mytabs[lasttabopen['tabid']] = emptytab(lasttabopen['tabid'],ts,pid)
				# 	mytabs = populatetab(mytabs,lastclick['tabid'],lasttabopen['tabid'],dtmd,'left_mouse-click')
				# 	reset_tabopen_listeners()
				# if tabdeact.get('tabid',None)==lasttbpgshw.get('tabid',None) and 'tabid' in lasttbpgshw:
				# 	mytabs[lasttabopen['tabid']] = emptytab(lasttabopen['tabid'],ts,pid)
				# 	mytabs = populatetab(mytabs,tabdeact['tabid'],lasttabopen['tabid'],dtmd,'double-click_in_chrome')
				# 	reset_tabopen_listeners()
				if tabdeact['ts']!=0 and clickthenopen == True:
					mytabs[lasttabopen['tabid']] = emptytab(lasttabopen['tabid'],ts,pid)
					mytabs = populatetab(mytabs,tabdeact['tabid'],lasttabopen['tabid'],dtmd,'left_mouse-click')
					reset_tabopen_listeners()
				elif windowreactivate == True and tabdeact['ts']!=0:
					mytabs[lasttabopen['tabid']] = emptytab(lasttabopen['tabid'],ts,pid)
					mytabs = populatetab(mytabs,tabdeact['windowid'],lasttabopen['tabid'],dtmd,'tab_moved_btwn_windows')
					reset_tabopen_listeners()
				else:
					mytabs[lasttabopen['tabid']] = emptytab(lasttabopen['tabid'],ts,pid)
					mytabs = populatetab(mytabs,None,lasttabopen['tabid'],dtmd,'unknown_tab-open_event')
					unknowneventopen+=1
					reset_tabopen_listeners()
			mytabs[alias]['activity_periods'][ts] = None
			mytabs[alias]['last_start_of_active_per'] = ts
		elif 'cmd_newNavigatorTab' == dtmd['action']:
			if 'commands:xul:toolbarbutton' == dtmd['group']:
				newtabbutton = True
				try:
					xulmom = dtmd['tabid']
				except:
					xulmom = None
			elif 'commands:key' == dtmd['group']:
				cmdt = True
				try:
					cmdtmom = dtmd['tabid']
				except:
					cmdtmom = None
		elif 'activate' == dtmd['action']:
			windowreactivate = True
			for i in dtmd['tabids']:
				mytabs[i]['activity_periods'][ts] = None
				mytabs[i]['last_start_of_active_per'] = ts
		### Tab Death Listeners ###
		elif 'tab-close' == dtmd['action']:
			mytabs[alias]['death'] = ts
			mytabs[alias]['lifespan'] = int(ts) - int(mytabs[alias]['born_on'])
			mytabs[alias]['last_act_to_death_latency'] = int(ts) - int(mytabs[alias]['last_action'])
			mytabs = store_and_reset_activity(mytabs,alias)
		elif 'close' == dtmd['action']:
			playthedirge(mytabs,dtmd,alias,pid)
			for t in dtmd['tabids']:
				mytabs[t]['death'] = ts
				mytabs[t]['lifespan'] = int(ts) - int(mytabs[t]['born_on'])
				mytabs[t]['last_act_to_death_latency'] = int(ts) - int(mytabs[t]['last_action'])
				mytabs = store_and_reset_activity(mytabs,t)
		### Tab Activity listeners ###
		act = dtmd.get('action',None)
		if act in actionlist and 'tabid' in dtmd:
			if alias not in mytabs:
				mytabs[alias] = emptytab(alias,ts,pid)
				mytabs[alias]['born_by'] = "action_preceded_birth"
			mytabs[alias]['actions'][dtmd['action']] += 1
			mytabs = tabactivityovetime(mytabs,act,alias,ts)
	if 'group' in dtmd:
		if dtmd['group'] in actionlist and 'tabid' in dtmd:
			if alias not in mytabs:
				mytabs[alias] = emptytab(alias,ts,pid)
				mytabs[alias]['born_by'] = "action_preceded_birth"
			mytabs[alias]['actions'][dtmd['group']] += 1
			mytabs = tabactivityovetime(mytabs,dtmd['group'],alias,ts)
for a in mytabs:
	singletab = mytabs[a]
	d = json.dumps(singletab)
	print d
	# alltabcount+=1

# print "alltabs=",alltabcount
# print "pre-ST tabs=",prestcount
# print "unknown tabs with open event=",unknowneventopen