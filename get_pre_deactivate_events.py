import re
import json

personIDs = json.load(open("personid_lines.json","r"))
lines=open("random10.search.events").readlines()
lookbackthresh = 10000 #in milliseconds
min_separation = 10 #in milliseconds

NumParticipants = 10
for pp in range(1,NumParticipants+1):
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
		last_ts = 0
		pre_events = 0
		print "DA Event " + str(e)
		for itr in range(this_start,this_end):
			deactivate_time = int(D_events[e][0])
			D_match = re.search(str(deactivate_time),lines[itr])
			if D_match:
				print "Match FOUND @ line " + str(itr) + "!!"

				for qq in range(itr,itr-20,-1):
					post_evstrid = re.search(r'"eventstoreid"',lines[qq])
					if post_evstrid:
						this_storeid = int(re.findall(r'\d+',lines[qq])[0])
						print "found deactivate event storeid, it is " + str(this_storeid)
				# Create loop to go backwards looking for events until a specified time
						if itr > 5000:
							trats = itr-5000
						if itr <= 5000:
							trats = 0
						for jj in range(itr,trats,-1):
							pre_ts = re.search(r'"ts":',lines[jj])
							if pre_ts:
								this_ts = int(re.findall(r'\d+',lines[jj])[0])
								if deactivate_time > this_ts and this_ts <= last_ts - min_separation:
									print "event " + str(deactivate_time-this_ts) + " milliseconds prior to deactivate event"
									pre_events = pre_events + 1
									last_ts = this_ts
									if this_ts <= deactivate_time - lookbackthresh:
										print "event OUT of window"
										jj = trats
										qq = itr-20
										output.append([pp,deactivate_time,itr,pre_events-1,e])
										itr = this_end
										break
#								elif int(D_events[e][0]) > int(re.findall(r'\d+',lines[jj])[0]) and int(D_events[e][0]) <= last_ts + min_separation:
#									continue
	events_out = open("PPT_" + str(pp) + "_pre-deactivate-events.json","w")
	events_out.write(json.dumps(output))
	events_out.close()

out = open("All_DeAct_Line_Nums.json","w")
out.write(json.dumps(lines))