# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 09:09:36 2018

@author: HintonP
"""

import pandas as pd
import numpy as np

FILE_PATH_INPUT = 'W:/B&M/Store Segmentation/Pete/Learning/Git/Predictive-Model---Claires/GER-Sales_Predictive_Model/4. LM without Weather + Lasso/Input_Data/'

FILE_PATH_OUTPUT = 'W:/B&M/Store Segmentation/Pete/Learning/Git/Predictive-Model---Claires/GER-Sales_Predictive_Model/4. LM without Weather + Lasso/Output_Data/'

#### Import required datasets from excel ###########################################################
sales_storeHours_hol_promo_df = pd.read_excel(FILE_PATH_INPUT+'Sales-StoreHours-Hol-Promo.xlsx', sheetname='Data')
sales_agg_df = pd.read_csv(FILE_PATH_INPUT+'Sales_agg_cluster-k4.csv')

#### Assign the right data types to the features. for example, store number should be categorical ##

sales_storeHours_hol_promo_df['Store_Number'] = sales_storeHours_hol_promo_df.Store_Number.astype('category')

#### Extract week, day of the week from transaction date ###########################################

def extract_dayofweek(date):
    return date.dayofweek

def extract_weeknum(date):
    return date.week

#### Data processing & clustering analysis #########################################################

sales_storeHours_hol_promo_cluster_df = pd.merge(sales_storeHours_hol_promo_df, sales_agg_df[['Store_Number','Cluster']],
                 how='left', on=['Store_Number'])
sales_storeHours_hol_promo_cluster_df.shape

#### filter out any records with open hours less than 0 ############################################
sales_storeHours_hol_promo_cluster_df = sales_storeHours_hol_promo_cluster_df.loc[sales_storeHours_hol_promo_cluster_df['Open Hours']>0,:]

#### Remove data for closed stores #################################################################

closed_stores_list = [] #### Add any French stores due to close, check stock builds

sales_storeHours_hol_promo_cluster_df = sales_storeHours_hol_promo_cluster_df.loc[np.logical_not(sales_storeHours_hol_promo_cluster_df.Store_Number.isin(closed_stores_list)),:]

features = ['Transaction_Date', 'Transaction_Count',
        'Open Hours', 'Labour Hours',
       'Holiday_Event', 'Holiday_Period', 'Promo', 'Sales_Promo', 'Cluster']

response = 'Sales'

response_df = sales_storeHours_hol_promo_cluster_df[response]
data_df = sales_storeHours_hol_promo_cluster_df[features]
data_df['Day_of_Week']  = data_df.Transaction_Date.apply(extract_dayofweek)
data_df['Week_Num'] = data_df.Transaction_Date.apply(extract_weeknum)

#### Convert various elements into category type ###################################################

data_df.Day_of_Week = data_df.Day_of_Week.astype('category')
data_df.Week_Num = data_df.Week_Num.astype('category')
data_df.Cluster =  data_df.Cluster.astype('category')

data_df.drop(['Transaction_Date'],axis=1,inplace=True)

data_df.drop(['Transaction_Count'],axis=1,inplace=True)

data_dummy_df = pd.get_dummies(data_df)

#### Model 1 #######################################################################################

from sklearn.model_selection import train_test_split

train_X, test_X, train_y, test_y = train_test_split(data_dummy_df, response_df, 
                                                    train_size=0.75,   #### Set Test Size
                                                    random_state=123,
                                                    )

#### Model 1 End ###################################################################################

##### Model 2 standardized data ####################################################################
#
#from sklearn.pipeline import make_pipeline
#from sklearn.preprocessing import StandardScaler
#from sklearn.model_selection import GridSearchCV
#from sklearn.linear_model import Lasso
#
#
#Est_StdSca_LM = make_pipeline(StandardScaler(),Lasso(random_state=123, max_iter=5000))
#
#Est_StdSca_LM_params = {'lasso__alpha':[.1,1,10]                    
#        }
#
#Est_grid = GridSearchCV(Est_StdSca_LM, param_grid=Est_StdSca_LM_params, cv=5,verbose=3)
#
#Est_grid.fit(train_X,train_y).score(test_X,test_y)

#### Model 2 End ###################################################################################

from sklearn.linear_model import Lasso
np.random.seed(123)

#### Create a list of Lasso Estimators with various L1 penalties--i.e. alpha values ################

Est_StdSca_Lasso_list = [Lasso(normalize=False,max_iter=5000, alpha=a, random_state=123) for a in [0.1,1,10]]

#### Store the output in the lists for each estimator 

lasso_coeff = []
lasso_score = []
lasso_params = []
lasso_intercept = []
for est in Est_StdSca_Lasso_list:
    print(est.get_params())
    score = est.fit(train_X,train_y).score(test_X,test_y)
    print("Score: ",score)
    print('Coeff:\n',est.coef_)
    #### append to the list
    lasso_coeff.append(est.coef_)
    lasso_score.append(score) ### Generalization error; Not training error
    lasso_params.append(est.get_params())
    lasso_intercept.append(est.intercept_)

##### print the score for alpha = 0.1 ##############################################################
    
from sklearn.metrics import mean_squared_error, r2_score
    
test_pred = Est_StdSca_Lasso_list[0].predict(test_X)
print(" Root Mean squared error: %.2f"
      % np.sqrt(mean_squared_error(test_y, test_pred)))
### Explained variance score: 1 is perfect prediction
print('Variance score: %.2f' % r2_score(test_y, test_pred))

#### Conclusion :
#### Lasso with alpha = 0.1 seems to be working fine
#### Root Mean squared error: 360.84
#### Variance score: 0.6

#### Output the coefficients into a file ###########################################################

lasso_coeff_df = pd.DataFrame(lasso_coeff).transpose()
lasso_coeff_df['Features'] =  test_X.columns

lasso_intercept_df = pd.DataFrame(lasso_intercept).transpose()
lasso_intercept_df['Features'] = 'Intercept'

lasso_score_df = pd.DataFrame(lasso_score).transpose()
lasso_score_df['Features'] = 'Score'

lasso_output_df = pd.merge(lasso_score_df, lasso_intercept_df,how="outer")
lasso_output_df = pd.merge(lasso_output_df,lasso_coeff_df,how="outer")
   
lasso_output_df.columns = ['Alpha_0.1', 'Alpha_1', 'Alpha_10', 'Features']

lasso_output_df.to_csv(FILE_PATH_OUTPUT+'Lasso_Output.csv',index=False)


#### Create Barplot of sroted values for Aplha 1 ###################################################
lasso_output_df2 = lasso_output_df
lasso_output_df2 = lasso_output_df2.drop('Alpha_0.1', 1)
lasso_output_df2 = lasso_output_df2.drop('Alpha_10', 1)
lasso_output_df2 = lasso_output_df2.sort_values('Alpha_1')
lasso_output_df2 = lasso_output_df2.loc[lasso_output_df2['Alpha_1'] != 0,:]
lasso_output_df2 = lasso_output_df2.loc[lasso_output_df2['Features'] != 'Intercept',:]
lasso_output_df2 = lasso_output_df2.loc[lasso_output_df2['Features'] != 'Score',:]



ax = lasso_output_df2.plot(kind='bar', title ="Germany Coefficient Variables [alpha_1]", figsize=(15, 10), edgecolor='black',  legend=False,  fontsize=12)
ax.set_xticklabels(lasso_output_df2.Features)
