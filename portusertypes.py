#!/usr/bin/env python
import re
import sys
import logging
import tldextract as tld
from collections import deque
from collections import defaultdict
from pprint import pprint as pp
try:
	import simplejson as json
except:
	import json

## Initialize ##
usermat = {}
mytabindex = {}
Counter1 = {'binned lifespans': defaultdict(int),'child data': defaultdict(int)}
Counter2 = {'binned lifespans': defaultdict(int),'child data': defaultdict(int)}

# def useranddatum(me):

def assignusertype(usermat,usertypes):
	for pt in usermat:
		try:
			usermat[pt]['user type'] = usertypes[pt]
		except:
			print pt
	return usermat

def comparemailandnotmail(usermat):
	mailtabs={'total mail tabs':0}
	nonmailtabs={'total non-mail tabs':0}
	mtemplfspn = []
	mbinnedlifespans=[]
	mtempnumchldrn = []
	nonmtemplfspn = []
	nonmtempnumchldrn = []	
	nonmbinnedlifespans=[]
	def binlifespans(usermat):
		lfspnrange = range(0,10000000,30000)
		binnedlifespans=[]
		for k in usermat:
			try:
				for kk in usermat[k]:
					for bin in range(len(lfspnrange)-1):
						if usermat[k][kk]['lifespan'] > lfspnrange[bin] and usermat[k][kk]['lifespan'] < lfspnrange[bin+1]:
							usermat[k][kk]['binned lfspn'] = lfspnrange[bin]
							break
			except:
				pass
				# print usermat[k][kk]
				# print "kk is",kk,"from binlifespans"
		return usermat

	def aggbymailorsearch(usermat,searchtype,Counter1,Counter2):
		print searchtype
		for k in usermat:
			for kk in usermat[k]:
				try:
					if usermat[k][kk][searchtype] is True and usermat[k][kk]['lifespan'] is not None:
						mtemplfspn.append(usermat[k][kk]['lifespan'])
						mtempnumchldrn.append(usermat[k][kk]['num children'])
						mbinnedlifespans.append(usermat[k][kk]['binned lfspn'])
						mailtabs['total mail tabs']+=1
					elif usermat[k][kk][searchtype] is False and usermat[k][kk]['lifespan'] is not None:
						nonmtemplfspn.append(usermat[k][kk]['lifespan'])
						nonmtempnumchldrn.append(usermat[k][kk]['num children'])
						nonmbinnedlifespans.append(usermat[k][kk]['binned lfspn'])
						nonmailtabs['total non-mail tabs']+=1
					# if usermat[k][kk]['lifespan'] < 100:
					# 	print usermat[k][kk]
				except:
					pass
					# print usermat[k][kk]
					# print "kk is",kk,"--from aggbymailorsearch"
		for v in mbinnedlifespans:
			Counter1['binned lifespans'][v]+=1
		for v2 in mtempnumchldrn:
			Counter1['child data'][v2]+=1
		for nonv in nonmbinnedlifespans:
			Counter2['binned lifespans'][nonv]+=1
		for nonv2 in nonmtempnumchldrn:
			Counter2['child data'][nonv2]+=1
		# print searchtype,"tabs:"
		# print Counter1
		# print "Non-" + str(searchtype) + "tabs:"
		# print Counter2
		# print "search term lfspns\n",len(mtemplfspn)
		# print "search term children\n",len(mtempnumchldrn)
		# print "non- lifespans\n",len(nonmtemplfspn)
		# print "non- children\n",len(nonmtempnumchldrn)
		# print "sum mtemplfspn",sum(mtemplfspn)
		print "length mtemplfspn",len(mtemplfspn)
		sort1 = mtemplfspn.sort()
		mailtabs['median_lifespan'] = sort1[int(len(mtemplfspn)/2)]
		mailtabs['avg lifespan'] = float(sum(mtemplfspn))/len(mtemplfspn)
		sort2 = mtempnumchldrn.sort()
		mailtabs['median num children'] = sort2[int(len(mtempnumchldrn)/2)]
		mailtabs['avg num children'] = float(sum(mtempnumchldrn))/len(mtempnumchldrn)
		# mailtabs['lifespan data'] = Counter(mtemplfspn).most_common(10)
		# mailtabs['child data'] = Counter(mtempnumchldrn).most_common(10)
		# mailtabsbinned['binned lifespans'] = Counter(mbinnedlifespans)
		print "sum nonmtemplfspn",sum(nonmtemplfspn)
		print "length nonmtemplfspn",len(nonmtemplfspn)
		sort3 = nonmtemplfspn.sort()
		nonmailtabs['median lifespan'] = sort3[int(len(nonmtemplfspn)/2)]
		nonmailtabs['avg lifespan'] = float(sum(nonmtemplfspn))/len(nonmtemplfspn)
		sort4 = nonmtempnumchldrn.sort()
		nonmailtabs['median num children'] = sort4[int(len(nonmtempnumchldrn)/2)]
		nonmailtabs['avg num children'] = float(sum(nonmtempnumchldrn))/len(nonmtempnumchldrn)
		# nonmailtabs['lifespan data'] = Counter(nonmtemplfspn).most_common(10)
		# nonmailtabs['child data'] = Counter(nonmtempnumchldrn).most_common(10)
		# nonmailtabsbinned['binned lifespans'] = Counter(nonmbinnedlifespans)
		print "\nDescriptives:",searchtype,"Tabs..."
		# print "Number of Children through Counter:",Counter1['binned lifespans']
		# print "LifeSpans through Counter:",Counter1['child data']
		print "\n More Descriptives:",searchtype,"Tabs..."
		for m in mailtabs:
			print m,"=",mailtabs[m]
		print "\nDescriptives: Non-" + str(searchtype) + " Tabs..."
		# print "Number of Children through Counter:",Counter2['binned lifespans']
		# print "LifeSpans through Counter:",Counter2['child data']
		print "\n More Descriptives: Non-" + str(searchtype) + " Tabs..."
		for n in nonmailtabs:
			print n,"=",nonmailtabs[n]

	usermat = binlifespans(usermat)
	aggbymailorsearch(usermat,'mail',Counter1,Counter2)
	aggbymailorsearch(usermat,'search',Counter1,Counter2)
	aggbymailorsearch(usermat,'social',Counter1,Counter2)
	aggbymailorsearch(usermat,'information',Counter1,Counter2)
	aggbymailorsearch(usermat,'video',Counter1,Counter2)

# def parcelbyusertype(usermat,usertypes):

def countusersbytype():
	usertypes = json.load(open("usertypes.json"))
	uniqueusertypes={}
	for l in usertypes:
		if usertypes[l] not in uniqueusertypes:
			uniqueusertypes[usertypes[l]] = {'num users': 1}
		elif usertypes[l] in uniqueusertypes:
			uniqueusertypes[usertypes[l]]['num users']+=1
	return uniqueusertypes,usertypes

def usertabindices(me,pid,usermat):
	social_sites=['facebook','twitter','myspace','instagram']
	video_sites=['youtube','hulu','netflix']
	information_sites=['news','times','post','wikipedia','tribune','herald']
	if pid not in usermat:
		usermat[pid] = {}
	if me['name'] not in usermat[pid]:
		usermat[pid][me['name']] = {}
		usermat[pid][me['name']] = {'lifespan': me['lifespan'],'num children':len(me['children']),'index': me['index'],'search': False,'mail': False,'social':False,'information':False,'video':False,'google search':False,'yahoo search':False}
		for i in me['urls_through_time']:
			if re.search('mail',i['url']):
				usermat[pid][me['name']]['mail'] = True
				break
		for i2 in me['urls_through_time']:
			if re.search('search',i2['url']):
				usermat[pid][me['name']]['search'] = True
				break
		for i3 in me['urls_through_time']:
			for soc in social_sites:
				if re.search(soc,i3['url']):
					usermat[pid][me['name']]['social'] = True
					break
				break
		for i4 in me['urls_through_time']:
			for inf in information_sites:
				if re.search(inf,i4['url']):
					usermat[pid][me['name']]['information'] = True
					break
				break
		for i5 in me['urls_through_time']:
			for vid in video_sites:
				if re.search(vid,i5['url']):
					usermat[pid][me['name']]['video'] = True
					break
				break
		for i6 in me['urls_through_time']:
			if re.search('www.google',i6['url']):
				usermat[pid][me['name']]['google search'] = True
				break
		for i7 in me['urls_through_time']:
			if re.search('search.yahoo',i7['url']):
				usermat[pid][me['name']]['yahoo search'] = True
				break
	return usermat

def myaveragetabindex(mytabindices):
	mytemptotal=0
	mytempind=0
	for i in mytabindices:
		mytempind += ((i+1)*mytabindices[i])
		mytemptotal+=mytabindices[i]
	try:
		return round(float(mytempind)/mytemptotal)
	except:
		pass
	

# def usertabdescriptives(usermat):
# 	for p in usermat:
# 		print "User #" + str(p) + 

[uniqueusertypes,usertypes] = countusersbytype()

# singles=[]
# pidict = defaultdict(int)

# def find_common_urls(me):
# 	if  

mail_sites = {'mail.google':0,'mail.yahoo':0,'mail.live':0,'mail.verizon':0}
interesting_spawn_sites = {'amazon':0,'twitter':0,'ebay':0,'youtube':0,'swagbucks':0,'facebook':0,'mail.google':0,'mail.yahoo':0,'mail.live':0,'mail.verizon':0,'bing':0}
pids_by_spawn_sites = {'amazon':{},'twitter':{},'ebay':{},'youtube':{},'swagbucks':{},'facebook':{},'mail.google':{},'mail.yahoo':{},'mail.live':{},'mail.verizon':{},'bing':{}}
lifespans_by_spawn_sites = {'amazon':[],'twitter':[],'ebay':[],'youtube':[],'swagbucks':[],'facebook':[],'mail.google':[],'mail.yahoo':[],'mail.live':[],'mail.verizon':[],'bing':[]}
act_periods_by_spawn_sites = {'amazon':[],'twitter':[],'ebay':[],'youtube':[],'swagbucks':[],'facebook':[],'mail.google':[],'mail.yahoo':[],'mail.live':[],'mail.verizon':[],'bing':[]}
has_mom = 0
no_mom = 0
mom_has_url=0
tabnum=0
momurls=defaultdict(int)
inddict = defaultdict(int)
name=[]
life=[]
active=[]
inactive=[]
indices_by_pid={}
mail_by_user={}
indexjson=[]
for line in sys.stdin:
	me = json.loads(line)
	pid = me['pid']
### get tab indices for each participant, and for groups
	if me['pid'] not in indices_by_pid:
		indices_by_pid[me['pid']] = defaultdict(int)
	if me['index'] not in ['null',None]:
		indices_by_pid[me['pid']][me['index']]+=1
	for u in me['urls_through_time']:
		for m in mail_sites:
			if re.search(m,u['url']):
				mail_by_user[me['pid']]={m:True}
				break
for pd in indices_by_pid:
	one_avgindex = myaveragetabindex(indices_by_pid[pd])
	print "pid",pd,"averages:",one_avgindex
	indexjson.append([pd,one_avgindex])
# fh=open("avg_index_by_pid.json","w")
# fh.write(json.dumps(indexjson))
# fh.close()
	usermat = usertabindices(me,pid,usermat)
	tabnum+=1
	if me['mother'] not in ['null',None]:# and len(me['urls_through_time'])!=0:	
		# print me
		has_mom+=1
		if me['mother_url'] not in ['null',None]:
			mom_has_url+=1
			momurls[me['mother_url']]+=1
			for n in interesting_spawn_sites:
				if re.search(n,me['mother_url']):
					if me['pid'] not in pids_by_spawn_sites[n]:
						pids_by_spawn_sites[n][me['pid']] = {'num_tabs':1,'lifespans':[]}
						if isinstance(me['lifespan'],int):
							pids_by_spawn_sites[n][me['pid']]['lifespans'].append(me['lifespan'])
					elif me['pid'] in pids_by_spawn_sites[n]:
						pids_by_spawn_sites[n][me['pid']]['num_tabs']+=1
						if isinstance(me['lifespan'],int):
							pids_by_spawn_sites[n][me['pid']]['lifespans'].append(me['lifespan'])
for q in pids_by_spawn_sites:
	for qq in pids_by_spawn_sites[q]:
		pids_by_spawn_sites[q][qq]['avg_lifespan']=round(float(sum(pids_by_spawn_sites[q][qq]['lifespans']))/len(pids_by_spawn_sites[q][qq]['lifespans']))
		lfspnsort = pids_by_spawn_sites[q][qq]['lifespans'].sort()
		pids_by_spawn_sites[q][qq]['median_lifespan']=lfspnsort[len(lfspnsort)/2]
		pids_by_spawn_sites[q][qq]['lifespans']=[]
					# interesting_spawn_sites[n]+=1
print has_mom,"tabs have a parent tab"
print "\nand",mom_has_url,"tabs have a parent tab with a labelled url"
print "\nwhich is",mom_has_url/float(has_mom)*100,"percent of tabs with parents"
print "\nand",mom_has_url/float(tabnum)*100,"percent of all tabs"
tmp_momurl_tot=[]
for m in momurls:
	tmp_momurl_tot.append(momurls[m])
sortedtmp = tmp_momurl_tot.sort()
momurl_median = sortedtmp[len(momurls)/2]
for mm in momurls:
	if momurls[mm] > momurl_median:
		print "site:",m,"//tabs spawned:",momurls[mm]

# for i in pids_by_spawn_sites:
# 	print "*****",i,"*****"
# 	for ii in pids_by_spawn_sites[i]:
# 		print pids_by_spawn_sites[i][ii]
# pp(pids_by_spawn_sites)
# for k in interesting_spawn_sites:
# 	print k,"makes up",interesting_spawn_sites[k]/float(tabnum)*100,"percent of tabs"
fh=open("pids_per_spawn_site.json","w")
fh.write(json.dumps(pids_by_spawn_sites))
fh.close()

usermat = comparemailandnotmail(usermat)

# usermat = json.load(open("usermat.json"))

# fh=open("usermat.json","w")
# fh.write(json.dumps(usermat))
# fh.close()

usermat = assignusertype(usermat,usertypes)
# fh=open("usermat.json","w")
# fh.write(json.dumps(usermat))
# fh.close()

# comparemailandnotmail(usermat)
# fh=open("usermat.json","w")
# fh.write(json.dumps(usermat))
# fh.close()

# for ut in uniqueusertypes:
