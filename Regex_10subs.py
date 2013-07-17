"""
Notes from Gregg and Ilana: (7/2/13)
maybe we should use "window-deactivate" and "-activate" events to track consecutive activity
deactivate should end a session unless there is another activate within a second (or something reasonable)
Other interesting events:
add-on main (first one is weird); add-on main ("reason": start-up)
-- look at last five events before add-on close (=closing the browser/no more windows)

Heat Map of usage; log10 of the events around it/normalize it by the most intense usage
"""


import re
import json

Deactivate_events = []
Reactivation_thresh = 1500
personids=[]
personid_lines=[]
rndev=open("random10.search.events",'r')
lines = rndev.readlines()

for fp in range(len(lines)):
	personid = re.search(r'personid',lines[fp],re.I)
	if personid:
		personids.append([lines[fp],str(fp)])
		personid_lines.append(str(fp))

#personid_lines = json.load(open("personid_lines.json","r"))

for person in range(1,len(personid_lines)+1):
	DeAct_count = 0
	tab_pageshow_events=[]
#	for ln in range(int(personid_lines[person-1]),int(personid_lines[person])):
	for ln in range(int(personid_lines[person-1]),len(lines)):
#		tempDeAct_event = []
		tempDeAct_event2 = []
#		tempDeAct_event_sanitycheck = []
#		DeAct_ts = []
#		ReAct_ts = []
		searchmatch = re.search(r'"action": "deactivate"|"close"',lines[ln],re.I)
		if searchmatch:
			for find_ts in range(ln,ln+5):
				suspect = re.search(r'"ts":',lines[find_ts])
				if suspect:
					DeAct_ts = int(re.findall(r'\d+',lines[find_ts])[0])
#					tempDeAct_event.extend([str(DeAct_ts),person])
#					tempDeAct_event_sanitycheck.append([lines[ln-3:ln],DeAct_ts])
					DeAct_true_bound = DeAct_ts + Reactivation_thresh
#					DeAct_count = DeAct_count + 1	
					print DeAct_ts
					print "deactivation time logged"
					Deactivate_events.append([str(DeAct_ts),person])
					for newln in range(ln,ln+100):
						substr = re.search(r'"action": "activate"',lines[newln],re.I)
						if substr:
							ReAct_suspect = re.search(r'"ts":+',lines[newln],re.I)
							if ReAct_suspect:
								ReAct_ts = int(re.findall(r'\d+',lines[newln])[0])
								if ReAct_ts < DeAct_true_bound:
									tempDeAct_event2.append("Window Re-activation at " + str(ReAct_ts))
#								if ReAct_ts >= DeAct_true_bound:
#									tempDeAct_event2.append("Window Activation within " + str(Reactivation_thresh) + "microseconds")
									if tempDeAct_event2:
										print "reactivation event logged"
										Deactivate_events.append(tempDeAct_event2)
#										print tempDeAct_event_sanitycheck	
	out = open("PPT_" + str(person) + "_deactivate_events.json",'w')
	out.write(json.dumps(Deactivate_events))
	out.close()
	print "PPT_" + str(person) + " deactivate_events.json written"
outpers = open("personid_lines.json",'w')
outpers.write(json.dumps(personids))
outpers.close()
rndev.close()