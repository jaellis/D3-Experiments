import re
import json

tabIDs = json.load(open("Tabs_for_127raw.json"))
lines=open("raw-127.txt").readlines()

def findMoves(tabID,index,movedTabs,lines):
	if not(tabID in movedTabs):
		for newj in range(len(lines)):
			thisone = re.search(str(tabID),lines[newj])
			if thisone:
				ind_srch = re.search("index",lines[newj-1])
				if ind_srch and index != int(re.findall(r'\d+',lines[newj-1])[0]):
					movedTabs.append(tabID)
					print "tab " + str(tabID) + " moved"
					break
	return movedTabs

# def treeTabs():

# ...by context-menu open link in new tab click
# moneyGrabber(j,'context-openlinkintab',lines,cntxt,this_tab,flag)
def moneyGrabber(start,searchterm,lines,count,this_tab,flag):
	for g in range(start-1,start-5,-1):
		if re.search(searchterm,lines[g]): 
			cntxt = cntxt + 1
			flag = 1
			babma2 = re.search(re.escape('//')+"(.+)"+re.escape('/'),lines[g])
			this_tab['BornBy'] = searchterm
			if babma2:
				this_tab['BornIn'] = babma2.group()
				this_tab['BabyMama'] = re.search(r'tabid.+',lines[start-1]).group().split()[1]
				dest = re.search(re.escape('//')+"(.+)"+re.escape('/'),lines[j])
				if dest:
					this_tab['Destination'] = dest.group()
	return this_tab,count,flag

# looking by actions; could there be predestination for tabs 
# (i.e. do you know this will be a searching tab, a news-reading tab, etc.)
def showmethePages(tabIDs,lines):
	actionlist = ['tab-pageshow','scroll','wheel','mouseup']
	tab_newPages = {}
	for tt in tabIDs:
		tab_newPages[tt]= {actionlist[0]: 0, actionlist[1]: 0, actionlist[2]: 0} 
	for j in range(len(lines)):
		if re.search(r'"tabid":',lines[j]) and re.search(r'"action":',lines[j])
			tabbie = re.search(r'"tabid":.+',lines[j])
			if tabbie:
				thisGuy = int(re.findall(r'\d+',tabbie.group().split()[1])[0])
				action = re.search(r'"action":.+',lines[j]).group().split()[1]
				for act in actionlist:
 					if re.findall('[a-z]',action) == re.findall('[a-z]',act):
 						tab_newPages[thisGuy][act] = tab_newPages[thisGuy][act] + 1

def getBirths():
	tabIDwPID = json.load(open("tab_ids_wPID.json"))
	tabID = json.load(open("Tabs_for_127raw.json"))
	lines=open("raw-127.txt").readlines()
	tbcnt = 0
	mcnt = 0
	cntxt = 0
	cmdclk = 0
	tlbr = 0
	movedTabs = []
	tab_births = []
	unknowns = []
	for j in range(len(lines)):
		tb = re.search(r'"tab-open"',lines[j])
		if tb:
			flag = 0
			this_tab = {}
			tbcnt=tbcnt+1
			# Get window ID
			this_tab['thisWin']=int(re.findall(r'\d+',re.search(r'windowid.+',lines[j]).group().split()[1])[0])
			# Get participant number
			this_tab['PID']=int(lines[j].split()[0])
			# Get tab ID number
			this_tab['thisTab']=int(re.findall(r'\d+',re.search(r'tabid.+',lines[j]).group())[0])
			# Get tab index in window
			this_tab['Index']=int(re.findall(r'\d+',re.search(r'index.+',lines[j]).group().split()[1])[0])
			# Get born on timestamp
			this_tab['BornOn']=lines[j].split()[1]
			# ...born by mouse click on self-opening link?
			if re.search(r'"action": "mouseup"',lines[j-1]+lines[j-2]+lines[j-3]) and re.search(r'tab-deactivate',lines[j+1]+lines[j+2]) and re.search(r'tab-activate',lines[j+2]+lines[j+3]):
				mcnt = mcnt + 1
				this_tab['BornBy'] = 'left-mouse click'
				flag = 1
				for g in range(j-1,j-3,-1):
					if re.search(r'"action": "mouseup"',lines[g]):
						babma_ = re.search(re.escape('//')+"(.+)"+re.escape('/'),lines[g])
						this_tab['BabyMama'] = re.search(r'tabid.+',lines[g]).group().split()[1]
						if babma_:
							this_tab['BornIn'] = babma_.group()
						break
				for gg in range(j+2,j+5):
						if re.search(r'tab-ready',lines[g+2]):
							dest = re.search(re.escape('//')+"(.+)"+re.escape('/'),lines[j])
							if dest:
								this_tab['Destination'] = dest.group()
								break
							break
			# ...born by command + mouse click?
			#for h in range(j-1,j-3):
			if re.search(r'tab-pageshow',lines[j-1]+lines[j-2]+lines[j-3]) and not re.search(r'tab-deactivate',lines[j+1]+lines[j+2]): #re.search(r'"action": "mouseup"',lines[j-2]): 
				cmdclk = cmdclk + 1
				flag = 1
				this_tab['BornBy'] = 'command + mouse click'
				for h in range(j-1,j-3):
					cmdsrch = re.search(r'tab-pageshow',lines[h])
					if cmdsrch:
						babma = re.search(re.escape('//')+"(.+)"+re.escape('/'),lines[h])
						if babma:
							this_tab['BornIn'] = babma.group()
							this_tab['BabyMama'] = re.search(r'tabid.+',lines[j-1]).group().split()[1]
					dest = re.search(re.escape('//')+"(.+)"+re.escape('/'),lines[j])
					if dest:
						this_tab['Destination']  = dest.group()
			for g in range(j-1,j-5,-1):
				if re.search(r'context-openlinkintab',lines[g]): 
					cntxt = cntxt + 1
					flag = 1
					babma2 = re.search(re.escape('//')+"(.+)"+re.escape('/'),lines[g])
					this_tab['BornBy'] = 'click-to-menu'
					if babma2:
						this_tab['BornIn'] = babma2.group()
					this_tab['BabyMama'] = re.search(r'tabid.+',lines[j-1]).group().split()[1]
				dest = re.search(re.escape('//')+"(.+)"+re.escape('/'),lines[j])
				if dest:
					this_tab['Destination'] = dest.group()
			# ...by new tab button in chrome
			for g in range(j-1,j-5,-1):
				if re.search('xul:toolbarbutton',lines[g]):
					tlbr = tlbr + 1
					this_tab['BornBy'] =  'new tab button' 
					this_tab['BabyMama'] = re.search(r'tabid.+',lines[j-1]).group().split()[1]
					flag = 1
			if flag != 1:
				this_tab['BornBy'] = 'Immaculate Conception?'
				unknowns.append(int(re.findall(r'\d+',re.search(r'tabid.+',lines[j]).group())[0]))
			tab_births.append(this_tab)	
	print "self-opening links account for " + str(mcnt) + " of " + str(tbcnt) + " total tab opens"
	print str(round(mcnt/float(tbcnt)*100)) + " percent"
	print "command + click accounts for " + str(cmdclk) + " of " + str(tbcnt) + " total tab opens"
	print str(round(cmdclk/float(tbcnt)*100)) + " percent"
	print "click-to-context menu accounts for " + str(cntxt) + " of " + str(tbcnt) + " total tab opens"
	print str(round(cntxt/float(tbcnt)*100)) + " percent"
	print "new tab button accounts for " + str(tlbr) + " of " + str(tbcnt) + " total tab opens"
	print str(round(tlbr/float(tbcnt)*100)) + " percent"
	mathz = int((cmdclk+mcnt+cntxt+tlbr)/float(tbcnt)*100)
	print "accounting for " + str(mathz)+ " percent of all tab opens"
	fh = open("tab_births_raw127_dict.json","w")
	fh.write(json.dumps(tab_births))
	fh.close()
	fh = open("UNKOWNtabs_raw127.json","w")
	fh.write(json.dumps(unknowns))
	fh.close()
	return tab_births

def sortBirths():
	def accrueTabs(choiceNum,f):
		for p in f:
			PID = re.search('PID',str(p))
			if PID:
				thisSub = int(re.findall(r'\d+',str(f[f.index(p)+1]))[0])
				user_tab_choice[thisSub][choiceNum] = user_tab_choice[thisSub][choiceNum] + 1
		return user_tab_choice

	tab_births = json.load(open("tab_births_raw127_dict.json"))
	subbies = json.load(open("Raw127_Subs.json"))
	newNvTb_cnt = 0
	cntxt_cnt = 0
	mseclk_cnt = 0
	# user_tab_choice = {}
	user_tab_choice = []
	numPID = len(subbies)
	BornBys = ['left-mouse click','click-to-menu','command + mouse click','new tab button','Immaculate Conception?']
	for h in range(numPID):
		# user_tab_choice[h] = {'left-mouse click': 0,'click-to-menu': 0,'command + mouse click': 0,'Immaculate Conception?': 0}
		user_tab_choice.append([0,0,0,0,0])
	user_tab_choice.insert(0,BornBys)
	for f in tab_births:
		midwife = BornBys.index(f['BornBy'])
		subNum = subbies.index(f['PID'])
		user_tab_choice[subNum+1][midwife] = user_tab_choice[subNum+1][midwife] + 1
	fh = open("userTabChoices_raw127.json","w")
	fh.write(json.dumps(user_tab_choice))
	fh.close()

getBirths()
# showmethePages(tabIDs,lines)