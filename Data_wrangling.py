"""Data Wrangling"""
""" From IBM: the process of cleaning, structuring, and enriching raw data 
to be used in data science, machine learning, and other data-driven applications.

The data we need for our particular application typically comes from different 
sources, which may be in different formats. Before we can use it, we have to combine 
it in such a way that it is convenient to analyze."""

import pandas as pd

"""Concatenate"""
#Concat is a method that combines multiple datasets into one by stacking them together.
#We typically use this when datasets have the same structure (same columns), and we want
#to add more observations
#important: duplicates are not checked or removed by default

jan = pd.DataFrame({
    "Firm": ["A", "B"],
    "Date": ["2025-01-31", "2025-01-31"],
    "Return": [0.02, 0.03]
})

feb = pd.DataFrame({
    "Firm": ["A", "B"],
    "Date": ["2025-02-28", "2025-02-28"],
    "Return": [-0.01, 0.04]
})

year_data = pd.concat([jan, feb], ignore_index=True)


#Column-wise concatenation is less common but we can use it to add more columns

returns = pd.DataFrame({
    "Return": [0.01, 0.02, 0.03]
})

riskfree = pd.DataFrame({
    "RF": [0.001, 0.001, 0.001]
})

combined = pd.concat([returns, riskfree], axis=1)

# When concatenating column-wise, pandas matches rows using their index labels,
# not simply their physical row positions. If the indices do not match,
# the combined data may contain missing values or incorrectly aligned observations.

# What if structure is not the same?

mar = pd.DataFrame({
    "Firm": ["A", "B"],
    "Date": ["2025-03-31", "2025-03-31"],
    "Return": [0.02, 0.03]
})

apr = pd.DataFrame({
    "Firm": ["A", "B"],
    "Date": ["2025-04-30", "2025-04-30"],
    "Return": [-0.01, 0.04],
    "Volume": [1000, 1500]
})

combined = pd.concat([mar, apr], ignore_index=True)


#ingnore_index controls what happens to row index after concatenation
# True ->  reset indexs to 0,1,2,..
# False -> keep original index
# if we set it as False, we may end up with duplicate indices. In some cases we may want this
# for example if the index are dates to firm IDs.
#default is False

year_data_2 = pd.concat([jan, feb], ignore_index=False)
pd.concat
print(year_data)
print(year_data_2)

#Join controls whihc columns are kept when the dataframes do not have identical structure
# outer -> keeps all columns and fills missing values with NaN
# inner -> keeps only the columns common to both datasets
# default is outer

combined2 = pd.concat([mar, apr], ignore_index=True, join="inner")
print(combined)
print(combined2)


"""merge"""
#merge is a method that combines two datasets along common columns or indices.


returns = pd.DataFrame({
    "Firm": ["A", "B", "C"],
    "Return": [0.05, 0.02, -0.01]
})

size = pd.DataFrame({
    "Firm": ["A", "B", "C"],
    "Size": [100, 200, 150]
})

print(returns)
print(size)

merged = pd.merge(returns, size, on="Firm")

print(merged)

#we can have multiple keys

returns = pd.DataFrame({
    "Firm": ["A", "A", "B", "B"],
    "Date": ["2025-01", "2025-02", "2025-01", "2025-02"],
    "Return": [0.05, 0.02, -0.01, 0.03]
})

size = pd.DataFrame({
    "Firm": ["A", "A", "B", "C"],
    "Date": ["2025-01", "2025-02", "2025-01", "2025-01"],
    "Size": [100, 110, 200, 300]
})

print(returns)
print(size)

merged = pd.merge(returns, size, on=["Firm", "Date"])

print(merged)

#how method contorls the inclusion logic of the merge
#inner (default) -> keep only rows that have matching keys in both dataframes
#outer -> keep all rows from both dataframes

merged_outer = pd.merge(returns, size, on=["Firm", "Date"], how="outer") # indicator = True
print(merged)
print(merged_outer)

#left -> keeps every row from the left data, add columns from right one when keys match,
#unmatched right-side values filled with Nan

merged_left = pd.merge(returns, size, on=["Firm", "Date"], how="left")
print(merged)
print(merged_left)

#right -> symetric case to left

merged_right = pd.merge(returns, size, on=["Firm", "Date"], how="right")
print(merged)
print(merged_right)


#Sometimes columns names are different

returns = pd.DataFrame({
    "Firm": ["A", "B", "C"],
    "Return": [0.05, 0.02, -0.01]
})

size = pd.DataFrame({
    "Ticker": ["A", "B", "C"],
    "Size": [100, 200, 150]
})

pd.merge(returns,size,left_on="Firm",right_on="Ticker")

# we can also merge by index
df1 = pd.DataFrame({"Return": [0.02, 0.03]},
                   index=["A", "B"])

df2 = pd.DataFrame({"Size": [100, 200]},
                   index=["A", "B"])

merged_on_index = pd.merge(df1,df2,left_index=True,right_index=True)

print(merged_on_index)


#Example

# Daily returns
returns = pd.DataFrame({
    "Firm": ["A", "A", "A", "B", "B"],
    "Date": ["2025-01-02", "2025-01-15", "2025-02-03",
             "2025-01-10", "2025-02-12"],
    "Return": [0.01, -0.02, 0.03, 0.02, -0.01]
})

# Convert Date to datetime
returns["Date"] = pd.to_datetime(returns["Date"])

# Create a Month variable
returns["Month"] = returns["Date"].dt.to_period("M")

returns.info()

# Monthly fundamentals
fundamentals = pd.DataFrame({
    "Firm": ["A", "A", "B", "B"],
    "Month": ["2025-01", "2025-02", "2025-01", "2025-02"],
    "Size": [100, 110, 200, 210]
})

# Convert Month to period type
fundamentals["Month"] = pd.to_datetime(fundamentals["Month"]).dt.to_period("M")

#merge
merged = pd.merge(returns, fundamentals, on=["Firm", "Month"], how="left")

print(merged)