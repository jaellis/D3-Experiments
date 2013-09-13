#!/usr/bin/env python
import re
import sys
import logging
from collections import defaultdict
from pprint import pprint as pp
try:
	import simplejson as json
except:
	import json

## Initialize ##
usermat = {}
activitymat = {}
mytabindex = {}
all_sites = ['linkedin','mail','search','plus.google','search.yahoo','www.google','instagram','tumblr','wikipedia','hulu','netflix','amazon','twitter','ebay','youtube','swagbucks','facebook','mail.aol','search.aol','mail.google','mail.yahoo','mail.live','mail.verizon','etsy','bing','reddit']
spawned_from_all_sites = defaultdict(int)
pids_by_spawn_sites = {}
interesting_spawn_sites = {}
for a in all_sites:
	pids_by_spawn_sites[a]={}
	interesting_spawn_sites[a]=0
	activitymat[a] = {}

# def nest_tabs():


## Called by comparemailandnotmail
## Returns min/max/quartiles for data piece
def five_point_data_summary(data):
	five_points={}
	sorted_data = sorted(data)
	# five_points['a_minimum'] = min(sorted_data)
	five_points['b_maximum'] = max(sorted_data)
	five_points['c_first_quartile'] = sorted_data[len(sorted_data)/4]
	five_points['d_second_quartile'] = sorted_data[len(sorted_data)/2]
	five_points['e_third_quartile']= sorted_data[len(sorted_data)*3/4]

	return five_points


def assignusertype(data,usertypes):
	for pt in data:
		try:
			data[pt]['user_type'] = usertypes[str(pt)]
		except:
			print pt
	return data

### 
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
	return usermat


def comparemailandnotmail(usermat,all_sites):
		
	def compare_across_a_tab_type(tab_type,usermat):
		# Initialize
		traits_to_compare = ['lifespan','num children','tab-pageshows','clicks','scrolls/wheels','last_act_to_death_latency','active_time']
		selected_tabs = defaultdict(list)
		
		for k in usermat:
			for kk in usermat[k]:
			#these are the tabs we are looking for
				if usermat[k][kk][tab_type] is True:# and usermat[k][kk]['lifespan'] not in ['null',None]:
					for i in traits_to_compare:
						if 'lifespan' == i and usermat[k][kk][i] in ['null',None]:
							continue
						else:
							selected_tabs[i].append(usermat[k][kk][i])
		return selected_tabs

	for type_of_tab in all_sites+['shopping','information','gaming']:
		print "* * * *",type_of_tab.upper(),"TABS * * * * "
		selected_tabs = compare_across_a_tab_type(type_of_tab,usermat)	
		print "n =",len(selected_tabs[selected_tabs.keys()[0]])
		for i in selected_tabs:
			print i + ":"
			five_points = five_point_data_summary(selected_tabs[i])
			for f in sorted(five_points):
				print f,"=",five_points[f]
	return usermat


def countusersbytype():
	usertypes = json.load(open("usertypes.json"))
	uniqueusertypes={}
	for l in usertypes:
		if usertypes[l] not in uniqueusertypes:
			uniqueusertypes[usertypes[l]] = {'num users': 1}
		uniqueusertypes[usertypes[l]]['num users']+=1
	return uniqueusertypes,usertypes

### Code a tab by a) the url of its parent, or b) the urls that it has visited over time
def classify_tab_by_url(me,pid,usermat,whose_url,all_sites):
	
	## Called by "find_sites_in_my_urls"
	## Looks through urls for a search term (can pass one or many) and, if found, changes that tab's Boolean Callsign to True
	def look_through_urls(me,search_term,boolean_callsign,this_tab_usermat):
		if isinstance(search_term,list):
			for i in search_term:
				for url in me['urls_through_time']:
					if re.search(i,url['url']):
						this_tab_usermat[boolean_callsign] = True
						break
		else:
			for url in me['urls_through_time']:
				if re.search(search_term,url['url']):
					this_tab_usermat[boolean_callsign] = True
		return this_tab_usermat

	## Called by "classify_tab_by_url"
	## Calls "look_through_urls" to check if a tab has visited a certain location or set of locations
	def find_sites_in_my_urls(me,pid,this_tab_usermat,all_sites):
		social_sites=['facebook','twitter','myspace','instagram']
		video_sites=['youtube','hulu','netflix']
		information_sites=['news','times','post','wikipedia','reddit','tribune','herald']
		gaming_sites=['game','play']
		shopping_sites = ['amazon','ebay','etsy','shop']
		this_tab_usermat = look_through_urls(me,'mail','mail',this_tab_usermat)
		this_tab_usermat = look_through_urls(me,'search','search',this_tab_usermat)
		this_tab_usermat = look_through_urls(me,social_sites,'social',this_tab_usermat)
		this_tab_usermat = look_through_urls(me,information_sites,'information',this_tab_usermat)
		this_tab_usermat = look_through_urls(me,video_sites,'video',this_tab_usermat)
		this_tab_usermat = look_through_urls(me,shopping_sites,'shopping',this_tab_usermat)
		this_tab_usermat = look_through_urls(me,gaming_sites,'gaming',this_tab_usermat)
		for s in all_sites:
			this_tab_usermat = look_through_urls(me,s,s,this_tab_usermat)
		return this_tab_usermat

	## Compares locations to parent_url
	def find_sites_in_parent_urls(me,pid,this_tab_usermat,all_sites):
		social_sites=['facebook','twitter','myspace','instagram','tumblr']
		video_sites=['youtube','hulu','netflix']
		information_sites=['news','times','post','wikipedia','tribune','herald']
		gaming_sites=['game','play','pogo']
		shopping_sites = ['amazon','ebay','etsy','shop']
		for s in all_sites:
			if re.search(s,me['parent_url']):
				this_tab_usermat[s] = True
		if re.search('mail',me['parent_url']):
			this_tab_usermat['mail'] = True
		if re.search('search',me['parent_url']):
			this_tab_usermat['search'] = True
		for soc in social_sites:
			if re.search(soc,me['parent_url']):
				this_tab_usermat['social'] = True
		for inf in information_sites:
			if re.search(inf,me['parent_url']):
				this_tab_usermat['information'] = True
		for vid in video_sites:
			if re.search(vid,me['parent_url']):
				this_tab_usermat['video'] = True
		for shop in shopping_sites:
			if re.search(shop,me['parent_url']):
				this_tab_usermat['shopping'] = True
		return this_tab_usermat

	## Script for classify_tabs_by_url:
	if 'mine' == whose_url:
		usermat[pid][me['name']] = find_sites_in_my_urls(me,pid,usermat[pid][me['name']],all_sites)
	elif 'parent' == whose_url:
		usermat[pid][me['name']] = find_sites_in_parent_urls(me,pid,usermat[pid][me['name']],all_sites)

	return usermat

###
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

### print unique users that utilize each open method
def print_unique_users_and_their_open_methods(datadict):
	for i in datadict:
		print i,":"
		print "num users =",len(datadict[i])


def aggregate_tab_activity(me,data_slice):
	data_slice
	return data_slice

###
def add_uniq_users_to_tab_open_method(me,tab_open_types):
	if me['born_by'] not in tab_open_types:
		tab_open_types[me['born_by']] = {}
	if me['pid'] not in tab_open_types[me['born_by']]:
		tab_open_types[me['born_by']][me['pid']] = {}
	return tab_open_types

[uniqueusertypes,usertypes] = countusersbytype()

tab_open_types = {}
bad_lfspncount = 0
good_lfspncount = 0
has_mom = 0
no_mom = 0
mom_has_url=0
tabnum=0
momurls=defaultdict(int)
inddict = defaultdict(int)
indices_by_pid={}
uniq_index = {}
mytotaltabs = defaultdict(int)
# mail_by_user={}
indexjson=[]
# lifespans = []
grandma={}
born_from_mail_click=0
born_from_dict=defaultdict(int)
passed_through_dict=defaultdict(int)

### Stream data and json.load line
for line in sys.stdin:
	me = json.loads(line)
	pid = me['pid']

###################
### Nest children for geneology
	# if len(me['children'])>10:
	# 	grandma[me['name']]={}
	# 	for i in me['children']:
	# 		grandma[me['name']][i] = {}
	# if me['parent'] in grandma:
	# 	for j in me['children']:
	# 		grandma[me['parent']][me['name']][j] = {'children':None,'name':j['last_url']}
	# 		print "\n\n",grandma
	# else:
	# 	for k in grandma:
	# 		if len(grandma[k])>0:
	# 			if me['parent'] in grandma[k]:
	# 				for q in me['children']:
	# 					grandma[k][me['parent']][me['name']][q] = {}
###################
	
#################
### Get total tabs per user
	mytotaltabs[me['pid']]+=1

### Get Unique users that have a given tab index
# 	if me['index'] not in uniq_index:
# 		uniq_index[me['index']]={}
# 	uniq_index[me['index']][pid] = True
# print "Tab Indices and number of unique users"
# for p in uniq_index:
# 	# print "Num Tabs:",p,"\n --- >",len(uniq_index[p]),"users"
# 	print len(uniq_index[p]),p


# 	if me['lifespan'] not in ['null',None]:
# 		lifespans.append(me['lifespan'])
	
	# for u in me['urls_through_time']:
	# 	for m in mail_sites:
	# 		if re.search(m,u['url']):
	# 			mail_by_user[me['pid']]={m:True}
	# 			break

##################
### Get tab indices for each participant, and for groups
# if me['pid'] not in indices_by_pid:
# 		indices_by_pid[me['pid']] = defaultdict(int)
# if me['index'] not in ['null',None]:
# 	indices_by_pid[me['pid']][me['index']]+=1
# for pd in indices_by_pid:
# 	one_avgindex = myaveragetabindex(indices_by_pid[pd])
# 	indices_by_pid[pd]['avg_index'] = one_avgindex
# 	# print "pid",pd,"averages:",one_avgindex
# 	indexjson.append([pd,one_avgindex])

# indices_by_pid = assignusertype(indices_by_pid,usertypes)

# for u in uniqueusertypes:
# 	temp_total = []
# 	for i in indices_by_pid:
# 		if u == indices_by_pid[i]['user_type']:
# 			temp_total.append(indices_by_pid[i]['avg_index'])
# 	temp_total.sort()
# 	five_point_sum = five_point_data_summary(temp_total)
# 	print u,":"
# 	for f in five_point_sum:
# 		print f,":",five_point_sum[f]

# fh=open("avg_index_by_pid.json","w")
# fh.write(json.dumps(indexjson))
# fh.close()
##################

# ### Fix mail count
# 	tabnum+=1
# 	if me['parent_url'] not in ['null',None]:	
# 		for i in all_sites:
# 			if 'left_mouse-click' == me['born_by'] and re.search(i,me['parent_url']):
# 				born_from_dict[i]+=1
# for a in born_from_dict:
# 	print born_from_dict[a],"tabs left-click born from",a
# 	print round(born_from_dict[a]/float(tabnum)*100),"percent"
### Count "gone through" any of ____ urls
	all_sites = ['linkedin','mail','search','plus.google','search.yahoo','www.google','instagram','tumblr','wikipedia','hulu','netflix','amazon','twitter','ebay','youtube','swagbucks','facebook','mail.aol','search.aol','mail.google','mail.yahoo','mail.live','mail.verizon','etsy','bing','reddit']
	tabnum+=1
	if len(me['urls_through_time']) > 0:
		for u in me['urls_through_time']:
			for i in all_sites:
				if re.search(i,u['url']):
					passed_through_dict[i]+=1
					all_sites.remove(i)
					break
for a in passed_through_dict:
	print passed_through_dict[a],"tabs passed through",a
	print round(passed_through_dict[a]/float(tabnum)*100),"percent"

### These lines will pull activity/inactivity times and lengths
	

### These two lines will aggregated uniquw users under each tab-open method they use
	# tab_open_types = add_uniq_users_to_tab_open_method(me,tab_open_types)
# print_unique_users_and_their_open_methods(tab_open_types)

# 	if pid not in usermat:
# 		usermat[pid] = {}
# 	if me['name'] not in usermat[pid]:
# 		usermat[pid][me['name']] = {'last_act_to_death_latency':me.get('last_act_to_death_latency',0),'lifespan': me['lifespan'],'scrolls/wheels':me['total actions']['scroll']+me['total actions']['wheel'],'tab-pageshows':me['total actions']['tab-pageshow'],'clicks':me['total actions']['click']+me['total actions']['mouseup'],'num children':len(me['children']),'index': me['index']}
# 		## sum active time
# 		tot_active_time=0
# 		for k in me['activity_periods']:
# 			if me['activity_periods'][k] not in ['null',None]:
# 				tot_active_time+=me['activity_periods'][k]['length']
# 		usermat[pid][me['name']]['active_time'] = tot_active_time

# 		for a in all_sites:
# 			usermat[pid][me['name']][a]=False	

# # Classify tabs by urls of a) parent or b) own visits	
# 	if me['parent_url'] not in ['null',None]:
# 		usermat = classify_tab_by_url(me,pid,usermat,'parent',all_sites)
	# tabnum+=1
# 	if me['parent'] not in ['null',None]:
# 		has_mom+=1
# 		if me['parent_url'] not in ['null',None]:
# 			mom_has_url+=1
# 			momurls[me['parent_url']]+=1
# 			for n in all_sites:
# 				if re.search(n,me['parent_url']):
# 					interesting_spawn_sites[n]+=1
# 					if me['pid'] not in pids_by_spawn_sites[n]:
# 						pids_by_spawn_sites[n][me['pid']] = {'num_tabs':1,'lifespans':[]}
# 					elif me['pid'] in pids_by_spawn_sites[n]:
# 						pids_by_spawn_sites[n][me['pid']]['num_tabs']+=1
# 						if isinstance(me['lifespan'],int):
# 							pids_by_spawn_sites[n][me['pid']]['lifespans'].append(me['lifespan'])
										
# for q in pids_by_spawn_sites:
# 	print q,"attracted",len(pids_by_spawn_sites[q]),"users"
# 	# for qq in pids_by_spawn_sites[q]:
# 	# 	pids_by_spawn_sites[q][qq]['avg_lifespan']=round(float(sum(pids_by_spawn_sites[q][qq]['lifespans']))/len(pids_by_spawn_sites[q][qq]['lifespans']))
# 	# 	lfspnsort = sorted(pids_by_spawn_sites[q][qq]['lifespans'])
# 	# 	pids_by_spawn_sites[q][qq]['median_lifespan']=lfspnsort[len(lfspnsort)/2]
# 	# 	pids_by_spawn_sites[q][qq]['lifespans']=[]
# # print "\n",has_mom,"tabs have a parent tab"
# # print "\nand",mom_has_url,"tabs have a parent tab with a labelled url"
# # print "\nwhich is",mom_has_url/float(has_mom)*100,"percent of tabs with parents"
# # print "\nand",mom_has_url/float(tabnum)*100,"percent of all tabs"
# print "\n Total tabs:",tabnum
# tmp_momurl_tot=[]
# for m in momurls:
# 	tmp_momurl_tot.append(momurls[m])
# tmp_momurl_tot.sort()
# momurl_median = tmp_momurl_tot[len(momurls)/2]
# for mm in momurls:
# 	if momurls[mm] > 500:#momurl_median:
# 		print "site:",mm,"//tabs spawned:",momurls[mm]
# # fh0 = open("spawn_sites.json","w")
# # fh0.write(json.dumps(momurls))
# # fh0.close()

# # for i in pids_by_spawn_sites:
# # 	print "*****",i,"*****"
# # 	for ii in pids_by_spawn_sites[i]:
# # 		print pids_by_spawn_sites[i][ii]
# # pp(pids_by_spawn_sites)
# for k in interesting_spawn_sites:
# 	print k,"makes up",round(interesting_spawn_sites[k]/float(tabnum))*100,"percent of tabs"
# fh=open("pids_per_spawn_site.json","w")
# fh.write(json.dumps(pids_by_spawn_sites))
# fh.close()

# usermat = json.load(open("usermat.json"))

# usermat = comparemailandnotmail(usermat,all_sites)

# fh=open("total_tabs_by_user.json","w")
# fh.write(json.dumps(mytotaltabs))
# fh.close()

# print "\n",tabnum

# # fh=open("all_lifespans.json","w")
# # fh.write(json.dumps(lifespans))
# # fh.close()

# # usermat = assignusertype(usermat,usertypes)
# # fh=open("usermat.json","w")
# # fh.write(json.dumps(usermat))
# # fh.close()

# comparemailandnotmail(usermat)


# for ut in uniqueusertypes:
