import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import os
import re

from functools import reduce

import folium

import datetime

import streamlit as st
from streamlit_folium import st_folium

title_text = "Analysis: Polution in the Air of Beijing"
st.title(title_text)

st.markdown(
    """
    ## About me
    Hello! Welcome to my dashboard. My name is Hafizh, a final-year student from Institut Teknologi Bandung and I\'m currently taking Bangkit Academy program.
    
    In this page, you will find my analysis about the air quality data recorded by monitoring stations in Beijing. Let's get to work!
    """
)

st.markdown(
    """
    ## About the dataset
    I'm using the dataset given by Dicoding Team, which is provided by UCI Machine Learning Repository and can be accessed [here](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data). The dataset contains few CSV file, each filled with the recorded data from different monitoring sites. Below are the variables for every CSV file:
    1. `No`: indicates the row number.
    2. `year`: year of the data in its corresponding row
    3. `month`: month of the data in its corresponding row
    4. `hour`: hour of the data in its corresponding row
    5. `PM2.5`: PM2.5 concentration (μg/m^3)
    6. `PM10`: PM10 concentration (μg/m^3)
    7. `SO2`: SO2 concentration (μg/m^3)
    8. `NO2`: NO2 concentration (μg/m^3)
    9. `CO`: CO concentration (μg/m^3)
    10. `O3`: O3 concentration (μg/m^3)
    11. `TEMP`: temperature (degree Celsius) 
    12. `PRES`: pressure (hPa)
    13. `DEWP`: dew point temperature (°C)
    14. `RAIN`: precipitation (mm)
    15. `wd`: wind direction
    16. `WSPM`: wind speed (m/s)
    17. `station`: the name of the air-quality monitoring site
    We will classify variable 5 to 10 as 'pollutant concentration' and variable 11 to 16 as 'meteorological parameters'.
    """
)

st.markdown(
    """
    ## What are we gonna be looking at?
    Upon inspecting the dataset, I proposed two questions:
    1. How do the trends of average concentration changes for major pollutants (PM2.5, PM10, NO2, CO, SO2, and O3) in Beijing vary monthly from 2013 to 2017?
    2. What is the relationship between the pollutant PM10 and meteorological parameters in Beijing from 2013 to 2017?
    So let's answer those question!
    """
)

st.markdown(
    """
    ## Analysis
    ### Process
    Well, in this dashboard, I will mostly present the result. You can find the complete Jupyter Notebook for the full data analysis in my repository.
    
    ### Result
    For the first question, I averaged the value of all the data from each monitoring station. After that, we can generate a time-series plot for each pollutant as follow:
    """
)

tabFull, tabFullWithoutCO, tabEach = st.tabs(["Combined Plot", "Combined Plot without O3", "Separated Plot"])

###############################################################
# Import data gabungan
merged_df = pd.read_csv("main_data.csv")

# Rekap kolom polutan
polutan_col = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']

# Dapatkan kolom datetime
merged_df['datetime'] = pd.to_datetime(merged_df[['year','month','day']])
merged_df['month_year'] = merged_df['datetime'].dt.to_period('M').dt.to_timestamp()

# Lakukan pivoting pada merged_df terhadap datetime untuk mendapatkan rata-rata konsentrasi polutan dari seluruh station di Beijing
merged_df_avg_station = merged_df.groupby('datetime')[polutan_col].mean().reset_index()

# Buat kolom untuk menyatakan bulan dan tahun
merged_df_avg_station['month_year'] = merged_df_avg_station['datetime'].dt.to_period('M')

# Lakukan pivoting terhadap dataframe hasil pivoting sebelumnya terhadap kolom bulan-tahun
merged_df_avg_month = merged_df_avg_station.groupby('month_year')[polutan_col].mean().reset_index()
merged_df_avg_month['month_year'] = merged_df_avg_month['month_year'].dt.to_timestamp()

# Lakukan melt untuk 'unpivot' dataframe
merged_df_avg_month_melted = merged_df_avg_month.melt(id_vars='month_year', value_vars=polutan_col, 
                               var_name='Pollutant', value_name='Average Concentration')
###############################################################

###############################################################
fig1 = plt.figure(figsize=(12, 6))
ax1 = fig1.add_subplot(111)

sns.lineplot(data=merged_df_avg_month_melted, x='month_year', y='Average Concentration', hue='Pollutant', marker='o', ax=ax1)

ax1.set_aspect('auto')
ax1.set_xlim(left=merged_df_avg_station['month_year'].min(), right=merged_df_avg_station['month_year'].max()-1)
ax1.set_ylim(top=3000)

ax1.set_xlabel('Time (Monthly)', fontsize=12)
ax1.set_ylabel('Average Concentration ($\mu$g/$\mathregular{m}^3$)', fontsize=12)

ax1.set_title('Monthly Average Pollutant Concentration Trends Across Stations', fontsize=14)

plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)

ax1.grid(True,linewidth=0.5)

plt.tight_layout()
###############################################################

with tabFull:
    st.pyplot(fig1)

###############################################################
fig2 = plt.figure(figsize=(12, 6))
ax2 = fig2.add_subplot(111)

sns.lineplot(data=merged_df_avg_month_melted.loc[merged_df_avg_month_melted["Pollutant"]!="CO"], x='month_year', y='Average Concentration', hue='Pollutant', marker='o', ax=ax2)

ax2.set_aspect('auto')
ax2.set_xlim(left=merged_df_avg_station['month_year'].min(), right=merged_df_avg_station['month_year'].max()-1)
ax2.set_ylim(top=200)

ax2.set_xlabel('Time (Monthly)', fontsize=12)
ax2.set_ylabel('Average Concentration ($\mu$g/$\mathregular{m}^3$)', fontsize=12)

ax2.set_title('Monthly Average Pollutant Concentration Trends Across Stations', fontsize=14)

plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)

ax2.grid(True,linewidth=0.5)

plt.tight_layout()
###############################################################

with tabFullWithoutCO:
    st.pyplot(fig2)

###############################################################
fig3, axes3 = plt.subplots(len(polutan_col), 1, figsize=(12, len(polutan_col) * 2.5), sharex=True)

for i, polutan in enumerate(polutan_col):
    polutan_df = merged_df_avg_month_melted[merged_df_avg_month_melted['Pollutant'] == polutan]

    sns.lineplot(data=polutan_df, x='month_year', y='Average Concentration', marker='o', ax=axes3[i])
    axes3[i].set_title(f'Monthly Average Concentration of {polutan}', fontsize=14)
    
    axes3[i].set_ylabel('Concen. ($\mu$g/$\mathregular{m}^3$)', fontsize=12)
    
    axes3[i].grid(True)
    
    axes3[i].set_xlim(left=polutan_df['month_year'].min(), right=polutan_df['month_year'].max())

axes3[-1].set_xlabel('Time (Monthly)', fontsize=12)

plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)

ax1.grid(True,linewidth=0.5)

plt.tight_layout()
###############################################################

with tabEach:
    st.pyplot(fig3)

st.markdown(
    """
    There are few trends that we can infer.
    1. Every month over the years, every pollutant except SO2 neither increases nor decreases; a fluctuating pattern is observed with an estimated trendline that remains fairly flat. For the pollutant SO2, there is a negative-gradient trend could be observed.
    2. Each pollutant fluctuates with relatively similar periods. For O3, it reaches a 'peak' when other variables reach a 'valley', and vice versa.
    """
)

st.markdown(
    """
    For the second question, I'm using Pearson correlation value to assess the relationship between pollutant PM10 and meteorological parameters.
    """
)

###############################################################
# Catat kolom yang akan dicek korelasi
included_col = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3", "TEMP", "PRES", "DEWP", "RAIN", "WSPM"]
corr_mat = merged_df[included_col].corr()

# Lakukan plot dengan seaborn
fig4 = plt.figure(figsize=(12, 6))
ax4 = fig4.add_subplot(111)

sns.heatmap(corr_mat, annot=True, cmap='coolwarm', fmt='.2f', square=True, ax=ax4)

plt.xticks(rotation=45)
plt.yticks(rotation=45)
###############################################################

st.pyplot(fig4)

st.markdown(
    """
    From the correlation matrix hitmap, it can be seen that PM10 concentration does not have a significant relationship with meteorological variables, namely temperature (TEMP), air pressure (PRES), dew point temperature (DEWP), rainfall (RAIN), and wind speed (WSPM). This is indicated by the low Pearson correlation coefficients between the concentration of PM10 and these variables. The highest absolute value of the correlation coefficient is only 0.18 (between PM10 concentration and wind speed).
    """
)

st.markdown(
    """
    ## Conclusion
    That's the end of my analysis. The answers to our previous two questions have been explained in the previous sections. Now, what about you try it yourself?
    
    ## Extras
    I provides an interactive plot for you to play with. Enjoy!
    
    ### Interactive Line Plot
    """
)

timesample = st.selectbox(
    label="Select time sample period",
    options=('Yearly', 'Monthly', 'Daily', 'Hourly')
)

station_select = st.selectbox(
    label="Select monitoring station",
    options=tuple(merged_df['station'].unique())
)

begin_date_select = st.date_input(label='Select start date', min_value=datetime.date(2013, 3, 1), max_value=datetime.date(2017, 2, 28), value=datetime.date(2013, 3, 1))
begin_hour_select = st.time_input("Select hour in the start date", step=3600, value=datetime.time(0,0))

begin_datetime_select = datetime.datetime.combine(begin_date_select, begin_hour_select)

end_date_select = st.date_input(label='Select end date', min_value=begin_date_select, max_value=datetime.date(2017, 2, 28), value=datetime.date(2017, 2, 28))
end_hour_select = st.time_input("Select hour in the end date", step=3600, value=datetime.time(0,0))

end_datetime_select = datetime.datetime.combine(end_date_select, end_hour_select)

polutan_choice = list(st.multiselect(
    label="Select pollutants",
    options=tuple(polutan_col),
    default=tuple(polutan_col)
))

#####################################################
# Dapatkan kolom datetime yang disertai jam
merged_df['datetime-hour'] = merged_df.apply(
    lambda row: datetime.datetime.combine(row['datetime'].date(), datetime.time(row['hour'], 0)), axis=1
)

# Filter sesuai start dan end date-hour
filtered_df = merged_df.loc[(merged_df['datetime-hour']>=begin_datetime_select) & (merged_df['datetime-hour']<=end_datetime_select)]

# Dictionary input dengan nama kolom
filtered_sample = {'Yearly':'year', 'Monthly':'month_year', 'Daily':'datetime', 'Hourly':'hour'}

# Lakikan pivot terhadap nama kolom sampling
filtered_df_pivot = filtered_df.groupby(filtered_sample[timesample])[polutan_choice].mean().reset_index()

# Lakukan melt untuk 'unpivot'
filtered_df_melted = filtered_df_pivot.melt(id_vars=filtered_sample[timesample], value_vars=polutan_choice, 
                            var_name='Pollutant', value_name='Concentration')

fig5 = plt.figure(figsize=(12, 6))
ax5 = fig5.add_subplot(111)

sns.lineplot(data=filtered_df_melted, x=filtered_sample[timesample], y='Concentration', hue='Pollutant', marker='o', ax=ax5)

ax5.set_aspect('auto')
ax5.set_xlim(left=filtered_df_pivot[filtered_sample[timesample]].min(), right=filtered_df_pivot[filtered_sample[timesample]].max())

ax5.set_xlabel(f'Time ({timesample})', fontsize=12)
ax5.set_ylabel('Average Concentration ($\mu$g/$\mathregular{m}^3$)', fontsize=12)

ax5.set_title(f'{timesample} {"Average" if timesample!="Hourly" else ""} Pollutant Concentration, Detected by {station_select} Station', fontsize=14)

plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)

ax5.grid(True,linewidth=0.5)

st.pyplot(fig5)

#####################################################

st.markdown(
    """
    ### Map with Annotation
    """
)

date_choice = datetime.datetime.combine(st.date_input(label='What date?', min_value=datetime.date(2013, 3, 1), max_value=datetime.date(2017, 2, 28)), datetime.datetime.min.time())
hour_choice = st.time_input("What time?", step=3600).hour
pollutant_choice = str(st.selectbox(
    label="What's the pollutant?",
    options=tuple(polutan_col)
))

#####################################################
def getAnnotationColor(polutan, konsentrasi):
    # Lakukan conditional yang terpisah karena tiap polutan memiliki persyaratan interim yang berbeda
    if polutan == 'PM2.5':
        if konsentrasi >= 75:
            color = 'darkpurple'
        elif konsentrasi >= 50:
            color = 'darkred'
        elif konsentrasi >= 37.5:
            color = 'red'
        elif konsentrasi >= 25:
            color = 'orange'
        elif konsentrasi >= 15:
            color = 'beige'
        else:
            color = 'green'
    elif polutan == 'PM10':
        if konsentrasi >= 150:
            color = 'darkpurple'
        elif konsentrasi >= 100:
            color = 'darkred'
        elif konsentrasi >= 75:
            color = 'red'
        elif konsentrasi >= 50:
            color = 'orange'
        elif konsentrasi >= 45:
            color = 'beige'
        else:
            color = 'green'
    elif polutan == 'O3':
        if konsentrasi >= 160:
            color = 'darkpurple'
        elif konsentrasi >= 120:
            color = 'darkred'
        elif konsentrasi >= 100:
            color = 'red'
        else:
            color = 'green'
    elif polutan == 'NO2':
        if konsentrasi >= 120:
            color = 'darkpurple'
        elif konsentrasi >= 50:
            color = 'darkred'
        elif konsentrasi >= 25:
            color = 'red'
        else:
            color = 'green'
    elif polutan == 'SO2':
        if konsentrasi >= 125:
            color = 'darkpurple'
        elif konsentrasi >= 50:
            color = 'darkred'
        elif konsentrasi >= 40:
            color = 'red'
        else:
            color = 'green'
    elif polutan == 'CO':
        if konsentrasi >= 7000:
            color = 'darkpurple'
        elif konsentrasi >= 4000:
            color = 'darkred'
        else:
            color = 'green'
    else:
        color = 'gray'

    return color

# Simpan koordinat tiap stasiun
station_coordinates = {
    "Aotizhongxin": [39.982, 116.397],
    "Changping": [40.217, 116.230],
    "Dingling": [40.292, 116.220],
    "Dongsi": [39.929, 116.417],
    "Guanyuan": [39.929, 116.339],
    "Gucheng": [39.914, 116.184],
    "Huairou": [40.328, 116.628],
    "Nongzhanguan": [39.937, 116.461],
    "Shunyi": [40.127, 116.655],
    "Tiantan": [39.886, 116.407],
    "Wanliu": [39.987, 116.287],
    "Wanshouxigong": [39.878, 116.352]
} 

try:
    # Dapatkan dataframe pada tanggal yang ditentukan
    time_merged_df = merged_df.loc[(merged_df["datetime"]==date_choice) & (merged_df["hour"]==hour_choice)]

    # Buat peta dengan titik tengah koordinat di Beijing
    center_peta = [40.1042, 116.4074]  
    beijing_peta = folium.Map(location=center_peta, zoom_start=9)

    # Beri tanda untuk tiap stasiun
    for station, location in station_coordinates.items():
        data_station = time_merged_df.loc[(time_merged_df["station"]==station)]
        konsentrasi = data_station[pollutant_choice].values[0]
        folium.Marker(
            location,
            popup=station,
            icon=folium.Icon(color=getAnnotationColor(pollutant_choice, konsentrasi)),
        ).add_to(beijing_peta)

    # Tambahkan anotasi keliling Beijing dari GeoJSON
    folium.GeoJson("beijing.json", name="Beijing").add_to(beijing_peta)

    # Tampilkan peta
    st_beijing_peta = st_folium(beijing_peta)
except:
    st.write('Data unavailable')
#####################################################