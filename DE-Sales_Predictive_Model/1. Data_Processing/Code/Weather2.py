# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 12:54:02 2017

@author: aripiralas
edited by Ke Xing@1/18/2013
"""
## url = 'http://api.wunderground.com/api/eec4c24fa3e74d09/history_20171105/q/MD/Baltimore.json'


import pandas as pd
import glob
import os
# import numpy as np


### wunderground api key : eec4c24fa3e74d09  station id for an example station IHAMMERS1

from urllib.request import urlopen as uReq
# from urllib.request import Request
import json
from datetime import date, timedelta
import time


def build_url_wunderground(date, city, state, country, key):
    global url_begin

    if (country == 'US'):
        return url_begin + key + '/history_' + date.strftime("%Y%m%d") + '/q/' + state + '/' + city + '.json'
    else:
        return url_begin + key + '/history_' + date.strftime("%Y%m%d") + '/q/' + country + '/' + city + '.json'


def get_weather(start_date, end_date, city, state, country, weather_df):
    global FIRST_ITER
    global minute_counter, day_counter, per_key_per_minute_counter, DAY_MAX_COUNT, MINUTE_MAX_COUNT, MINUTE_MAX_COUNT_PER_KEY
    global key_looper

    d = start_date
    delta = timedelta(days=1)

    while d <= end_date:
        url = build_url_wunderground(d, city, state, country, key_list[key_looper])
        print(url)
        # req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        # weather_json= uReq(req).read()
        weather_json = uReq(url)
        weather_dict = json.load(weather_json)

        day_counter = day_counter + 1
        minute_counter = minute_counter + 1
        per_key_per_minute_counter = per_key_per_minute_counter + 1

        if per_key_per_minute_counter == MINUTE_MAX_COUNT_PER_KEY:
            if key_looper == KEY_COUNT - 1:
                key_looper = 0
            else:
                key_looper = key_looper + 1
            per_key_per_minute_counter = 0

        if day_counter == DAY_MAX_COUNT:
            day_counter = 0
            time.sleep(60 * 60 * 24)  ### sleep for 24 hours

        if minute_counter == MINUTE_MAX_COUNT:
            minute_counter = 0
            time.sleep(90)  #### sleep for 1.5 minutes

        # print("The mean temperature is %0.2f "%float(weather_dict['history']['dailysummary'][0]['meantempi']))
        try:
            if FIRST_ITER:
                dailysummary_cols = [k for k in weather_dict['history']['dailysummary'][0].keys()]
                dailysummary_cols.insert(0, 'Date')
                dailysummary_cols.insert(0, 'City')
                weather_df = pd.DataFrame(columns=dailysummary_cols)
                # print("First Iter\n")
                FIRST_ITER = False

            dailysummary_values = [v for v in weather_dict['history']['dailysummary'][0].values()]
            dailysummary_values.insert(0, d)
            dailysummary_values.insert(0, city)

            df = pd.DataFrame(dailysummary_values)
            df = df.transpose()
            df.columns = weather_df.columns

            weather_df = pd.concat([weather_df, df])
            d += delta
        except KeyError:
            print("There is no data available for airport code:%s & date:%s\n" % (city, d.strftime("%Y%m%d")))
            d += delta
        except IndexError:
            print(
                "IndexError: There is no data available for airport code:%s & date:%s\n" % (city, d.strftime("%Y%m%d")))
            d += delta
    return weather_df


####### INITIALIZE variables ###########################################

# key = 'eec4c24fa3e74d09'
url_begin = 'http://api.wunderground.com/api/'

country = 'DE'

start_date = date(2016, 1, 1)
end_date = date(2018, 1, 13)

FILE_PATH = 'W:/B&M/Store Segmentation/Predictive Model/EU - Model/DE/'

FILE_PATH_LOCAL = 'C:/Ad hoc Analysis/Weather/'

key_list = ['56ea777f7516c834', 'eec4c24fa3e74d09', '70628b4299bc3d8b', '4013a46d97e47844', '6f463c16cde40212',
            '59e4d5b0bfe7b0fe', '15452cb4037bdbec', 'e8b4e71b38660737', 'e36ef1805bbe364a', 'a5af324a7e3aebfb',
            '1f59ac5dde31573f', 'd10134f003be0924', 'dc7fbab17b6306ef', '8c73f89279e0799a', '7e5eabcda55f9659',
            'd7a4b41073377aef', 'aad1e3a5703667ae', 'dc57de726c1bbf8d', '3bcb5a9054c51b8a', 'bc7277662fdd7a8f',
            '439e85f9c4ac942f', '8995edeeb47c83d9', 'ad68e3eec63fa7e8', 'd085fd331227406b']

KEY_COUNT = len(key_list)
MINUTE_MAX_COUNT = 10 * KEY_COUNT
DAY_MAX_COUNT = 490 * KEY_COUNT
MINUTE_MAX_COUNT_PER_KEY = 10

minute_counter = 0
day_counter = 0
per_key_per_minute_counter = 0
key_looper = 0

# time.sleep(60*60*24) ### sleep for 24 mins. Start tomorrow noon

####### END Initialization of Variables ########


### load the airport codes in to a dataframe #####

DATASET_NOT_LOADED = True
FIRST_ITER = True

if DATASET_NOT_LOADED:
    uk_airport_df = pd.read_csv(FILE_PATH + 'Airport_DE.csv')

    DATASET_NOT_LOADED = False

weather_df = pd.DataFrame()

airport_code_counter = 13
### loop through all the
uk_airport_df_continue = uk_airport_df[0:]

for code in uk_airport_df_continue['Airport_Code']:
    # print(code)
    weather_df = pd.DataFrame(pd.np.empty((0,72)))

    if FIRST_ITER:
        weather_df = get_weather(start_date, end_date, code, '', country, pd.DataFrame())
    else:
        weather_df = get_weather(start_date, end_date, code, '', country, weather_df)

    weather_df.to_csv(FILE_PATH_LOCAL + 'weather_' + str(code) + '.csv')

# Combining all downloaded files
# set wd
os.chdir(FILE_PATH_LOCAL)
# get all the .csv from wd
allfiles = glob.glob("*.csv")
# prepare empty data frame
raw_data = pd.DataFrame()
# read and merge all csv in a for loop
raw_data = pd.concat((pd.read_csv(f, header=0) for f in allfiles))
# rearrange columns to fit data_processing.py
ready_data = raw_data[['0', '1', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26',
                       '27', '28', '29', '3', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '4',
                       '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '5', '50', '51', '52', '53',
                       '54', '55', '56']]
# renaming the all in one file
ready_data.rename(columns={'0': 'City', '1': 'Date', '3': 'fog', '4': 'rain', '5': 'snow', '14': 'hail',
                           '15': 'thunder', '16': 'tornado', '17': 'meantempm', '18': 'meantempi', '19': 'meandewptm',
                           '20': 'meandewpti', '21': 'meanpressurem', '22': 'meanpressurei', '23': 'meanwindspdm',
                           '24': 'meanwindspdi', '25': 'meanwdire', '26': 'meanwdird', '27': 'meanvism',
                           '28': 'meanvisi', '29': 'humidity', '30': 'maxtempm', '31': 'maxtempi', '32': 'mintempm',
                           '33': 'mintempi', '34': 'maxhumidity', '35': 'minhumidity', '36': 'maxdewptm',
                           '37': 'maxdewpti', '38': 'mindewptm', '39': 'mindewpti', '40': 'maxpressurem',
                           '41': 'maxpressurei', '42': 'minpressurem', '43': 'minpressurei', '44': 'maxwspdm',
                           '45': 'maxwspdi', '46': 'minwspdm', '47': 'minwspdi', '48': 'maxvism', '49': 'maxvisi',
                           '50': 'minvism', '51': 'minvisi', '52': 'gdegreedays', '53': 'heatingdegreedays',
                           '54': 'coolingdegreedays', '55': 'precipm', '56': 'precipi'}, inplace=True)
ready_data.to_csv(FILE_PATH_LOCAL + 'weather_' + 'vF2' + '.csv', index=False)