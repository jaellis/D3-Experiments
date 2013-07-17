import json
import re
import random

# Load Data first
tab_ids = json.load(open("tab_ids.json","r"))
tab_lives = json.load(open("prelim_tab_lives_071113.json","r"))

# Generate FIR filter
fir=[]
filter_length = 30
for t in range(filter_length):
	fir.append(random.gauss(10,2))

def convolve(t,name):
	#find omega event
	if t[1] and t[2]:
		deathday = max(max(t[1])[1],max(t[2])[1])
	elif t[1] and not t[2]:
		deathday = max(max(t[1])[1])
	elif t[2] and not t[1]:
		deathday = max(t[2])[1]
	elif not t[1] and not t[2]:
		deathday = max(t[3])
	thistabID = tab_ids[tab_lives.index(t)]
	# convolve events and FIR filter
	timeline = [0] * (((deathday-birthday)/100)+1)
	x_axis = range(deathday/100-birthday/100)
	print "timeline length = " + str(len(timeline))
	for event in t[3]:
		start = abs((min(t[3])-event)/100)
		if start > len(timeline) - filter_length:
			break
		else:
			print "event @ ts " + str(start)
			for p in range(start,start+len(fir)):
				timeline.insert(p,timeline[p]+fir[p-start])
				timeline.pop(p+1)
	thing1=[timeline,x_axis,name]
	return thing1

fir.sort()
fir.reverse()
deaths = []
tls = []
for t in tab_lives:
	name = tab_lives.index(t)
	print "tab # " + str(name)
	#find alpha event
	if t[0]:
		birthday = t[0][0][1]
		thing2 = convolve(t,name)
	elif t[-1]:
		birthday = min(t[-1])
		thing2 = convolve(t,name)
	tls.append(thing2)
	print "done w/ #" + str(name)

fh=open("some_timelines.json","w")
fh.write(json.dumps(tls))
fh.close()

