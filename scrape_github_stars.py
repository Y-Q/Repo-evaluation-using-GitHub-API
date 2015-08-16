# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 11:31:51 2015

@author: NancyLi
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib


# get star history

repo_list = [('druid-io','druid'), ('apache','kafka'), ('apache','storm'), ('amplab','tachyon'), ('apache','spark'), ('docker','docker'), ('mbostock','d3'),('apache','mesos'),('apache','samza')]

star_history_dict = {}
monthly_star_total = {}

for user, repo in repo_list:
    star_history_dict[repo] = star_history_list(user, repo)
    monthly_star_total[repo] = star_monthly_list(star_history_dict[repo])

# save github data to cvs

for key in star_history_dict:
    star_history_dict[key].to_csv('star_history_'+ key + '.csv')

# plots
repo_list = [('druid-io','druid'), ('apache','kafka'), ('amplab','tachyon'), ('apache','mesos')]
color=iter(plt.cm.rainbow(np.linspace(0,1,len(repo_list))))
for item in repo_list:    
    c=next(color)   
    plt.plot(monthly_star_total[item[1]].index,monthly_star_total[item[1]], c=c)
plt.legend([item[1] for item in repo_list])
plt.xticks(rotation=70)
plt.ylabel('Total # of stars', fontsize = 14)
plt.xlabel('Date of observation', fontsize = 14)
plt.title('Comparison of # of stars', fontsize = 18)

color=iter(plt.cm.rainbow(np.linspace(0,1,len(repo_list))))
for item in repo_list:    
    c=next(color)
    plt.plot(range(1,len(monthly_star_total[item[1]])+1),monthly_star_total[item[1]], c=c)
plt.legend([item[1] for item in repo_list])
plt.ylabel('Total # of stars', fontsize = 14)
plt.xlabel('# of month since the beginning of repo', fontsize = 14)
plt.title('Comparison of # of stars', fontsize = 18)

### FUNCTIONS ----------------------------------------------------------------------------

def star_history_list(user, repo):

    url = 'https://api.github.com/repos/'+ user +'/' + repo +'/stargazers'
    headers = {'Accept': 'application/vnd.github.v3.star+json'}
    user_name, password = 'Y-Q', 'totallynotmypassword'
    per_page_num = 100
    r = requests.get(url, auth=(user_name,password), headers = headers, params= {'per_page':per_page_num})

    # parse the total page number
    if 'link' in r.headers.keys(): 
        link = r.headers['link']
        index1, index2 = link[::-1].find('=egap'),link.find('>; rel="last"')
        total_pages = int(link[-index1:index2])
    else:
        total_pages = 1        
    
    # iterate through pages to record data of interests    
    rows = []
    for page_num in range(1, total_pages + 1):
        params_page = {'per_page':per_page_num, 'page':page_num}    
        response_list = requests.get(url, auth=(user_name,password), headers = headers, params=params_page).json()
        
        for response in response_list:
            rows.append([response['starred_at']] + [response['user']['login']])
            
    star_history_list = pd.DataFrame(rows, columns = ['timestamp','user'])
     
    return star_history_list


def star_monthly_list(star_list):
    # aggregate number of new stars by month 

    star_list['timestamp'] = [datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ' ) for date in star_list['timestamp']]
    star_list['year'] = [date.year for date in star_list['timestamp']]
    star_list['month'] = [date.month for date in star_list['timestamp']]
    star_growth = np.cumsum(np.array(star_list.groupby(['year', 'month']).count()['user']),axis = 0)

    startDate = (np.min(star_list['timestamp'])).date()
    monthly_dates = pd.date_range(start=startDate,periods=len(star_growth), freq="m")
    
    star_monthly_list = pd.DataFrame(star_growth, index=monthly_dates, columns=['star_growth'])

    return star_monthly_list

