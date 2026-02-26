#!/usr/bin/env python
# coding: utf-8

# # Health Data Scientist Practical Assessment
# 
# **Candidate:** Cameron Hannie  
# **Date:** 16 February 2026
# 
# ## Section B  Practical: Wide Patient Dataset
# ### Imports :
# 

# In[64]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from datetime import date




# ## 1) Load the data files
# We load the medicine dispensing data and the laboratory data and do basic data analysis checks.  
# 

# In[65]:


med = pd.read_csv("medicine_data.csv")
med.head()


# In[66]:


lab = pd.read_csv("lab_data.txt", sep="\t")
lab.head()


# In[67]:


print(med.columns)
print(lab.columns)



# In[68]:


print(med.shape)
print(lab.shape)




# In[69]:


print(med.isnull().sum())
print()
print(lab.isnull().sum())


# In[70]:


print(med.dtypes)
print()
print(lab.dtypes)


# ## 2) Standardize sex 
#  
# 

# In[71]:


# Standardize sex column to M / F
med["sex"] = med["sex"].str.strip().str.upper().str[0]
lab["sex"] = lab["sex"].str.strip().str.upper().str[0]


# ## 3 ) Create 1 row per patient table 
# 

# In[72]:


# Build a base patient table
demo = pd.concat(
    [
        med[["patient_id", "sex", "date_of_birth"]],
        lab[["patient_id", "sex", "date_of_birth"]]
    ],
    ignore_index=True
).drop_duplicates(subset="patient_id")


# In[73]:


demo.head()


# ## 4) Create age category 
# Buckets: <30, 30-39, 40-49, 50-59, >=60
# 

# In[76]:


today = pd.Timestamp(date.today())
demo["date_of_birth"] = pd.to_datetime(demo["date_of_birth"])

# age in years (whole number)
demo["age_years"] = (today - demo["date_of_birth"]).dt.days / 365.25
demo["age_years"] = np.floor(demo["age_years"])

def age_bucket(age):
    if pd.isna(age):
        return np.nan
    age = int(age)

    if age < 30:
        return "<30"
    elif age < 40:
        return "30-39"
    elif age < 50:
        return "40-49"
    elif age < 60:
        return "50-59"
    else:
        return ">=60"

demo["age_category"] = demo["age_years"].apply(age_bucket)


# ## 5 )Summarise medicine data per patient
# 
# 

# In[77]:


# Flag insulin and metformin rows
med["is_insulin"] = med["medication_name"].str.contains("insulin", na=False)
med["is_metformin"] = med["medication_name"].str.contains("metformin", na=False)

# Summarise per patient
med_summary = med.groupby("patient_id").agg(
    last_medicine_dispensing_date=("dispensing_date", "max"),
    number_times_medicines_dispensed=("dispensing_date", "count"),
    any_insulin=("is_insulin", "max"),
    any_metformin=("is_metformin", "max"),
).reset_index()

# Create medicine category
med_summary["medicine_category"] = "No drugs dispensed"
med_summary.loc[(med_summary["any_insulin"] == 1) & (med_summary["any_metformin"] == 0), "medicine_category"] = "Insulin only"
med_summary.loc[(med_summary["any_insulin"] == 0) & (med_summary["any_metformin"] == 1), "medicine_category"] = "Metformin only"
med_summary.loc[(med_summary["any_insulin"] == 1) & (med_summary["any_metformin"] == 1), "medicine_category"] = "Insulin and metformin"


# In[78]:


med_summary.head()


# ## 6) Merge medicine summary into patient table
# 

# In[79]:


# Merge medicine summary into the patient table
wide = demo.merge(med_summary, on="patient_id", how="left")

# Fill missing values for patients with no medicine records
wide["number_times_medicines_dispensed"] = wide["number_times_medicines_dispensed"].fillna(0)
wide["medicine_category"] = wide["medicine_category"].fillna("No drugs dispensed")


# In[80]:


wide.head()


# ## 7) Get latest HbA1c test per patient (date + result)
# 

# In[81]:


# Keep only HbA1c tests
hba1c = lab[lab["lab_test_type"] == "HbA1c"]

# Convert result column to numeric
hba1c["lab_test_result"] = pd.to_numeric(hba1c["lab_test_result"])

# Get the latest HbA1c test per patient
hba1c = hba1c.sort_values("lab_test_date")
latest_hba1c = hba1c.groupby("patient_id").last().reset_index()

# Rename columns
latest_hba1c = latest_hba1c.rename(columns={
    "lab_test_date": "hba1c_test_date",
    "lab_test_result": "hba1c_test_result"
})

# Merge into wide dataset
wide = wide.merge(
    latest_hba1c[["patient_id", "hba1c_test_date", "hba1c_test_result"]],
    on="patient_id",
    how="left"
)


# In[82]:


latest_hba1c.head()


# ## 8 )Create follow-up flag and export final wide dataset
# follow up flag 
# 

# In[83]:


wide.columns


# In[84]:


# Create follow-up flag
wide["diabetic_treatment_follow_up_flag"] = 0

wide.loc[wide["hba1c_test_result"] >= 8, "diabetic_treatment_follow_up_flag"] = 1
wide.loc[wide["number_times_medicines_dispensed"] == 0, "diabetic_treatment_follow_up_flag"] = 1

# Final dataset with required columns
final = wide[[
    "patient_id",
    "sex",
    "age_category",
    "medicine_category",
    "last_medicine_dispensing_date",
    "number_times_medicines_dispensed",
    "hba1c_test_date",
    "hba1c_test_result",
    "diabetic_treatment_follow_up_flag"
]]

final.head()



# In[85]:


# Export dataset
final.to_csv("wide_patient_dataset.csv", index=False)


# ## Question 3 Distribution of insulin-only patients by sex and age category
# 

# In[59]:


insulin_only = final[final["medicine_category"] == "Insulin only"]


# In[63]:


#group data
plot_data = insulin_only.groupby(["age_category", "sex"]).size().unstack(fill_value=0)
plot_data

#plot data
plot_data.plot(kind="bar")
plt.title("Distribution insulin-Only Patients by sex and age category")
plt.xlabel("Age category")
plt.ylabel("Number of patients")
plt.xticks(rotation=0)
plt.show()


# In[ ]:




