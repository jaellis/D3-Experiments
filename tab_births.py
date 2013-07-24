
import re
import json

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

def getBirths():
	tabIDwPID = json.load(open("tab_ids_wPID.json"))
	lines=open("random10.search.events").readlines()
	tbcnt = 0
	mcnt = 0
	cmd = 0
	movedTabs = []
	tab_births = []
	for j in range(len(lines)):
		tb = re.search(r'"tab-open"',lines[j])
		if tb:
			flag = 0
			this_tab = []
			tbcnt=tbcnt+1
			for winnie in range(j+1,j+10):
				winid = re.search('"windowid"',lines[winnie])
				if winid:
					this_tab.extend(['window ID:'])
					this_tab.extend([int(re.findall(r'\d+',lines[winnie])[0])])
					# break
			for qp in range(j-1,j-10,-1):
				tabid_srch = re.search(r'"tabid"',lines[qp])
				if tabid_srch:
					tabid = int(re.findall(r'\d+',lines[qp])[0])
					# get participant number
					for pid in tabIDwPID:
						if pid[0] == tabid:
							this_tab.extend(['PID:',pid[1]])
							break
					this_tab.extend(["this tabid:"])
					this_tab.extend([tabid])
					for jj in range(qp-1,qp-5,-1):
						index = re.search(r'"index".+',lines[jj])
						if index:
							this_tab.extend([index.group()])
							index = int(re.findall(r'\d+',lines[jj])[0])
							# print "checking tab " + str(tabid) + " for movement in tabbar"
							# movedTabs = findMoves(tabid,index,movedTabs,lines)
							break
			for l in range(j-1,j-40,-1):
				act = re.search(r'"action": "mouseup"',lines[l])
				tbshw = re.search(r'"tab-pageshow"',lines[l])
				cmdsrch1 = re.search(r'command.+',lines[l])
				if act:
					this_tab.extend(['open action:',act.group()])
					mcnt = mcnt + 1
					for s in range(l,l-20,-1):
						url = re.search(r'"url".+|"location".+|title.+',lines[s])
						if url:
							mama1 = re.search(re.escape(r'//')+"(.*?)"+re.escape('/'),lines[s])
							maTabnum1 = re.search(r'"tabid.+"',lines[s])
							if mama1 and not re.search(r'about',mama1.group()):
								this_tab.extend(['MamaPage1:',mama1.group(1)])
								break
							elif url and re.search(r'about',url.group()):
								this_tab.extend(['MamaPage1:',url.group()])
								break
							elif maTabnum1:
								this_tab.extend(['MamaPageTabNum:',int(maTabnum1.group()[0])])
				if cmdsrch1:
					cmd = cmd + 1
					this_tab.extend(['open cmd:',cmdsrch1.group()])
					for mm in range(j+20,j-30,-1):
						deact_srch = re.search(r'"tab-deactivate"',lines[mm])
						if deact_srch:
							for ds in range(mm,mm-10):
								ma_srch1 = re.search(r'"url".+|"location".+',lines[ds])
								if ma_srch1:
									mama2 = re.search(re.escape(r'//')+"(.*?)"+re.escape('/'),lines[mm])
									this_tab.extend(['MamaPage2:',mama2.group(1)])
									break
									masrchcnt = 3
						ma_srch2 = re.search(r'"url".+|"location".+',lines[mm])
						if ma_srch2 and not re.search('about',ma_srch2.group()):
							mama3 = re.search(re.escape(r'//')+"(.*?)"+re.escape('/'),lines[mm])
							this_tab.extend(['MamaPage3:',mama3.group(1)])
							flag = 1
							break
				if tbshw: 
					for g in range(l-1,l-20,-1):
						cmdsrch2 = re.search(r'command.+|action.+',lines[g])
						if cmdsrch2 and flag != 1:
							cmd = cmd + 1
							this_tab.extend([cmdsrch2.group()])
						mama4 = re.search(re.escape(r'//')+"(.*?)"+re.escape('/'),lines[g])
						maTabnum2 = re.search(r'"tabid.+"',lines[g])
						if mama4 and not re.search(r'about',mama4.group()):
							this_tab.extend(['MamaPage4:',mama4.group(1)])
						elif maTabnum2:
							this_tab.extend(['MamaPageTabNum',int(re.findall(r'\d+',maTabnum2.group())[0])])
			j=len(lines)
			tab_births.append(this_tab)
	print "mouseups account for " + str(mcnt) + " of " + str(tbcnt) + " total tab opens"
	print "commands account for " + str(cmd) + " of " + str(tbcnt) + " total tab opens"
	mathz = int((cmd+mcnt)/float(tbcnt)*100)
	print "accounting for " + str(mathz)+ " percent of all tab opens"
	fh = open("tab_births.json","w")
	fh.write(json.dumps(tab_births))
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

	tab_births = json.load(open("tab_births.json"))
	newNvTb_cnt = 0
	cntxt_cnt = 0
	mseclk_cnt = 0
	user_tab_choice = []
	numPID = 10
	for h in range(0,10):
		user_tab_choice.append([0,0,0])
	user_tab_choice.insert(0,['newNavigatorTab','context-openlinkintab','mouseup'])
	for f in tab_births:
		for i in f:
			srch1=re.search(r'newNavigatorTab',str(i))
			srch2=re.search(r'context-openlinkintab',str(i))
			srch3=re.search(r'mouseup',str(i))
			if srch1:
				newNvTb_cnt = newNvTb_cnt + 1
				user_tab_choice = accrueTabs(0,f)
				# print tab_births.index(f)
				# for ii in f:
				# 	masrch = re.search('MamaPage',ii)
				# 	if masrch and not re.search('blank',ii+1):
				# 		print f[f.index(ii)+1]
			if srch2:
				cntxt_cnt = cntxt_cnt + 1
				user_tab_choice = accrueTabs(1,f)
			if srch3:
				mseclk_cnt = mseclk_cnt + 1
				user_tab_choice = accrueTabs(2,f)
	print "New Navigator Tabs account for " + str(int(newNvTb_cnt/float(len(tab_births))*100)) + " percent of all tab births"
	print "context-openlinkinnewtab's account for " + str(int(cntxt_cnt/float(len(tab_births))*100)) + " percentof all tab births"
	print "Mouse clicks in prev page, auto-generating new tabs, account for " + str(int(mseclk_cnt/float(len(tab_births))*100)) + " percent of all tab births"
	for aa in range(numPID):
		SubDat = user_tab_choice[aa+1]
		print "Subject " + str(aa) + " tab choice stats:"
		print "total new tabs = " + str(sum(SubDat))
		for g in range(len(SubDat)):
			print "Percentage from " + str(user_tab_choice[0][g]) + ": " + str(int(SubDat[g]/float(sum(SubDat))*100))
	fh = open("userTabChoices.json","w")
	fh.write(json.dumps(user_tab_choice))
	fh.close()

sortBirths()
