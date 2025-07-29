# -*- coding: utf-8 -*-

#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
#%% Import data and create data frame
world_yearly_fp = 'yearly_full_release_long_format.csv'
world = pd.read_csv(world_yearly_fp)

world.info()

#%% Initial pre-processing
# Drop unnecessary columns
world = world.drop(world.columns[[4,5,6,7,8,9,10]], axis=1)

# Filter data
 # Subsets for electricity demand
world_demand = world[(world['Area']=='World') & (world['Category']=='Electricity demand') & (world['Variable']=='Demand')]
us_demand = world[(world['Area']=='United States of America') & (world['Category']=='Electricity demand') & (world['Variable']=='Demand')]
eu_demand = world[(world['Area']=='EU') & (world['Category']=='Electricity demand') & (world['Variable']=='Demand') & (world['Year'] < 2024)]
china_demand = world[(world['Area']=='China') & (world['Category']=='Electricity demand') & (world['Variable']=='Demand')]
india_demand = world[(world['Area']=='India') & (world['Category']=='Electricity demand') & (world['Variable']=='Demand')]

 # Subset for electricity generation:
content_filter = (world['Category']=='Electricity generation') & ((world['Subcategory']=='Fuel') | (world['Subcategory']=='Total'))
world_gen_pct = world[content_filter & (world['Area'] == 'World') &  (world['Unit']=='%')]

#%% Visualize demand over time
sns.set_theme(style='whitegrid', palette='pastel')
fig, (ax1, ax2) = plt.subplots(2, sharex=True, figsize=(8,7))
ax1.plot(world_demand['Year'], world_demand['Value'], color='black', label='World', linewidth=3)
ax1.set_ylabel('Global Demand (TWh)', labelpad=10)
ax2.plot(us_demand['Year'], us_demand['Value'], linewidth=2.5, label='US')
ax2.plot(eu_demand['Year'], eu_demand['Value'], linewidth=2.5, label='EU')
ax2.plot(china_demand['Year'], china_demand['Value'], linewidth=2.5, label='China')
ax2.plot(india_demand['Year'], india_demand['Value'], linewidth=2.5, label='India')
ax2.set_ylabel('Nation or Bloc Demand (TWh)', labelpad=10)
ax1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
ax2.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
ax2.set_xlabel('Year')
fig.suptitle('Electricity Demand, 2000-2023', y=0.92)
fig.legend(loc='center right', bbox_to_anchor=(1.05,.52))
plt.subplots_adjust(wspace=0.1, hspace=0.1)
plt.show()

# Calculate relationship between endpoints for discussion
print(max(world_demand['Value'])/min(world_demand['Value']))
print(us_demand['Value'].iloc[-1]/us_demand['Value'].iloc[0])

#%% Visualize global demand as pie chart 
 # Use most recent 5 years of data and take average
recent_demand = world[(world['Year']>2018) & (world['Category']=='Electricity demand') & (world['Variable']=='Demand') & 
                      (world['Country code'].notnull())]
recent_avg_demand = recent_demand.groupby(['Area'])['Value'].mean()
recent_avg_demand = recent_avg_demand.to_frame(name='Demand')
# add per capita demand as an option
recent_avg_demand['PerCapita'] = world[(world['Year']>2018) & (world['Category']=='Electricity demand') & 
                                       (world['Variable']=='Demand per capita')].groupby(['Area'])['Value'].mean()

top5_dmnd = recent_avg_demand.sort_values(by='Demand', ascending=False).head(5)
print(top5_dmnd)
rest_of_world_dmnd = recent_avg_demand.drop(list(top5_dmnd.index)).sum()

 
values = [top5_dmnd['Demand'].iloc[x] for x in range(0,5)]
values.append(rest_of_world_dmnd['Demand'])

labels = list(top5_dmnd.index)
labels.append('Rest of World')
labels[1] = 'United States'
labels[3] = 'Russia'

sns.color_palette("ch:start=.2,rot=-.3")
sns.set_theme(style='whitegrid', palette='pastel')
colors = ['red', 'blue', 'orange', 'darkslategrey', 'whitesmoke', 'lightgrey']
fig, ax = plt.subplots(figsize=(8,6))
ax.pie(values, labels=labels, autopct='%1.1f%%', pctdistance=0.65, labeldistance=1.1, textprops={'fontsize': 11}, radius=1)
plt.title('Average Electricity Demand from 2018-2023 \n as Share of Global Demand', y=0.94)
plt.show()

#%% Create filters to view breakdown of fuel sources for world and US
world_pct = world[(world['Area']=='World') & (world['Category']=='Electricity generation') 
                  & (world['Subcategory']=='Fuel') & (world['Unit']=='%')]

bioenergy = world_pct['Variable'] == 'Bioenergy'
coal = world_pct['Variable'] == 'Coal'
gas = world_pct['Variable'] == 'Gas'
hydro = world_pct['Variable'] == 'Hydro'
nuclear = world_pct['Variable'] == 'Nuclear'
other_fossil = world_pct['Variable'] == 'Other Fossil'
other_renew = world_pct['Variable'] == 'Other Renewables'
solar = world_pct['Variable'] == 'Solar'
wind = world_pct['Variable'] == 'Wind'

# repeat for US
us_pct = world[(world['Area']=='United States of America') & (world['Category']=='Electricity generation') 
               & (world['Subcategory']=='Fuel') & (world['Unit']=='%')]
u_bioenergy = us_pct['Variable'] == 'Bioenergy'
u_coal = us_pct['Variable'] == 'Coal'
u_gas = us_pct['Variable'] == 'Gas'
u_hydro = us_pct['Variable'] == 'Hydro'
u_nuclear = us_pct['Variable'] == 'Nuclear'
u_other_fossil = us_pct['Variable'] == 'Other Fossil'
u_other_renew = us_pct['Variable'] == 'Other Renewables'
u_solar = us_pct['Variable'] == 'Solar'
u_wind = us_pct['Variable'] == 'Wind' 


#%% Examine global electricity distribution over time
years = world_pct['Year'].unique()
y_list = []
variables = [coal, gas, other_fossil, nuclear, bioenergy, hydro, solar, wind, other_renew]
for var in variables:
    y_list.append(world_pct[var]['Value'])
y1, y2, y3, y4, y5, y6, y7, y8, y9 = np.array(y_list)

yrs_us = us_pct['Year'].unique()
u_list = []
u_variables = [u_coal, u_gas, u_other_fossil, u_nuclear, u_bioenergy, u_hydro, u_solar, u_wind, u_other_renew]
for u_var in u_variables:
    u_list.append(us_pct[u_var]['Value'])
u1, u2, u3, u4, u5, u6, u7, u8, u9 = np.array(u_list)

# check that quantities are accurate and correspond to order of variables!
fig, (ax1, ax2) = plt.subplots(1,2, sharey=True, figsize=(10,7))
ax1.bar(years, y1, label='Coal', color='dimgrey')
ax1.bar(years, y2, bottom=y1, label='Natural Gas', color='darkgrey')
ax1.bar(years, y3, bottom=(y1+y2), label='Other Fossil Fuels', color='lightgrey')
ax1.bar(years, y4, bottom=(y1+y2+y3), label='Nuclear')
ax1.bar(years, y5, bottom=(y1+y2+y3+y4), label='Bioenergy')
ax1.bar(years, y6, bottom=(y1+y2+y3+y4+y5), label='Hydroelectric')
ax1.bar(years, y7, bottom=(y1+y2+y3+y4+y5+y6), label='Solar')
ax1.bar(years, y8, bottom=(y1+y2+y3+y4+y5+y6+y7), label='Wind')
ax1.bar(years, y9, bottom=(y1+y2+y3+y4+y5+y6+y7+y8), label='Other Renewables')

ax2.bar(yrs_us, u1, label='Coal', color='dimgrey')
ax2.bar(yrs_us, u2, bottom=u1, label='Natural Gas', color='darkgrey')
ax2.bar(yrs_us, u3, bottom=(u1+u2), label='Other Fossil Fuels', color='lightgrey')
ax2.bar(yrs_us, u4, bottom=(u1+u2+u3), label='Nuclear')
ax2.bar(yrs_us, u5, bottom=(u1+u2+u3+u4), label='Bioenergy')
ax2.bar(yrs_us, u6, bottom=(u1+u2+u3+u4+u5), label='Hydroelectric')
ax2.bar(yrs_us, u7, bottom=(u1+u2+u3+u4+u5+u6), label='Solar')
ax2.bar(yrs_us, u8, bottom=(u1+u2+u3+u4+u5+u6+u7), label='Wind')
ax2.bar(yrs_us, u9, bottom=(u1+u2+u3+u4+u5+u6+u7+u8), label='Other Renewables')

ax1.set_xlabel('Year')
ax1.set_ylabel('Percent of Electricity Generation')
ax1.set_title('World')
ax1.set_ylim(0, 103)
ax2.set_xlabel('Year')
ax2.set_title('United States')
plt.subplots_adjust(wspace=0.03, hspace=0.05)
plt.legend(ncol=3, bbox_to_anchor=(0.7, -0.105))
plt.suptitle('Fuels for Electricity Generation Worldwide and in the US, 2000-2023')
plt.show()

#%% Closer look at US from 2016 - 2022
us = world[(world['Area']=='United States of America') & (world['Category']=='Electricity generation') 
               & (world['Subcategory']=='Fuel')]
yr_filter = (us['Year'] > 2014) & (us['Year'] < 2024)
us_t1_pct = us[yr_filter & (us['Unit']=='%')]
us_t1_twh = us[yr_filter & (us['Unit']=='TWh')]
t1_yrs = us_t1_twh['Year'].unique()

# Create figure for renewables
fig, (ax1, ax2) = plt.subplots(2, sharex=True, figsize=(8,7))

ax1.plot(t1_yrs, us_t1_pct[us_t1_pct['Variable']=='Hydro']['Value'], 
         color='C2', linewidth=2.5, label='Hydroelectric')
ax1.plot(t1_yrs, us_t1_pct[us_t1_pct['Variable']=='Solar']['Value'], 
         color='C3', linewidth=2.5, label='Solar')
ax1.plot(t1_yrs, us_t1_pct[us_t1_pct['Variable']=='Wind']['Value'], 
         color='C4', linewidth=2.5, label='Wind')
#plt.plot(t1_yrs, us_t1_pct[us_t1_pct['Variable']=='Bioenergy']['Value'], label='Bioenergy')
#plt.plot(t1_yrs, us_t1_pct[us_t1_pct['Variable']=='Other Renewables']['Value'], label='Other Renewables')
# ^ Bioenergy and Other Renewables are mostly constant and have small shares so they are not shown to simplify the figure
ax1.axvline(x=2017, color='dimgrey', linestyle='--')
ax1.axvline(x=2021, color='dimgrey', linestyle='--')
ax1.set_ylabel('% of US Electricity Generation')

ax2.plot(t1_yrs, us_t1_twh[us_t1_twh['Variable']=='Hydro']['YoY % change'], 
         color='C2', linewidth=2.5, label='Hydroelectric')
ax2.plot(t1_yrs, us_t1_twh[us_t1_twh['Variable']=='Solar']['YoY % change'],
         color='C3', linewidth=2.5, label='Solar')
ax2.plot(t1_yrs, us_t1_twh[us_t1_twh['Variable']=='Wind']['YoY % change'], 
         color='C4', linewidth=2.5, label='Wind')
ax2.set_xlabel('Year')
ax2.set_ylabel('Year-over-Year % Change')
ax2.axvline(x=2017, color='dimgrey', linestyle='--')
ax2.axvline(x=2021, color='dimgrey', linestyle='--')
ax2.legend(ncol = 3, bbox_to_anchor=(0.195, 1.01))

ax1.set_title('Renewables for Electricity Generation in the US, 2015-2023')
plt.show()

#%% Repeat for fossil fuels
fig, (ax1, ax2) = plt.subplots(2, sharex=True, figsize=(8,7))

ax1.plot(t1_yrs, us_t1_pct[us_t1_pct['Variable']=='Coal']['Value'], 
          linewidth=2.5, label='Coal')
ax1.plot(t1_yrs, us_t1_pct[us_t1_pct['Variable']=='Gas']['Value'], 
         linewidth=2.5, label='Natural Gas')
ax1.plot(t1_yrs, us_t1_pct[us_t1_pct['Variable']=='Other Fossil']['Value'], 
         color='C9', linewidth=2.5, label='Other Fossil Fuels')
#plt.plot(t1_yrs, us_t1_pct[us_t1_pct['Variable']=='Bioenergy']['Value'], label='Bioenergy')
#plt.plot(t1_yrs, us_t1_pct[us_t1_pct['Variable']=='Other Renewables']['Value'], label='Other Renewables')
# ^ Bioenergy and Other Renewables are mostly constant and have small shares so they are not shown to simplify the figure
ax1.axvline(x=2017, color='dimgrey', linestyle='--')
ax1.axvline(x=2021, color='dimgrey', linestyle='--')
ax1.set_ylabel('% of US Electricity Generation')

ax2.plot(t1_yrs, us_t1_twh[us_t1_twh['Variable']=='Coal']['YoY % change'], 
         linewidth=2.5, label='Coal')
ax2.plot(t1_yrs, us_t1_twh[us_t1_twh['Variable']=='Gas']['YoY % change'],
          linewidth=2.5, label='Natural Gas')
ax2.plot(t1_yrs, us_t1_twh[us_t1_twh['Variable']=='Other Fossil']['YoY % change'], 
         color='C9', linewidth=2.5, label='Other Fossil Fuels')
ax2.set_xlabel('Year')
ax2.set_ylabel('Year-over-Year % Change')
ax2.axvline(x=2017, color='dimgrey', linestyle='--')
ax2.axvline(x=2021, color='dimgrey', linestyle='--')
ax2.legend(ncol = 3, bbox_to_anchor=(0.138, 1.01))

ax1.set_title('Fossil Fuels for Electricity Generation in the US, 2016-2022')
plt.show()

#%% Look at hydro generation for story detail
us_hydro = us[(us['Unit']=='TWh') & (us['Variable']=='Hydro')]
us_hydro.plot('Year', 'Value')
us_hydro['Value'].mean()






















