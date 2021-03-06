import argparse
import os
import json
import numpy as np

#in the cls json file, 2 represent company name
inputpath='../../results/personnel-records/1954/cls/firm/'
clean_names = lambda x: [i for i in x if i[0] != '.']
count=0
for dir in sorted(clean_names(os.listdir(inputpath))):  #one dir includes prob for one page
    print("processing "+dir)
    with open(os.path.join(inputpath,dir)) as jsonfile:
        cls = json.load(jsonfile)
    cls=cls['id']
    for i in range(len(cls)):
        if i==0 and cls[i]==1:
            count+=1
        elif cls[i]==1 and cls[max(i-1,0)]!=1:
            count+=1
print(count)