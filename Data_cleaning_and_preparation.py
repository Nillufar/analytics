""""""" Data cleaning and preparation"""""
Before we can start analyzing data, we need to make sure the data is correct. 
If the data is wrong or incomplete, the analysis will be wrong or misleading,
no matter how sophisticated our models are.

Data cleaning is a critical steps. finance analyst spend significanlty more 
time preparing, cleaning and validating data than perdorming actual analysis
(some sources say 40%-80% of warking hours.)

"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

"""Handling of corporate actions"""
#Corporate actions like dividends, stock plits, and m&a mechanically alter
#prices. If these events are not properly adjusted for, the data may suggest 
#large price changes that are not true economic gains or losses.

netflix = pd.read_excel("Netflix.xlsx")
netflix.columns = netflix.iloc[0]
netflix = netflix.drop(0)
netflix = netflix.rename(columns={"Timestamp": "Date"})
netflix = netflix.dropna(axis=1, how="all")
netflix = netflix.set_index("Date")
print(netflix.index.dtype)

#plot stock price for netflix
plt.figure()
plt.plot(netflix.index, netflix["CLOSE"])
plt.title("Netflix Stock Price")
plt.xlabel("Date")
plt.ylabel("Price")
plt.show()

#plot adjusted prices
plt.figure()
plt.plot(netflix.index, netflix["Close-Adjusted"])
plt.title("Netflix Stock Price")
plt.xlabel("Date")
plt.ylabel("Price")
plt.show()

#Calculate adjustement factor

netflix["adj_factor"] = 1.0
netflix.loc[netflix.index <= "2025-11-17", "adj_factor"] = 0.1
netflix["Adj_Close_check"] = netflix["CLOSE"] * netflix["adj_factor"]

"""Avoid survivorship bias"""
#Survivorship bias occurs when we analyze only the firms that currently exist
#and ignore those that failed, merged, or were delisted.
#By excluding companies that disappeared, we systematically overestimate historical 
#performance and underestimate risk.

""""Handling missing data"""
data = pd.DataFrame([[np.nan,np.nan, 6.5, 3.], [np.nan,1., np.nan, np.nan],[np.nan,np.nan, np.nan, np.nan], [np.nan,np.nan, 6.5, 3.]])

data.isna().sum()
#data = data.dropna() 
#data = data.dropna(subset=[2]) 
#data= data.dropna(axis=1, how="all")
#data = data.dropna(thresh=2)

#define missings when loading
#df = pd.read_csv("data.csv", na_values=["NA", "N/A", -99, -999])
#convert custom missings
#df = df.replace(["NA", "N/A", "NULL", ""], pd.NA)

#Filling missing data


data.fillna(0)
data.fillna({1: 0.5, 3: 0})

data.ffill()
# df.sort_index() may need to be used
#data.ffill(limit=2)

data.bfill()

data.fillna(data.mean())

data.interpolate()
#data.interpolate(method="time")

"""Handling duplicates"""
#sometimes we have repeated data that we need to drop.
data.duplicated()
data.drop_duplicates()

"""handling outlier"""
#Datasets often contain extreme values, with ome of them real, and some errors
#Many statistical measures are sensitive to outliers, so they can substantially 
#alter the outcome of the analysis.

#creating example data

np.random.seed(1)
normal_returns = np.random.normal(loc=0.001, scale=0.02, size=100)
outliers = np.array([0.50, -0.40])   
returns = np.concatenate([normal_returns, outliers])
df = pd.DataFrame({"Return": returns})

df.describe()

#remove outliers
df_removed=df[df["Return"].abs() < 0.20]
df_removed.describe()

#winsorize
lower = df["Return"].quantile(0.01)
upper = df["Return"].quantile(0.99)
df["Return_w"] = df["Return"].clip(lower, upper)
df.describe()


"""Data transformation"""

#Log transformation is used in finance to modify the scale and 
#statistical properties of data. It is commonly applied to prices
#to compute log returns, which convert multiplicative growth into 
#additive changes. Logs are also used for highly skewed variables 
#such as firm size or market capitalization. Because logarithms 
#compress large values more than small ones,
#they reduce skewness and prevent extreme observations from 
#disproportionately influencing the analysis.

assets = pd.read_csv("Total_assets.csv")
assets.info()
assets.describe()

assets = assets[["tic", "fyear", "gvkey", "at"]]
assets.duplicated(subset=["gvkey", "fyear"]).sum()

#drops all rows with duplicates. This is tipically dangerous to do
assets = assets.drop_duplicates(subset=["gvkey", "fyear"], keep=False)
assets.duplicated(subset=["gvkey", "fyear"]).sum()
assets = assets.dropna(subset=["at"])
assets.describe()


plt.figure()
plt.hist(assets["at"], bins=30)
plt.title("Distribution of Total Assets (Raw)")
plt.xlabel("Total Assets")
plt.ylabel("Frequency")
plt.show()

#log transformation
assets["log_at"] = np.log(assets["at"])

plt.figure()
plt.hist(assets["log_at"], bins=30)
plt.title("Distribution of Total Assets (Log Transformed)")
plt.xlabel("Log(Total Assets)")
plt.ylabel("Frequency")
plt.show()


#Dummy and categorical variables.
#Many datasets contain categorical (qualitative) variables 
#that represent groups or labels rather than numerical quantities
#Because statistical models require numerical inputs, categorical variables 
#must be transformed into numbers.
#A common approach is to create dummy variables, which convert each category into 
#a binary indicator (0 or 1).

#dummy variables
wages = pd.DataFrame({
    "Name": ["Alice", "Bob", "Carol", "David", "Emma", "Frank"],
    "Gender": ["Female", "Male", "Female", "Male", "Female", "Male"],
    "Salary": [90000, 75000, 65000, 80000, 62000, 72000]
})


wages["Male"] = (wages["Gender"] == "Male").astype(int)

pd.get_dummies(wages["Gender"])
 
wages2 = pd.concat([wages, pd.get_dummies(wages["Gender"])], axis=1)
wages3 = pd.concat([wages, pd.get_dummies(wages["Gender"],drop_first=True)], axis=1)


#categorical 
credit_rating = pd.DataFrame({
    "Firm": ["A", "B", "C", "D", "E"],
    "Rating": ["AAA", "BBB", "A", "AA", "BBB"]
})

print(credit_rating.dtypes)
credit_rating["Rating"] = credit_rating["Rating"].astype("category")
print(credit_rating.dtypes)
print(credit_rating["Rating"].cat.codes)

#categorical ordered
rating_order = ["AAA", "AA", "A", "BBB"]

credit_rating["Rating"] = pd.Categorical(
    credit_rating["Rating"],
    categories=rating_order,
    ordered=True
)

#Z-score transformation
#rescales a variable so that it has a mean of zero 
#and a standard deviation of one, making the transformed variable unitless.
#This transformation places variables into a comparable scale
#By standardizing, we ensure that comparisons reflect relative variation 
#rather than measurement units.
assets["log_at"].describe()

mean_log_at = assets["log_at"].mean()
std_log_at = assets["log_at"].std()

assets["log_at_z"] = (assets["log_at"] - mean_log_at) / std_log_at

assets["log_at_z"].describe()
