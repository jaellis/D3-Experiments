import re
import json

personIDs = json.load(open("personid_lines.json","r"))
lines=open("random10.search.events").readlines()
lookbackthresh = 10000 #in milliseconds
min_separation = 10 #in milliseconds

NumParticipants = 10
for pp in range(10,NumParticipants+1):
	output = []
	count = 0
	# Set participant start & end line
	this_start = int(personIDs[pp-1][1])
	if pp < 10:
		this_end = int(personIDs[pp][1])
	if pp == 10:
		this_end = 5779243
	print "Digging into Participant " + str(pp) + "'s sanitized, HIPPA-certified, organic, biodiesel DATA!"
	D_events = json.load(open("PPT_" + str(pp) + "_deactivate_events.json","r"))
	for e in range(len(D_events)):
		pre_events = 0
		deactivate_time = int(D_events[e][0])
		last_ts = deactivate_time
		print "DA Event " + str(e)
		for itr in range(this_start,this_end):
			D_match = re.search(str(deactivate_time),lines[itr])
			if D_match:
				print "Match FOUND @ line " + str(itr) + "!!"
				for qq in range(itr,itr-20,-1):
					post_evstrid = re.search(r'"eventstoreid"',lines[qq])
					if post_evstrid:
						this_storeid = int(re.findall(r'\d+',lines[qq])[0])
						print "found deactivate event storeid, it is " + str(this_storeid)
				# Create loop to go backwards looking for events until a specified time
						if itr > 2000:
							trats = itr-2000
						if itr <= 2000:
							trats = 0
						for jj in range(itr,trats,-1):
							pre_ts = re.search(r'"ts":',lines[jj])
							if pre_ts:
								this_ts = int(re.findall(r'\d+',lines[jj])[0])
#								print "found a pre_ts at line " + str(jj)
#								print "last ts = " + str(last_ts)
#								print "this ts = " + str(this_ts)
								if this_ts < deactivate_time and this_ts <= last_ts - min_separation and this_ts >= deactivate_time - lookbackthresh:
									print "event " + str(deactivate_time-this_ts) + " milliseconds prior to deactivate event"
									pre_events = pre_events + 1
									last_ts = this_ts
#									print str(last_ts) + " = last ts"
								if this_ts <= deactivate_time - lookbackthresh:
									print "event OUT of window, " + str(deactivate_time-this_ts) + "ms before deactivation"
#									jj = trats
#									qq = itr-20
									output.append([pp,deactivate_time,itr,pre_events-1,e])
#									itr = this_end
									break
				break
	events_out = open("PPT_" + str(pp) + "_pre-deactivate-events.json","w")
	events_out.write(json.dumps(output))
	events_out.close()

out = open("All_DeAct_Line_Nums.json","w")
out.write(json.dumps(lines))