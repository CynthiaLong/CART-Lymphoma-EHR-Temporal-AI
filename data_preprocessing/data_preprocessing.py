#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np 


# In[2]:


# Generate simulated patient timeline data
# include patiet ID(patient_SN)，key timepoint(TIME, LOT, Pre/Post treatment)
df_timeline = pd.DataFrame({
'patient_SN': [
        'P01', 'P01', 'P01', 'P01', 'P01',  
        'P02', 'P02', 'P02', 
    ],
    'TIME': [
        '2018-05-28', '2019-01-10',  # P01 LOT 1
        '2022-05-27', '2023-02-17',  # P01 LOT 2
        '2023-05-25',   # P01 CART
        '2019-03-08', '2019-07-11',  # P02 LOT 1 
        '2021-11-21',   # P02 CART 
    ],
    # line of treatment
    'LOT': [
        '1', '1', 
        '2', '2', 
        'CART',  
        '1', '1', 
        'CART'
    ],
    # before or after treatment
    'Pre/Post treatment': [
        'Pre', 'Post', 
        'Pre', 'Post', 
        'Pre',  
        'Pre', 'Post', 
        'Pre'
    ]
})


# In[3]:


# Generate simulated patient clinical feature data
# _COL7 is time, _COL8-_COL11 are clinical features

np.random.seed(42)
df_clin_feats = pd.DataFrame({
    'patient_SN': ['P01']*10 + ['P02']*8,
    '_COL7': ['2018-05-01', '2018-05-02', '2019-01-01', '2019-01-02', \
              '2022-05-01', '2022-05-27', '2023-02-01', '2023-02-02', \
              '2023-05-01', '2023-05-02', \
              '2019-03-01', '2019-03-02', '2019-03-03', '2019-07-01', '2019-07-02',\
              '2021-11-01', '2021-11-02', '2021-11-03'],
    '_COL8': np.random.randint(low=10, high=20, size=18).astype(float),  
    '_COL9': np.where(np.random.rand(18) < 0.2, np.nan, np.random.randint(0, 10, 18)), # genearte missing values  
    '_COL10': np.where(np.random.rand(18) < 0.2, np.nan, ['A']*10 + ['B']*5 + ['C']*3), # genearte missing values
    '_COL11': np.where(np.random.rand(18) < 0.2, np.nan, np.random.randint(100, 120, 18)), # genearte missing values
})


# # Temporal Structure Alignment

# In[4]:


# 1. transform datetime and mark data source
df_clin_feats['TIME'] = pd.to_datetime(df_clin_feats['_COL7'])
df_timeline['TIME'] = pd.to_datetime(df_timeline['TIME'])
df_clin_feats['source'] = 'exam' 
df_timeline['source'] = 'timeline'


# In[5]:


# 2. Vertical stacking 
common_cols = ['patient_SN', 'TIME', 'LOT', 'Pre/Post treatment', 'source'] + ['_COL7', '_COL8', '_COL9', '_COL10', '_COL11']
df_combined = pd.concat([df_clin_feats, df_timeline], ignore_index=True)


# In[6]:


# 3. Sorting and filling in 
# Sort in descending order by time.
# If a Timeline record is encountered, and the record below it is an "exam", then it belongs to this stage.
# If the exam time equals to the timeline time, then it also belongs to this stage.
df_combined = df_combined.sort_values(by=['patient_SN', 'TIME', 'source'], ascending=[True, False, False])


# In[7]:


# Use the forward filling function to mark the treatment stage each check belongs to
df_combined['LOT'] = df_combined.groupby('patient_SN')['LOT'].ffill()
df_combined['Pre/Post treatment'] = df_combined.groupby('patient_SN')['Pre/Post treatment'].ffill()


# In[8]:


# 4. Filter and Group
# Remove the original timeline record rows and only retain the examination data that has been labeled with the treatment stage.
# At the same time, also remove the examination data that did not match any treatment stage.
df_mapped = df_combined[df_combined['source'] == 'exam'].dropna(subset=['LOT']).copy()


# In[9]:


# 创建分组键
df_mapped['sort_key'] = df_mapped['patient_SN'] + '_' + df_mapped['LOT'] + '_' + df_mapped['Pre/Post treatment']


# In[10]:


# 5. Combining data from the same treatment stage
# Within this time window, 
# if there are multiple inspection records, 
# the most recent non-empty value will be selected as the priority.

# Define the aggregation function: 
# Take the first non-null value (since it is currently in reverse order, the latest value is at the top)
def get_latest_valid(series):
    series = series.replace('nan', np.nan, regex=True) # in case 'nan' string exists
    valid = series.dropna()
    if not valid.empty:
        return valid.iloc[0] # Take the first item in reverse order, which is the latest one on the original timeline.
    return np.nan

# Perform aggregation on the specified column
target_cols = ['_COL7', '_COL8', '_COL9', '_COL10', '_COL11'] 
df_result = df_mapped.groupby(['patient_SN', 'LOT', 'Pre/Post treatment'])[target_cols].agg(get_latest_valid).reset_index()


# In[11]:


df_result =  df_result.sort_values(by=['patient_SN', 'LOT', 'Pre/Post treatment'], ascending=[True, True, False])


# # Missing Value Imputation

# In[12]:


# Function to impute each feature for each patient
def impute_patient_features(group):
    for col in target_cols: # target_cols = ['_COL7', '_COL8', '_COL9', '_COL10', '_COL11'] = ['_COL7', '_COL8', '_COL9', '_COL10', '_COL11']:
        # If there is no missing values, skip
        if group[col].notnull().all():
            continue
        # If all values in the column are null, fill with -1
        elif group[col].isnull().all():
            group[col].fillna(-1, inplace=True)
        # If there is only one non-null value, fill all nulls with that value
        elif group[col].notnull().sum() == 1:
            group[col].fillna(group[col].dropna().iloc[0], inplace=True)
        else:
            # First apply Forward fill (use previous non-null value)
            group[col].ffill(inplace=True)
            # If there is still missing values, apply Backward fill (use next non-null value if no previous non-null)
            group[col].bfill(inplace=True)
    return group


# In[13]:


df_imputed = df_result.groupby('patient_SN').apply(impute_patient_features)


# In[14]:


df_imputed.reset_index(drop=True, inplace=True)


# # Data Format Standardization

# In[15]:


from sklearn.preprocessing import MinMaxScaler
 
scaler = MinMaxScaler()

numerical_feats = ['_COL8', '_COL9', '_COL11']
X = df_imputed[numerical_feats]
X = X.replace(['nan', 'NaN', 'None', ' ', ''], np.nan)
X_normalized = scaler.fit_transform(X)
df_scaled = pd.DataFrame(X_normalized, columns=numerical_feats)
df_imputed[numerical_feats] = df_scaled

# The preprocessed dataframe
print(df_imputed)