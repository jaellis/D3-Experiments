import json
import re

DeActs = json.load(open("New_All_10.json","r"))
NumParticipants = 10
for pp in range(1,NumParticipants+1):
	PreSource = json.load(open("PPT_" + str(pp) + "_pre-deactivate-events.json","r"))
	for entr in range(len(DeActs)):
		if DeActs[entr][1] == pp:
			for pre in PreSource:
				if pre[1] == int(DeActs[entr][0]):
					DeActs[entr].append(pre[3])

tf=open("All_10_test_add.json","w")
tf.write(json.dumps(DeActs))
tf.close()