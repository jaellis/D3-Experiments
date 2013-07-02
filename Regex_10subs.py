"""
Notes from Gregg and Ilana:
maybe we should use "window-deactivate" and "-activate" events to track consecutive activity
deactivate should end a session unless there is another activate within a second (or something reasonable)
Other interesting events:
add-on main (first one is weird); add-on main ("reason": start-up)
-- look at last five events before add-on close (=closing the browser/no more windows)

Heat Map of usage; log10 of the events around it/normalize it by the most intense usage
"""


import re
import json

personids=[]
personid_lines=[]
rndev=open("random10.search.events",'r')
lines = rndev.readlines()

for fp in range(len(lines)):
	personid = re.search(r'personid',lines[fp],re.I)
	if personid:
		personids.append([lines[fp],str(fp)])
		personid_lines.append(str(fp))

for person in range(1,len(personid_lines)):
	matchcount = 0
	tab_pageshow_events=[]
	for ln in range(int(personid_lines[person-1]),int(personid_lines[person])):
		tempurl=[]
		tempts=[]
		temptevent=[]
		searchmatch = re.search(r'tab-pageshow',lines[ln],re.I)
		if searchmatch:
			matchcount = matchcount + 1
			print "found a match"
			for i in range(ln-8,ln+6):
				matchurl = re.search(r'"url": ',lines[i],re.I)
				if matchurl:
#					print lines[i]
					tempurl.append(lines[i])
					tempurl.append(str(i))

				matchts = re.search(r'"ts": ',lines[i],re.I)
				if matchts:
#					print lines[i]
					tempts.append(lines[i])
					tempts.append(str(i))
			if tempurl:
				temptevent.append(tempurl)
			if tempts:
				temptevent.append(tempts)
		tab_pageshow_events.extend(temptevent)
	print str(matchcount) + " matches for ppt " + str(person)
	out = open("PPT_" + str(person) + "_tab_pageshow_events.json",'w')
	out.write(json.dumps(tab_pageshow_events))
	out.close()
outpers = open("personid_lines.json",'w')
outpers.write(json.dumps(personids))
outpers.close()
rndev.close()