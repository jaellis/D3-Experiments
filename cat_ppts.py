import json

final = []
for ppt in range(1,10):
	thisload = json.load(open("PPT_" + str(ppt) + "_deactivate_events.json"))
	final.extend(thisload)

out = open("All_10_ppt_deactivation_events.json","w")
out.write(json.dumps(final))
out.close()
