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
activthresh = 1000000
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
datsum = 0
# recents = deque([],15)
mytabs = {}
curpid = None
curts = None
actionlist = ['tab-pageshow','scroll','wheel','mouseup','click','urlbar','searchbar','drag']
allopens = {}

def opentypesums(mytabs,pid,datsum,allopens):
	def spinout(opn,sumz):
		for aa in opn:
			print aa," accounts for ",round((opn[aa]/float(sumz))*100)," percent of opens"

	opens={}
	pidsum = 0
	for i in mytabs:
		if mytabs[i]['born by'] in opens:
			opens[mytabs[i]['born by']]+=1
			allopens[mytabs[i]['born by']]+=1
		else:
			opens[mytabs[i]['born by']]=1
			allopens[mytabs[i]['born by']]=1
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

def emptytab(idnum,ts,pid):
	currtab = {}
	currtab['name'] = idnum
	currtab['born on'] = ts
	currtab['window id'] = None
	currtab['actions'] = {'tab-pageshow': 0,'scroll':0,'wheel':0,'mouseup':0,'urlbar':0,'searchbar':0,'click':0,'tabbar':0}
	currtab['activity'] = []
	currtab['inactivity'] = []
	currtab['mother'] = None
	currtab['born by'] = None
	currtab['pid'] = pid
	currtab['index'] = None
	currtab['children'] = []  ## append dicts to children
	currtab['urls through time'] = []
	currtab['last url'] = None
	currtab['death'] = None
	currtab['lifespan'] = None
	currtab['last action'] = 0
	return currtab

def playthedurge(mytabs,data,alias):
	for t in data['tabids']:
		if not t in mytabs:
			mytabs[t] = emptytab(t,data['ts'],alias)
			mytabs[t]['born by'] = 'I am a ghost! No Birth!'
		mytabs[t]['death'] = ts
		mytabs[alias]['lifespan'] = int(ts) - int(mytabs[t]['born on'])
	return mytabs

def populatetab(mytabs,mother,daughter,data,thismethod):
	mytabs = signbirthcert(mytabs,mother,daughter,thismethod)
	mytabs[alias]['index'] = data.get('index',None)
	mytabs[alias]['window id'] = data.get('windowid',None)
	return mytabs

def signbirthcert(mytabs,mother,daughter,thismethod):
	mytabs = checkbirth(mytabs,daughter,thismethod)
	if mytabs[daughter]['mother'] == None:
		mytabs[daughter]['mother'] = mother
	if mother != None:
		mytabs[mother]['children'].append(daughter)	
	return mytabs

def checkbirth(mytabs,daughter,thismethod):
	if mytabs[daughter]['born by'] != None:
		old = mytabs[daughter]['born by']
		# mytabs[daughter]['born by'] = [mytabs[daughter]['born by'],thismethod]
		# print "birth wackness: ",daughter," was ",old," and is now ",thismethod
	
	mytabs[daughter]['born by'] = thismethod
	return mytabs

# def propagate1(mytabs,mother,daughter):
# 	if mytabs[daughter]['mother'] == '':
# 		mytabs[daughter]['mother'] = mother
# 	mytabs[mother]['children'].append({'name': daughter, 'children': mytabs[daughter]['children']})	
# 	mytabs = propagate2(mytabs,mytabs[mother]['mother'],mytabs[mother]['name'])
# 	return mytabs
# 	print "propagated1"

# def propagate2(mytabs,mother,daughter):
# 	if len(mytabs[mother]['children']) == 0:
# 		print "  ***  error in propagate2  ***  "
# 	elif len(mytabs[mother]['children']) != 0:
# 		for i in mytabs[mother]['children']:
# 			if daughter == i['name']:
# 				i['children'] = mytabs[daughter]['children']
# 	if mytabs[mother]['mother'] != '': #and mytabs[mother]['name'] != mytabs[mother]['mother']:
# 		mytabs = propagate2(mytabs,mytabs[mother]['mother'],mytabs[mother]['name'])
# 	return mytabs
# 	print "propagated2"

## tabactivityovetime: If the most recent activity has occured outside of the activity window (last action + activity threshold),
## this marks a period of inactivity retroactively
def tabactivityovetime(mytabs,act,alias,ts):
	if ts > mytabs[alias]['last action'] + activthresh:
		if mytabs[alias]['last action'] != 0:
			mytabs[alias]['inactivity'].append(mytabs[alias]['last action'])
		mytabs[alias]['activity'].append(ts)
	mytabs[alias]['last action'] = ts

	return mytabs

def urlsthroughtime(mytabs,ts,dtmd,alias):
	if not re.search('about:',dtmd['url']):
		try:
			loc = re.search(re.escape('//')+"(.+)"+re.escape('/'),dtmd['url']).group()
		except:
			loc = dtmd['url']
		if mytabs[alias]['last url'] != loc:
		# if mytabs[alias]['last url'] != dtmd['url']:
				mytabs[alias]['urls through time'].append({'ts': ts,'url': loc })
				mytabs[alias]['last url'] = loc
	return mytabs

reset_tabopen_listeners()

for line in sys.stdin:
	pid = int(line.split('\t',6)[0])
	ts = int(line.split('\t',6)[1])	###CHANGE!
	dtm = json.loads(line.split('\t')[-1])
	dtmd = dtm['data']
	if pid != curpid:
		# fh = open("tabs_for_pid_"+ str(curpid) + ".json","w")
		# fh.write(json.dumps(mytabs))
		# fh.close()
		# print "\n **** \n pid #" + str(curpid) + " used " + str(len(mytabs)) + " tabs"
		# print sums of different open (birth) types
		# allopens,datsum = opentypesums(mytabs,curpid,datsum,allopens)
		## reset variables
		# print '%s\t%s' % (curpid, mytabs)
		reset()
		curpid = pid		
	## timestamp check for hadoop
	if ts < curts:
		raise Exception("Timestamps are not in order!")
	else:
		curts = ts
		# print "\n   ---------- new PID ------------ "		

	# Add tab to mytabs dict if not already present
	if type(dtmd) is bool:
		continue
	if 'tabid' in dtmd:
		alias = dtmd['tabid']
		if not alias in mytabs:
			mytabs[alias] = emptytab(alias,ts,pid)
			# print "added new tab"
		if 'url' in dtmd:
			mytabs = urlsthroughtime(mytabs,ts,dtmd,alias)
	if 'action' in dtmd:
		### Tab Birth Method listeners ####
		if 'tab-open' == dtmd['action']:
			lasttabopen = dtmd
			if lasttracking['ts']!=0 and (lasttracking['ts'] - lasttabopen['ts']) < 100:
				mytabs[alias]['born by'] = 'new window open'
				mytabs[alias]['index'] = dtmd.get('index',None)
				mytabs[alias]['window id'] = dtmd.get('windowid',None)
				reset_tabopen_listeners()
			elif rightclickmenu['ts']!=0 and (rightclickmenu['ts'] - lasttabopen['ts']) < 100:
				# mytabs[alias]['born by'] = 'context-openlinkintab'
				mytabs = populatetab(mytabs,rightclickmenu['tabid'],alias,dtmd,'context-openlinkintab')
				reset_tabopen_listeners()
			elif newtabbutton is True:
				# mytabs[alias]['born by'] = 'new tab button'
				mytabs = populatetab(mytabs,xulmom,alias,dtmd,'new tab button')
				reset_tabopen_listeners()
			elif cmdt is True:
				# mytabs[alias]['born by'] = 'command + T'
				mytabs = populatetab(mytabs,cmdtmom,alias,dtmd,'command + T')
				reset_tabopen_listeners()
			if lastclick['ts']!=0 and (lastclick['ts'] - lasttabopen['ts']) < 100:
				clickthenopen = True

		##COMMENTED FOR DEBUGGING
		elif 'tab-pageshow' == dtmd['action']:
			lasttbpgshw = dtmd
			# if clickthenopen == 1:
			# 	cmd_click = 1
			# 	mytabs[lasttabopen['tabid']]['born by'] = 'cmd + click'
			# 	mytabs = signbirthcert(mytabs,lasttabopen['tabid'],alias)
			# 	reset_tabopen_listeners()
		elif clickthenopen is True and (int(ts) + 500) > lasttabopen['ts'] and lasttabactivate['ts']==0 and tabdeact['ts']==0 and lasttbpgshw['ts']!=0 and lasttabopen['ts']!=0:
			if lasttabopen['tabid'] == alias:
				pass
				# print "duplicated ", alias
			else:
				# mytabs[lasttabopen['tabid']]['born by'] = 'cmd + click'
				mytabs = populatetab(mytabs,lasttabopen['tabid'],alias,dtmd,'cmd + click')
				reset_tabopen_listeners()
		elif 'tracking' == dtmd['action']:
			lasttracking = dtmd
		elif 'context-openlinkintab' == dtmd['action'] and 'tabid' in dtmd:
			rightclickmenu = dtmd
		elif 'mouseup' == dtmd['action']:
			lastclick = dtmd
		elif 'tab-deactivate' == dtmd['action']:
			tabdeact = dtmd
			mytabs[alias]['inactivity'].append(ts)
		elif 'tab-activate' == dtmd['action']:
			lasttabactivate = dtmd
			mytabs[alias]['activity'].append(ts)
			if abs(dtmd['ts'] - tabdeact['ts']) < 100 and clickthenopen == 1 and tabdeact['ts'] != 0:
				# mytabs[alias]['born by'] = 'left mouse-click'
				mytabs = populatetab(mytabs,tabdeact['tabid'],alias,dtmd,'left mouse-click')
				reset_tabopen_listeners()
		elif 'cmd_newNavigatorTab' == dtmd['action']:
			if 'commands:xul:toolbarbutton' == dtmd['group']:
				newtabbutton = True
				try:
					xulmom = dtmd['tabid']
				except:
					xulmom = None
				# print "xul:toolbarbutton open"
			elif 'commands:key' == dtmd['group']:
				cmdt = True
				try:
					cmdtmom = dtmd['tabid']
				except:
					cmdtmom = None
				# print "cmd + T open"
		### Tab Death Listeners ###
		elif 'tab-close' == dtmd['action']:
			mytabs[alias]['death'] = ts
			mytabs[alias]['lifespan'] = int(ts) - int(mytabs[alias]['born on'])
		elif 'close' == dtmd['action']:
			playthedurge(mytabs,dtmd,alias)
			for t in dtmd['tabids']:
				mytabs[t]['death'] = ts
				mytabs[alias]['lifespan'] = int(ts) - int(mytabs[t]['born on'])
		### Tab Activity listeners ###
		act = dtmd.get('action',None)
		if act in actionlist and 'tabid' in dtmd:
			# if alias != dtmd['tabid']:
				# print "     >>>  ^ IMPOSTER! ^ <<<\n",alias," (alias) is not ",dtmd['tabid']," (tab-id)"
			mytabs[alias]['actions'][dtmd['action']] += 1
			mytabs = tabactivityovetime(mytabs,act,alias,ts)
		# elif act in actionlist and not 'tabid' in dtmd:
			# print " * faceless action * "

# print "Birth Stats for snappy:"
# allopens = opentypesums(mytabs,curpid,datsum,allopens)
# fh = open("tabs_for_pid_"+ str(curpid) + ".json","w")
# fh.write(json.dumps(mytabs))
# fh.close()
# print "pid #" + str(curpid) + " used " + str(len(mytabs)) + " tabs"
print '%s\t%s' % (curpid, mytabs)
