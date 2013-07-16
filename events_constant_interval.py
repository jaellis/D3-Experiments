import json
import re
from collections import deque

lines=open("random10.search.events").readlines()
personIDs = json.load(open("personid_lines.json","r"))
times = range(1370530200000,1371156735800,6000000)

NumParticipants = 10
for pp in range(1,NumParticipants+1):
	actions = ['clicks','scrolls','set-cookies','tab-bar','searchbar','urlbar','timestamp','participant num']
	events = [[0]*len(actions)]
	for i in range(len(times)):
		events.extend([[0]*len(actions)])

	for c in range(len(events)):
		events[c][-1] = pp

	this_start = int(personIDs[pp-1][1])
	if pp < 10:
		this_end = int(personIDs[pp][1])
	elif pp == 10:
		this_end = 5779243
	for ee in range(this_start+5,this_end-5):
		deck = deque(lines[ee-10:ee+5])
		tsm = re.search(r'"ts":',lines[ee])		
		if tsm:
			mouseup = 0
			scrls = 0
			cookie = 0
			tab_bar = 0
			searchbar = 0
			urlbar = 0
			# bin into the right part of your time range
			this_ts = int(re.findall(r'\d+',lines[ee])[0])
			for tt in range(1,len(times)):
				if this_ts > times[tt-1] and this_ts < times[tt]:
					this_time_bin = tt
					events[this_time_bin][actions.index('timestamp')] = str(times[tt]/1000)
					print "ts found in bin " + str(this_time_bin)
					for q in list(deck):
						mouseup = re.search(r'"mouseup"',q)
						scroll = re.search(r'scroll|wheel',q)
						setcookie = re.search(r'"set-cookie"',q)
						t_bar = re.search(r'"tab-bar"',q)
						srchbar = re.search(r'searchbar',q)
						url = re.search(r'urlbar',q)
						if mouseup:
							events[this_time_bin][actions.index('clicks')] = events[this_time_bin][actions.index('clicks')] + 1
						elif scroll:
							events[this_time_bin][actions.index('scrolls')] = events[this_time_bin][actions.index('scrolls')] + 1
						elif setcookie:
							events[this_time_bin][actions.index('set-cookies')] = events[this_time_bin][actions.index('set-cookies')] + 1
						elif t_bar:
							events[this_time_bin][actions.index('tab-bar')] = events[this_time_bin][actions.index('tab-bar')] + 1
						elif srchbar:
							events[this_time_bin][actions.index('searchbar')] = events[this_time_bin][actions.index('searchbar')] + 1
						elif url:
							events[this_time_bin][actions.index('urlbar')] = events[this_time_bin][actions.index('urlbar')] + 1
					break
	fh = open("event_sums_ppt_" + str(pp) + ".json","w")
	fh.write(json.dumps(events))
	fh.close()
