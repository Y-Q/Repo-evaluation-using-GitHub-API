# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 12:28:53 2015

@author: NancyLi
"""


import requests
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


# get star history

repo_list = [('druid-io','druid'), ('apache','kafka'), ('apache','storm'), ('amplab','tachyon'), ('apache','spark'), ('docker','docker'), ('mbostock','d3'),('apache','mesos'),('apache','samza')]

commit_history_dict = {}
contributor_history_dict = {}
commit_monthly_dict = {}
contributor_monthly_dict = {}

for user, repo in repo_list:
    commit_history_dict[repo],contributor_history_dict[repo]  = commit_history_list(user, repo)
    if not commit_history_dict[repo].empty:
        commit_monthly_dict[repo] = commit_monthly_list(commit_history_dict[repo])
    else:
        commit_monthly_dict[repo] = []
    commit_monthly_dict[repo]['code_activity'] = commit_monthly_dict[repo]['addition'] + commit_monthly_dict[repo]['deletion']
    
    if not contributor_history_dict[repo].empty:
        contributor_monthly_dict[repo] = contributor_monthly_list(contributor_history_dict[repo])
    else:
        contributor_monthly_dict[repo] = []
    
    
# save github data to cvs

for key in commit_history_dict:
    commit_history_dict[key].to_csv('commit_history_'+ key + '.csv')

# plots
color=iter(plt.cm.rainbow(np.linspace(0,1,len(repo_list))))
for item in repo_list:    
    c=next(color)
    plt.plot(commit_monthly_dict[item[1]].index,commit_monthly_dict[item[1]]['code_activity'], c=c)
plt.legend([item[1] for item in repo_list])
plt.ylabel('Code activity', fontsize = 14)
plt.xlabel('Date of observation', fontsize = 14)
plt.title('Comparison of code activities', fontsize = 18)

# commit history plot
repo_list = [('druid-io','druid'), ('apache','kafka'), ('apache','storm'), ('amplab','tachyon'), ('apache','spark'), ('docker','docker'), ('mbostock','d3'),('apache','samza')]
color=iter(plt.cm.rainbow(np.linspace(0,1,len(repo_list))))
for item in repo_list:    
    c=next(color)
    plt.plot(range(1,len(commit_monthly_dict[item[1]])+1),commit_monthly_dict[item[1]]['commits'], c=c)
plt.legend([item[1] for item in repo_list])
plt.ylabel('Total # of commits', fontsize = 14)
plt.xlabel('# of month since the beginning of repo', fontsize = 14)
plt.title('Comparison of # of commits', fontsize = 18)

# code activity history plot

color=iter(plt.cm.rainbow(np.linspace(0,1,len(repo_list))))
for item in repo_list:    
    c=next(color)
    plt.plot(range(1,len(commit_monthly_dict[item[1]])+1),commit_monthly_dict[item[1]]['code_activity'], c=c)
plt.legend([item[1] for item in repo_list])
plt.ylabel('Code activity', fontsize = 14)
plt.xlabel('# of month since the beginning of repo', fontsize = 14)
plt.title('Comparison of code activities', fontsize = 18)


# contributor history plot

color=iter(plt.cm.rainbow(np.linspace(0,1,len(repo_list))))
for item in repo_list:    
    c=next(color)
    plt.plot(range(1,len(contributor_monthly_dict[item[1]])+1),contributor_monthly_dict[item[1]]['contributors'], c=c)
plt.legend([item[1] for item in repo_list])
plt.ylabel('# of contributors', fontsize = 14)
plt.xlabel('# of month since the beginning of repo', fontsize = 14)
plt.title('Comparison of contributor growth', fontsize = 18)

### FUNCTIONS ----------------------------------------------------------------------------

def commit_history_list(user, repo):
    
    url = 'https://api.github.com/repos/'+ user +'/' + repo +'/stats/contributors'
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
    rows_total = []
    for page_num in range(1, total_pages + 1):
        params_page = {'per_page':per_page_num, 'page':page_num}    
        response_list = requests.get(url, auth=(user_name,password), headers = headers, params=params_page).json()
        
        for response in response_list:
            if_state = True                            
            for item in response['weeks']:                
                rows.append([item['w']] + [item['c']] + [item['a']] + [item['d']])
                if (((item['c'] + item['a'] + item['d']) > 0) & if_state):
                    rows_total.append([response['author']['login']] + [response['total']] + [item['w']])
                    if_state = False
                
    contributor_history_list = pd.DataFrame(rows_total, columns = ['contributor','total_commits','first_time'])                
    commit_history_list = pd.DataFrame(rows, columns = ['timestamp','commits','addition','deletion'])
     
    return (commit_history_list, contributor_history_list)


def commit_monthly_list(df):
    # aggregate number of new stars by month 

    df['timestamp1'] = [datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d %H:%M:%S') for date in df['timestamp']]
    df['timestamp2'] = [datetime.strptime(date, '%Y-%m-%d %H:%M:%S' ) for date in df['timestamp1']]    
    df['year'] = [date.year for date in df['timestamp2']]
    df['month'] = [date.month for date in df['timestamp2']]
    growth = np.cumsum(np.array(df.groupby(['year', 'month'])[['commits','addition','deletion']].sum()),axis = 0)

    startDate = (np.min(df['timestamp2'])).date()
    monthly_dates = pd.date_range(start=startDate,periods=len(growth), freq="m")
    
    commit_monthly_list = pd.DataFrame(growth, index=monthly_dates, columns=['commits','addition','deletion'])

    return commit_monthly_list    


def contributor_monthly_list(df):
    # aggregate number of new stars by month 

    df['timestamp1'] = [datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d %H:%M:%S') for date in df['first_time']]
    df['timestamp2'] = [datetime.strptime(date, '%Y-%m-%d %H:%M:%S' ) for date in df['timestamp1']]    
    df['year'] = [date.year for date in df['timestamp2']]
    df['month'] = [date.month for date in df['timestamp2']]
    growth = np.cumsum(np.array(df.groupby(['year', 'month'])['contributor'].count()),axis = 0)

    startDate = (np.min(df['timestamp2'])).date()
    monthly_dates = pd.date_range(start=startDate,periods=len(growth), freq="m")
    
    contributor_monthly_list = pd.DataFrame(growth, index=monthly_dates, columns=['contributors'])

    return contributor_monthly_list  