"""
This script pulls in the deactivation events and looks 
for the <<num>> number of events preceeding them
"""
import re
import json

personIDs = json.load(open("personid_lines.json","r"))

NumParticipants = 10

for pp in range(1,NumParticipants+1):
	lines = []
	count = 0
	# Set participant start & end line
	this_start = int(personIDs[pp][1])
	if pp < 10:
		this_end = int(personIDs[pp+1][1])
	if pp == 10:
		this_end = 5779243
	print "Digging into Participant " + str(pp) + "'s sanitized, HIPPA-certified, organic, biodiesel DATA!"
	D_events = json.load(open("PPT_" + str(pp) + "_deactivate_events.json","r"))
	for e in range(len(D_events)):
		flag=0
		print "DA Event " + str(e)
		with open("random10.search.events","r") as source:
#			while flag == 0:
				print "HERE!!!"
				for itr in range(this_start,this_end):
					line = source.readline(itr)
					count = count+1;
					D_match = re.search(str(D_events[e][0]),line)
					if D_match:
						print "Match FOUND @ line " + str(count) + "!!"
#						flag = 1
						lines.extend([count,pp])
						break
out = open("All_DeAct_Line_Nums_ppt" + str(pp) + ".json","w")
out.write(json.dumps(lines))
out.close()