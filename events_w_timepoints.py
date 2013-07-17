import json
import re
from collections import deque

lines=open("random10.search.events").readlines()
personIDs = json.load(open("personid_lines.json","r"))
#times = range(1370530200000,1371156735800,6000000)
all_events = ['time stamp','action','pp']

NumParticipants = 10
for pp in range(1,NumParticipants+1):
	this_start = int(personIDs[pp-1][1])
	if pp < 10:
		this_end = int(personIDs[pp][1])
	elif pp == 10:
		this_end = 5779243
	print "searching ppt " + str(pp) + " within lines " + str(this_start) + " to " + str(this_end)
	for ee in range(this_start+5,this_end-5):
		deck = deque(lines[ee-10:ee+5])
		tsm = re.search(r'"ts":',lines[ee])		
		if tsm:
			this_ts = int(re.findall(r'\d+',lines[ee])[0])
			for q in list(deck):
				mouseup = re.search(r'"mouseup"',q)
				scroll = re.search(r'scroll|wheel',q)
				setcookie = re.search(r'"set-cookie"',q)
				t_bar = re.search(r'"tab-bar"',q)
				srchbar = re.search(r'searchbar',q)
				url = re.search(r'urlbar',q)
				if mouseup:
					all_events.append([this_ts,'mouseup',pp])
					print "mouseup"
				elif scroll:
					all_events.append([this_ts,'scroll',pp])
					print "scroll"
				elif setcookie:
					all_events.append([this_ts,'set-cookie',pp])
					print "cookie set"
				elif t_bar:
					all_events.append([this_ts,'tab-bar',pp])
					print "tab bar"
				elif srchbar:
					all_events.append([this_ts,'searchbar',pp])
					print "search bar"
				elif url:
					all_events.append([this_ts,'urlbar',pp])
					print "url bar"
	fh = open("allevents_ppt_" + str(pp) + ".json","w")
	fh.write(json.dumps(all_events))
	fh.close()
