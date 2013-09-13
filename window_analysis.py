#!/usr/bin/env python
"""Generates statistics about window usage from the output of window_tracker.py
"""
import re
import sys
from collections import deque
from collections import defaultdict
from pprint import pprint as pp
try:
	import simplejson as json
except:
	import json

### Initialize ###
window_mat = {}

def five_point_data_summary(data):
	five_points={}
	sorted_data = sorted(data)
	# five_points['a_minimum'] = min(sorted_data)
	five_points['b_maximum'] = max(sorted_data)
	five_points['c_first_quartile'] = sorted_data[len(sorted_data)/4]
	five_points['d_second_quartile'] = sorted_data[len(sorted_data)/2]
	five_points['e_third_quartile']= sorted_data[len(sorted_data)*3/4]
	five_points['average'] = sum(sorted_data)/float(len(sorted_data))

	return five_points

for line in sys.stdin:
	win = json.loads(line)
	pid = win['pid']
	if pid not in window_mat:
		window_mat[pid] = {}
	window_mat[pid][win['window_id']] = win

for p in window_mat:
	for ii in window_mat[p]:
		window_mat[p][ii]['cohort'] = []


	for w in window_mat[p]:
		start = window_mat[p][w]['first_seen']
		end = window_mat[p][w]['last_seen']
		for ww in window_mat[p]:
			if start < window_mat[p][ww]['first_seen'] < end or start < window_mat[p][ww]['last_seen'] < end:
				window_mat[p][w]['cohort'].append(window_mat[p][ww]['window_id'])

#### Get five points per subject; also get five points over all subs
five_points_on_windows={}
tot_list_win_cohorts = []
for pers in window_mat:
	my_sum = []
	for co in window_mat[pers]:
		my_sum.append(len(window_mat[pers][co]['cohort']))
		tot_list_win_cohorts.append(len(window_mat[pers][co]['cohort']))
	five_points_on_windows[pers] = five_point_data_summary(my_sum)
overall_five_points = five_point_data_summary(tot_list_win_cohorts)
print "Overall Window Stats: Num Co-existing Windows"
for o in overall_five_points:
	print o,"=",overall_five_points[o]

#### Get num unique users with a given number of windows open at once
uniq_users_win_num = {}
for pp in window_mat:
	for i in window_mat[pp]:
		if len(window_mat[pp][i]['cohort']) not in uniq_users_win_num:
			uniq_users_win_num[len(window_mat[pp][i]['cohort'])] = {}
		uniq_users_win_num[len(window_mat[pp][i]['cohort'])][pp] = True
# for aa in uniq_users_win_num:
# 	print aa,len(uniq_users_win_num[aa])

#### Get a new five points feeding in the five point summary from every subject
a_col_of_numbers=[]
the_five_quant_touchstones=five_points_on_windows[five_points_on_windows.keys()[0]]
for k in the_five_quant_touchstones:
	print k,":"
	for j in five_points_on_windows:
		a_col_of_numbers.append(five_points_on_windows[j][k])
	new_five = five_point_data_summary(a_col_of_numbers)
	for i in new_five:
		print i,"=",new_five[i]



fh=open("window_list_per_pid.json","w")
fh.write(json.dumps(window_mat))
fh.close()