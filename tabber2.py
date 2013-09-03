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
lasttracking = False
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
	lasttracking = False
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
	global birth
	birth = False
	global likely_cmd_clk_birth
	likely_cmd_clk_birth={}

## Move current tab activities count to reside under timestamp of activity-period start 
def store_and_reset_activity(mytabs,myname,time,deact_cause):
	scroll_and_wheel = mytabs[myname]['actions']['scroll'] + mytabs[myname]['actions']['wheel']
	mouseup_and_click = mytabs[myname]['actions']['mouseup'] + mytabs[myname]['actions']['click']
	mytabs[myname]['activity_periods'][mytabs[myname]['last_start_of_active_per']] = {'reason_for_activity_stop':deact_cause,'length': time-mytabs[myname]['last_start_of_active_per'],'clicks': mouseup_and_click,'scroll/wheel':scroll_and_wheel,'tab-pageshow': mytabs[myname]['actions']['tab-pageshow'],'url_bar': mytabs[myname]['actions']['urlbar'],'search_bar':mytabs[myname]['actions']['searchbar']} 
	mytabs[myname]['actions'] = {'tab-pageshow': 0,'scroll':0,'wheel':0,'mouseup':0,'click':0,'urlbar':0,'searchbar':0,'click':0}
	return mytabs

def emptytab(mytabs,idnum,ts,pid):
	if idnum in mytabs:
		currtab = mytabs[idnum]
		# print "duplicate:",idnum
	else:
		currtab = {}
		currtab['name'] = idnum
		currtab['born_on'] = ts
		currtab['window_id'] = None
		currtab['actions'] = {'tab-pageshow': 0,'scroll':0,'wheel':0,'mouseup':0,'click':0,'urlbar':0,'searchbar':0,'click':0}
		currtab['activity_periods'] = {}
		currtab['inactivity'] = []
		currtab['parent'] = None
		currtab['parent_url'] = None
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

## Populate termination/death fields for tab
def playthedirge(mytabs,data,alias,pid):
	for t in data['tabids']:
		if not t in mytabs:
			mytabs[t] = emptytab(mytabs,t,data['ts'],pid)
			mytabs[t]['born_by'] = 'I am a ghost! No Birth!'
		mytabs[t]['death'] = ts
		mytabs[t]['cause_of_death'] = 'window closed'
		mytabs[t]['last_act_to_death_latency'] = int(ts) - int(mytabs[t]['last_action'])
		mytabs[t]['lifespan'] = int(ts) - int(mytabs[t]['born_on'])
		mytabs = store_and_reset_activity(mytabs,t,ts,'window closed')
	return mytabs

## Populate child and parent fields with tab-birth data
def populatetab(mytabs,parent,child,data,thismethod):
	mytabs = signbirthcert(mytabs,parent,child,thismethod,data)
	mytabs[child]['index'] = data.get('index',None)
	mytabs[child]['window_id'] = data.get('windowid',None)
	return mytabs

## Fill in current tab's (child's) parent, add child to parent's children field, grab parent's url at creation-time; 
## Also, if parent has spawned child without itself being recorded, this parent was created before tracking
def signbirthcert(mytabs,parent,child,thismethod,data):
	mytabs = checkbirth(mytabs,child,thismethod)
	if mytabs[child]['parent'] == None:
		mytabs[child]['parent'] = parent
	if parent != None and parent in mytabs:
		mytabs[parent]['children'].append(child)
		mytabs[child]['parent_url'] = mytabs[parent]['last_url']
	elif parent != None and parent not in mytabs:
		mytabs[parent] = emptytab(mytabs,parent,data['ts'],mytabs[child]['pid'])
		mytabs = populatetab(mytabs,None,parent,data,'created_pre-ST')
	return mytabs

def checkbirth(mytabs,child,thismethod):
	if mytabs[child]['born_by'] != None:
		if 'born_by_orig' not in mytabs[child]:
			mytabs[child]['born_by_orig'] = []
		mytabs[child]['born_by_orig'].append(mytabs[child]['born_by'])
		mytabs[child]['born_by_orig']=list(set(mytabs[child]['born_by_orig']))
	mytabs[child]['born_by'] = thismethod	
	return mytabs

## tabactivityovetime: If the most recent activity_periods has occured outside of the activity_periods window (last action + activity_periods threshold),
## this marks a period of inactivity retroactively
def tabactivityovetime(mytabs,act,myname,ts):
	if ts > mytabs[myname]['last_action'] + activthresh and mytabs[myname]['last_action'] != 0:
		mytabs[myname]['inactivity'].append(mytabs[myname]['last_action'])
		mytabs = store_and_reset_activity(mytabs,myname,ts,'user inactive too long')
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
	eventid = int(line.split('\t',6)[2])
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
	## Skip line if data field is BOOLEAN
	if isinstance(dtmd,bool) or isinstance(dtmd,str):
		continue
	alias = dtmd.get('tabid',None)
	## Handle url -- adding to list of all visited, if new
	if 'url' in dtmd:
		try:
			mytabs = urlsthroughtime(mytabs,ts,dtmd,alias)
		except:
			continue
			# print "url visited before tab exists"
	if 'action' in dtmd:
		## Handle actions that precede tab-open events; 'opentabs' keeps a tally of tabs with "tab-open" events
		if alias is not None and alias not in opentabs:
			## Handle session restore
			if 'about:sessionrestore' == dtmd.get('url',None) or 'about:sessionrestore' ==  dtmd.get('location',None):
				mytabs[alias] = emptytab(mytabs,alias,ts,pid)
				mytabs = populatetab(mytabs,None,alias,dtmd,'session restore')
			else:
				mytabs[alias] = emptytab(mytabs,alias,ts,pid)
				mytabs = populatetab(mytabs,None,alias,dtmd,'created_pre-ST')
				prestcount+=1
		# (this probably should never happens)
		if 'tabids' in dtmd:
			for i in dtmd['tabids']:
				if i not in opentabs:
					mytabs[i] = emptytab(mytabs,i,ts,pid)
					mytabs = populatetab(mytabs,None,i,dtmd,'created_pre-ST')
					prestcount+=1
		### Tab Birth Method listeners ####
		## Handle tab-open events depending on select prior activities that are sufficient to ascribe tab-birth-method
		if 'tab-open' == dtmd['action']:# and alias != None:
			opentabs[dtmd['tabid']]=True
			## Handle a second (new) "tab-open" action while previous "tab-open" event is still unresolved; no "tab-activation" or "tab-deactivation" == command+click
			if lasttabopen['ts'] != 0 and clickthenopen is True and lasttabactivate['ts']==0 and tabdeact['ts']==0:
				mytabs[lasttabopen['tabid']] = emptytab(mytabs,lasttabopen['tabid'],ts,pid)
				mytabs = populatetab(mytabs,click_parent['tabid'],lasttabopen['tabid'],dtmd,'cmd_click')
				birth = True
				# reset_tabopen_listeners()
			lasttabopen = dtmd
		## Handle first tab opened in window
			if 0 == dtmd['index'] or lasttracking==True:
				mytabs[alias] = emptytab(mytabs,alias,ts,pid)
				mytabs = populatetab(mytabs,None,alias,dtmd,'new_window_open')
				birth = True

		## Handle if there has been a right-click-menu activation (e.g. 'context-openlinkintab')
			if rightclickmenu['ts']!=0:
				mytabs[alias] = emptytab(mytabs,alias,ts,pid)
				mytabs = populatetab(mytabs,rightclickmenu.get('tabid',None),alias,dtmd,'context-openlinkintab')
				birth = True

		## Handle if there was a new-tab-button activation (e.g. 'commands:xul:toolbarbutton')
			if newtabbutton is True:
				mytabs[alias] = emptytab(mytabs,alias,ts,pid)
				mytabs = populatetab(mytabs,xulmom,alias,dtmd,'new_tab_button')
				birth = True

		## Handle if there was a command+"T" activation (e.g. 'commands:key')
			if cmdt is True:
				mytabs[alias] = emptytab(mytabs,alias,ts,pid)
				mytabs = populatetab(mytabs,cmdtmom,alias,dtmd,'command_+_T')
				birth = True
		## Handle a "tab-open" after mouseup
			if 0 < lastclick['ts'] < (ts +200):
				clickthenopen = True
				click_parent = lastclick

		## Handle command+click activities
		if clickthenopen == True and 'tab-pageshow' == dtmd['action'] and click_parent.get('tabid',None) == dtmd.get('tabid',None) and tabdeact['ts']==0 and 'tabid' in dtmd:
			likely_cmd_clk_birth = {'event_id':eventid,'putative_parent':click_parent['tabid'],'putative_child':dtmd['tabid'],'ts':ts,'pid':pid,'data':dtmd}
		## Handle weird chronology of events that could falsely code a left-click on _blank link as a command+click
		if likely_cmd_clk_birth.get('event_id') == (eventid - 1) and 'tab-deactivate' != dtmd['action']:
			mytabs[lasttabopen['tabid']] = emptytab(mytabs,lasttabopen['tabid'],ts,pid)
			mytabs = populatetab(mytabs,click_parent['tabid'],lasttabopen['tabid'],dtmd,'cmd_click')
			birth = True
	## Handle pre-"tab-open" events; record data (dtmd) or action evidence (BOOL)
		if 'tab-pageshow' == dtmd['action']:
			lasttbpgshw = dtmd
		elif 'open' == dtmd['action']:
			newwin = True
		elif 'tracking' == dtmd['action']:
			lasttracking = True
		elif 'context-openlinkintab' == dtmd['action']:
			rightclickmenu = dtmd
		elif dtmd['action'] in ['mouseup','click']:
			lastclick = dtmd
		elif 'tab-deactivate' == dtmd['action']:
			tabdeact = dtmd
			mytabs[dtmd['tabid']]['inactivity'].append(ts)
			mytabs = store_and_reset_activity(mytabs,dtmd['tabid'],ts,'tab deactivated')
	## Handle case: "tab-deactivate" is first activity of tab
		elif 'deactivate' == dtmd['action']:
			for i in dtmd['tabids']:
				mytabs[i]['inactivity'].append(ts)
				mytabs = store_and_reset_activity(mytabs,i,ts,'window deactivated')
	## Handle tab-activation (singular, un-backgrounding event)
		elif 'tab-activate' == dtmd['action']:
			lasttabactivate = dtmd
			if lasttabopen['ts']!=0:
				if tabdeact['ts']!=0 and clickthenopen == True:
					mytabs[lasttabopen['tabid']] = emptytab(mytabs,lasttabopen['tabid'],ts,pid)
					mytabs = populatetab(mytabs,tabdeact['tabid'],lasttabopen['tabid'],dtmd,'left_mouse-click')
					birth = True
			## Handle case: tab is moved between windows  <<< TO ADD: where did tab originate?
				elif windowreactivate == True and tabdeact['ts']!=0:
					mytabs[lasttabopen['tabid']] = emptytab(mytabs,lasttabopen['tabid'],ts,pid)
					mytabs = populatetab(mytabs,tabdeact['windowid'],lasttabopen['tabid'],dtmd,'tab_moved_btwn_windows')
					birth = True
			## Handle case: there are "tab-open" and "tab-activate" events for this tab but it cannot be categorized
				else:
					mytabs[lasttabopen['tabid']] = emptytab(mytabs,lasttabopen['tabid'],ts,pid)
					mytabs = populatetab(mytabs,None,lasttabopen['tabid'],dtmd,'unknown_tab-open_event')
					unknowneventopen+=1
					birth = True
			mytabs[alias]['activity_periods'][ts] = None
			mytabs[alias]['last_start_of_active_per'] = ts
	## Handle cmd_newNavigatorTab triggered, which can either happen via command+"T" button push, or clicking the new tab button
		elif 'cmd_newNavigatorTab' == dtmd['action']:
			if 'commands:key' == dtmd['group']:
				cmdt = True
				cmdtmom = dtmd.get('tabid',None)
			else:
				newtabbutton = True
				xulmom = dtmd.get('tabid',None)
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
			mytabs = store_and_reset_activity(mytabs,alias,ts,'tab closed')
		## Handle window closure (possibly multiple tabs)
		elif 'close' == dtmd['action']:
			playthedirge(mytabs,dtmd,alias,pid)
			for t in dtmd['tabids']:
				mytabs = store_and_reset_activity(mytabs,t,ts,'window closed')
		### Tab Activity listeners ###
		## Handle tab activities un-related to tab-open events
		act = dtmd.get('action',None)
		if act in actionlist and 'tabid' in dtmd:
			if alias not in mytabs:
				mytabs[alias] = emptytab(mytabs,alias,ts,pid)
				mytabs[alias]['born_by'] = "action_preceded_birth"
			mytabs[alias]['actions'][dtmd['action']] += 1
			mytabs = tabactivityovetime(mytabs,act,alias,ts)
	if 'group' in dtmd:
		if dtmd['group'] in actionlist and 'tabid' in dtmd:
			if alias not in mytabs:
				mytabs[alias] = emptytab(mytabs,alias,ts,pid)
				mytabs[alias]['born_by'] = "action_preceded_birth"
			mytabs[alias]['actions'][dtmd['group']] += 1
			mytabs = tabactivityovetime(mytabs,dtmd['group'],alias,ts)
	if birth == True:
		reset_tabopen_listeners()
for a in mytabs:
	singletab = mytabs[a]
	d = json.dumps(singletab)
	print d
	# alltabcount+=1

# print "alltabs=",alltabcount
# print "pre-ST tabs=",prestcount
# print "unknown tabs with open event=",unknowneventopen