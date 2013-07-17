"""
Explore:
1) number of clicks
2) number of scrolls
3) did this tab change identity through clicks or through the url-bar?
4) how many tabs added?
	4a) what is the chronology of tabs being added
	4b) do tabs die en masse (extinction) or singly (execution)

could add a title search within the tab live/death search; get length on each title
"""

import json
import re

personIDs = json.load(open("personid_lines.json","r"))
lines=open("random10.search.events").readlines()
DeActs = json.load(open("New_All_10.json","r"))

#NumParticipants = 10
#for pp in range(10,NumParticipants+1):
tab_ids=[]
for l in range(len(lines)):
	a_tab = re.search(r'"tabid":',lines[l])
	if a_tab and not(int(re.findall(r'\d+',lines[l])[0]) in tab_ids):
		tab_ids.append(int(re.findall(r'\d+',lines[l])[0]))
		print "New Tab, ID# " + str(int(re.findall(r'\d+',lines[l])[0]))

tab_lives=[]
for tab in tab_ids:
	born_on = 0
	rip_date = 0
	tab_activity = []
	tab_birth = []
	tab_death = []
	print str(tab)
	for l in range(len(lines)):
		tb_srch = re.search(str(tab),lines[l])
		if tb_srch:
			print "activity"
			for dem_lines in range(l-10,l+10):
				pgshw_srch = re.search(r'"action": "tab-pageshow"|"mouseup"|"scroll"|"wheel"',lines[dem_lines])
				if pgshw_srch:
					for act_ln in range(dem_lines,dem_lines-5,-1):
						tab_act = re.search(r'"ts":',lines[act_ln])
						if tab_act:
							tab_activity.append(int(re.findall(r'\d+',lines[act_ln])[0]))
				# Search for a Born On time
				birth_srch = re.search(r'"action": "tab-activate"',lines[dem_lines])
				if birth_srch:
					for k_ln in range(dem_lines,dem_lines-5,-1):
						bts_srch = re.search(r'"ts":',lines[k_ln])
						# Make sure this birth time is outside a given window of previous birth time
						if bts_srch and int(re.findall(r'\d+',lines[k_ln])[0]) - 100 > born_on:
							born_on = int(re.findall(r'\d+',lines[k_ln])[0])
							tab_birth.append(['birth',born_on])
							print "Time: " + str(born_on)
							print "tab " + str(tab) + " is born!!"
				# Search for a Death time
				kill_srch = re.search(r'"action": "tab-deactivate"',lines[dem_lines])
				if kill_srch:
					for k_ln in range(dem_lines,dem_lines-5,-1):
						kts_srch = re.search(r'"ts":',lines[k_ln])
						# Make sure this kill time is outside a given window of previous kill time
						if kts_srch and int(re.findall(r'\d+',lines[k_ln])[0]) - 100 > rip_date:
							rip_date = int(re.findall(r'\d+',lines[k_ln])[0])
							tab_death.append(['killed',rip_date])
							print "Time: " + str(rip_date)
							print "tab " + str(tab) + " is killed"
				wnkill_srch = re.search(r'"action": "deactivate"|"close"',lines[dem_lines])
				if wnkill_srch:
					extinction = []
					for wnk_ln in range(dem_lines+8,dem_lines-10,-1):
						wnkts_srch = re.search(r'"ts":',lines[wnk_ln])
						if wnkts_srch and int(re.findall(r'\d+',lines[wnk_ln])[0]) - 100 > rip_date:
							rip_date = int(re.findall(r'\d+',lines[wnk_ln])[0])
							extinction.append(['extinction',rip_date])
							print "Time: " + str(rip_date)
							print "tab " + str(tab) + " dies by window closure"
							the_dead = []
					# Search for other tabs in the tabenocide
							for extnct_ln in range(wnk_ln,wnk_ln+5):
								extnct_srch = re.search(r'"tabids"',lines[extnct_ln])
								if extnct_srch:
									for dd in range(extnct_ln+1,extnct_ln+10):
										brk_srch = re.search(r'"ts":',lines[dd])
										if brk_srch:
											break
										dead = re.findall(r'\d+',lines[dd])
										if dead:
											the_dead.append(int(re.findall(r'\d+',lines[dd])[0]))
									extinction.append(the_dead)
	tab_lives.append([tab_birth,tab_death,extinction,tab_activity])
	print "finished with tab " + str(tab)

				# Does a click in window precede?
				#for clksrch in range():
				#	clk = re.search(r'"action": "mouseup"',clksrch)
				#	if clk:
				#		spot = tab_ids.index(this_tab)
				#		tab_ids.pop(spot)
				#		tab_ids.insert(spot,[this_tab,'click-open'])



