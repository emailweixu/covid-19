import pycurl
import certifi
from io import BytesIO

buffer = BytesIO()
c = pycurl.Curl()
c.setopt(c.URL, 'https://covidtracking.com/api/states/daily')
c.setopt(c.WRITEDATA, buffer)
c.setopt(c.CAINFO, certifi.where())
c.perform()
c.close()

body = buffer.getvalue()

# process data
import json
data = json.loads(body.decode('utf-8'))
table = {}
dates = set()
for item in data:
  state = item['state']
  date = item['date']
  if state not in table:
    table[state] = {}
  table[state][date] = item
  dates.add(date)
dates = sorted(dates)

# state population
# from https://www2.census.gov/programs-surveys/popest/tables/2010-2019/state/totals/nst-est2019-01.xlsx
state_population_raw = '4903185 AL,731545 AK,7278717 AZ,3017804 AR,39512223 CA,5758736 CO,3565287 CT,973764 DE,705749 DC,21477737 FL,10617423 GA,1415872 HI,1787065 ID,12671821 IL,6732219 IN,3155070 IA,2913314 KS,4467673 KY,4648794 LA,1344212 ME,6045680 MD,6892503 MA,9986857 MI,5639632 MN,2976149 MS,6137428 MO,1068778 MT,1934408 NE,3080156 NV,1359711 NH,8882190 NJ,2096829 NM,19453561 NY,10488084 NC,762062 ND,11689100 OH,3956971 OK,4217737 OR,12801989 PA,1059361 RI,5148714 SC,884659 SD,6829174 TN,28995881 TX,3205958 UT,623989 VT,8535519 VA,7614893 WA,1792147 WV,5822434 WI,578759 WY'
state_population = {}
for item in state_population_raw.split(','):
  population, state = item.split()
  state_population[state] = int(population)

import random
import datetime

date = dates[-1]
prev_date= dates[-2]

stat = {}
stat2 = {}
for state in table.keys():
  pos = table[state][date]['positive']
  neg = table[state][date]['negative']
  if not pos:
    pos = 0
  if not neg:
    neg = 0

  pos_rate = pos / (pos + neg + 1e-30)
  prev_pos = table[state][prev_date]['positive']
  prev_neg = table[state][prev_date]['negative']
  if not prev_pos:
    prev_pos = 0
  if not prev_neg:
    prev_neg = 0
  new_pos = pos - prev_pos
  new_neg = neg - prev_neg
  new_pos_rate = new_pos / (new_pos + new_neg + 1e-30)
  if state in state_population:
    pos_per_1M = pos / state_population[state] * 1000000
  else:
    pos_per_1M = 0
  msg = "%-5s %5d %6.0f %5d %8.1f" % (state, pos, pos_per_1M, new_pos, 100*pos_rate)
  stat[pos + random.random()] = msg
  stat2[pos_per_1M + random.random()] = msg

# print table
print ("date: ", date)
print ("total: total number of positives")
print ("per_1M: number of positives per 1M population")
print ("new: new positives on %s" % date)
print ("pos_rate: #positives/(#positives + #negatives)")
print ("test data is from https://covidtracking.com/api/states/daily")
print ("population date is from https://www2.census.gov/programs-surveys/popest/tables/2010-2019/state/totals/nst-est2019-01.xlsx")
print ()
print ("state total per_1M   new pos_rate")
for _, msg in sorted(stat2.items(), reverse=True):
  print(msg)
  
