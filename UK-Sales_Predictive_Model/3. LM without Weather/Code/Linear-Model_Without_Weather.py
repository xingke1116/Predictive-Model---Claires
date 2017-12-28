import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler 
from sklearn.pipeline import make_pipeline
import numpy as np
import seaborn as sns
from sklearn.model_selection import GridSearchCV


FILE_PATH_INPUT = 'C:/Users/aripiralas/GitHub/Predictive-Modeling/Predictive-Model---Claires/UK-Sales_Predictive_Model/3. LM without Weather/Input_Data/'

FILE_PATH_OUTPUT = 'C:/Users/aripiralas/GitHub/Predictive-Modeling/Predictive-Model---Claires/UK-Sales_Predictive_Model/3. LM without Weather/Output_Data/'

# Import required datasets from excel
sales_storeHours_hol_promo_df = pd.read_excel(FILE_PATH_INPUT+'Sales-StoreHours-Hol-Promo.xlsx', sheetname='Data')
sales_agg_df = pd.read_csv(FILE_PATH_INPUT+'Sales_agg_cluster-k4.csv')

### Assign the right data types to the features. for example, store number should be categorical

sales_storeHours_hol_promo_df['Store_Number'] = sales_storeHours_hol_promo_df.Store_Number.astype('category')

###############################################################################################

#### extract week, day of the week from transaction date

def extract_dayofweek(date):
    return date.dayofweek

def extract_weeknum(date):
    return date.week

######### Data processing & clustering analysis ######################################


sales_storeHours_hol_promo_cluster_df = pd.merge(sales_storeHours_hol_promo_df, sales_agg_df[['Store_Number','Cluster']],
                 how='left', on=['Store_Number'])
sales_storeHours_hol_promo_cluster_df.shape

#### filter out any records with open hours less than 0 ###
sales_storeHours_hol_promo_cluster_df = sales_storeHours_hol_promo_cluster_df.loc[sales_storeHours_hol_promo_cluster_df['Open Hours']>0,:]

############################################################
### remove data for closed stores ####################################################

closed_stores_list = [156, 146, 345, 380, 113, 325, 499, 184, 237, 385, 93, 76, 521, 78, 137, 173, 475, 420, 462, 548, 513] 

sales_storeHours_hol_promo_cluster_df = sales_storeHours_hol_promo_cluster_df.loc[np.logical_not(sales_storeHours_hol_promo_cluster_df.Store_Number.isin(closed_stores_list)),:]


######################################################################################


features = ['Transaction_Date', 'Transaction_Count',
        'Open Hours', 'Labour Hours',
       'Holiday_Event', 'Holiday_Period', 'Promo', 'Sales_Promo', 'Cluster']

response = 'Sales'

response_df = sales_storeHours_hol_promo_cluster_df[response]
data_df = sales_storeHours_hol_promo_cluster_df[features]
data_df['Day_of_Week']  = data_df.Transaction_Date.apply(extract_dayofweek)
data_df['Week_Num'] = data_df.Transaction_Date.apply(extract_weeknum)


######################## convert various elements into category type #######

data_df.Day_of_Week = data_df.Day_of_Week.astype('category')
data_df.Week_Num = data_df.Week_Num.astype('category')
data_df.Cluster =  data_df.Cluster.astype('category')

############################################################################

data_df.drop(['Transaction_Date'],axis=1,inplace=True)

data_df.drop(['Transaction_Count'],axis=1,inplace=True)



data_dummy_df = pd.get_dummies(data_df)


#### Model 1 #########

from sklearn.model_selection import train_test_split

train_X, test_X, train_y, test_y = train_test_split(data_dummy_df, response_df, 
                                                    train_size=0.75, 
                                                    random_state=123,
                                                    )

#### linear model without weather data ########
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression

np.random.seed(123)
LM = LinearRegression()
LM.fit(train_X,train_y).score(test_X,test_y)

test_pred = LM.predict(test_X)

print('Coefficients: \n', LM.coef_)
# The mean squared error
print(" Root Mean squared error: %.2f"
      % np.sqrt(mean_squared_error(test_y, test_pred)))
# Explained variance score: 1 is perfect prediction
print('Variance score: %.2f' % r2_score(test_y, test_pred))


#### model with weather data incorporated #########

