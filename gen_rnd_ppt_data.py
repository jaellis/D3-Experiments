import random
import time as t
import math
import json
import datetime as dt

data=[];
for i in range(5000):
	time = t.time();
#	time2 = dt.datetime.now();
	mix = random.random();
	data.append([math.floor(time*mix),random.randint(1,100)])

#data=sorted(data,key=int);
out = open("rnd_ppt_scatter.json",'w')
out.write(json.dumps(data))
out.close()
