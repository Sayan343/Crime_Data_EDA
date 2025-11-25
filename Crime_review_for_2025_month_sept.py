import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from wordcloud import WordCloud

# Load the dataset
df = pd.read_csv("datafile.csv")

#display head
# print(df.head())

# Standardize text columns
text_cols = ["Heads Crime", "Major Heads", "Minor Heads"]
for col in text_cols:
    df[col] = df[col].astype(str).str.strip().str.title()


# Standardize 'Heads Crime' column data
df["Major Heads"] = (
    df["Major Heads"]
    .str.replace(r"\([^()]*\)", "", regex=True)  # remove simple parentheses
    .str.replace(r"\([^()]*\)", "", regex=True)  # run twice for nested parentheses
    .str.replace(r"\s+", " ", regex=True)        # remove extra spaces
    .str.strip()
)

df['Heads Crime'] = df['Heads Crime'].replace("E. CRIME AGAINST SCHEDULED CASTES /TRIBES BY NON SCs/STs", "E.CRIME AGAINST SCs/STs")
df['Minor Heads'] = df['Minor Heads'].replace("Nan", "Reason Not Known")



# Drop unnecessary columns
df.rename(columns={"Unnamed: 8": "Garbage Column"}, inplace=True)  #Garbage values unnecessary for this Eda Analysis
df.drop(columns=["Garbage Column"], inplace=True)  #Dropping unnecessary column
# Data cleaning
df=df.dropna(subset=['Heads Crime','Major Heads','Minor Heads']) # Drop rows where 'Heads Crime' is NaN
df['Heads Crime'] = (
    df['Heads Crime']
    .astype(str)
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

df['Heads Crime'] = df['Heads Crime'].str.replace(
    r"E\. Crime Against Scheduled Castes /Tribes By Non Scs/Sts",
    "E. Crime Against SCs/STs",
    regex=True
)

numeric_cols = [
    "During the current year upto the end of month under review",
    "During the corresponding month of previous year",
    "During the previous month",
    "During the current month"
]
df = df[(df[numeric_cols] != 0).any(axis=1)]
print(df)

# Rename
print(df.columns.tolist())
df.rename(columns={'During the current year upto the end of month under review': "Current Year Upto Month End",
                   'During the corresponding month of previous year': "Corresponding Month Previous Year",
                   'During the previous month': "Previous Month",
                   'During the current month': "Current Month"}, inplace=True)





#Fill missing 
df.loc[:, 'Current Year Upto Month End'] = (
    df['Current Year Upto Month End'].fillna(df['Current Year Upto Month End'].median())
)
df.loc[:, 'Corresponding Month Previous Year'] = (
    df['Corresponding Month Previous Year'].fillna(df['Corresponding Month Previous Year'].median())
)

df.loc[:, 'Previous Month'] = (
    df['Previous Month'].fillna(df['Previous Month'].median())
)
df.loc[:, 'Current Month'] = (
    df['Current Month'].fillna(df['Current Month'].median())
)

print(df.isnull().sum())
print(df.head())

#Grouping data by 'Heads Crime' and summing up the numeric columns

df_Heads_Crime = df.groupby('Heads Crime', as_index=False).agg({ 'Current Year Upto Month End': 'sum',
                                                    'Corresponding Month Previous Year': 'sum',
                                                    'Previous Month': 'sum',
                                                    'Current Month': 'sum'})


print(df_Heads_Crime)

# Convert numeric columns
num_cols = ["Current Year Upto Month End", "Corresponding Month Previous Year", "Previous Month", "Current Month"]
df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')


# Major heads analysis for ppt

df["Major Heads"] = df["Major Heads"].astype(str).str.replace("\n", " ", regex=False)
df["Major Heads"] = df["Major Heads"].str.replace("\r", " ", regex=False)
df["Major Heads"] = df["Major Heads"].str.strip()

freq = df["Major Heads"].value_counts().to_dict()

wc = WordCloud(
    width=1600,
    height=800,
    background_color="white"
).generate_from_frequencies(freq)

plt.figure(figsize=(14, 7))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.show()

df["Major Heads"] = (
    df["Major Heads"]
    .astype(str)
    .str.replace("\n", " ", regex=False)
    .str.replace("\r", " ", regex=False)
    .str.strip()
)


crime_counts = df_Heads_Crime.set_index('Heads Crime')['Current Month']






# Bar chart for top 20 crimes by Heads Crime (current month)
top20_heads = df_Heads_Crime.sort_values(by='Current Month', ascending=False).head(20)
plt.figure(figsize=(12, 8))
top20_heads.set_index('Heads Crime')['Current Month'].sort_values().plot(
    kind="barh",    
    color='blue',
    fontsize=12
)   
plt.title("Top Crimes by Heads Crime (Current Month)", fontsize=16)
plt.xlabel("Number of Crimes", fontsize=14)
plt.ylabel("Heads Crime", fontsize=14)
plt.tight_layout()
plt.show()

import matplotlib.pyplot as plt
import pandas as pd

# Sort the data for better readability and a clear ranking
crime_counts_sorted = crime_counts.sort_values(ascending=True)

# Create the figure
plt.figure(figsize=(10, 8))

# Plot the horizontal bar chart
ax = crime_counts_sorted.plot(
    kind='barh',
    color='#1f77b4', # Use a single, professional color
    edgecolor='black',
    zorder=3 # Bring bars forward
)

# Add titles and labels
plt.title("Crime Distribution by Heads Crime (Current Month)", fontsize=16, fontweight='bold', pad=15)
plt.xlabel("Number of Crimes (Current Month)", fontsize=12)
plt.ylabel("Heads Crime", fontsize=12)

# Add data labels to the bars
for i, v in enumerate(crime_counts_sorted):
    # Place text slightly to the right of the bar's end
    ax.text(v + (crime_counts_sorted.max() * 0.01), i, str(v), 
            color='black', va='center', fontweight='bold')

# Add subtle grid lines for comparison
ax.grid(axis='x', linestyle='--', alpha=0.7, zorder=0)

# Remove the top and right spines for a cleaner, modern look
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

plt.tight_layout()
plt.show()



# Bar chart for top 20 Major Heads
top20 = df["Major Heads"].value_counts().head(20)
plt.figure(figsize=(12, 8))

top20.sort_values().plot(
    kind="barh",
    fontsize=12
)
plt.title("Top 20 Major Heads (Frequency)", fontsize=16)
plt.xlabel("Count", fontsize=14)
plt.ylabel("Major Heads", fontsize=14)
plt.tight_layout()
plt.show()


# Line chart for crime trends over months
plt.figure(figsize=(12, 6))
plt.plot(df['Heads Crime'], df['Previous Month'], marker='o', label='Previous Month')
plt.plot(df['Heads Crime'], df['Current Month'], marker='o', label='Current Month')
plt.title("Crime Trends: Previous Month vs Current Month")
plt.xlabel("Heads Crime")
plt.ylabel("Number of Crimes")
plt.xticks(rotation=90)
plt.legend()
plt.show()


#Top 20 crimes by minor heads
plt.figure(figsize=(12, 6))
top_20_minor = df[['Minor Heads', 'Current Month']].sort_values(by='Current Month', ascending=False).head(20)
top_20_minor.set_index('Minor Heads').plot.bar(figsize=(12, 6), color='lightcoral') 
plt.title("Top 20 Crimes by Minor Heads (Current Month)")
plt.ylabel("Number of Crimes")
plt.xlabel("Minor Heads")
plt.xticks(rotation=90, ha='right')
plt.tight_layout()
plt.show()

import seaborn as sns
import matplotlib.pyplot as plt

# Bottom 20 crimes by Minor Heads
bottom_20_minor = (
    df[['Minor Heads', 'Current Month']]
    .sort_values(by='Current Month', ascending=True)
    .head(20)
)

plt.figure(figsize=(14, 6))
sns.barplot(
    data=bottom_20_minor,
    x='Minor Heads',
    y='Current Month',
    palette='coolwarm'
)

plt.title("Bottom 20 Crimes by Minor Heads (Current Month)")
plt.xlabel("Minor Heads")
plt.ylabel("Number of Crimes")
plt.xticks(rotation=90, ha='right')
plt.tight_layout()
plt.show()



# Divide data
ipc_df = df[df["Heads Crime"].str.contains("IPC", case=False, na=False)]
special_df = df[df["Heads Crime"].str.contains("Special", case=False, na=False)]
women_df = df[df["Heads Crime"].str.contains("Crimes against women", case=False, na=False)]
children_df = df[df["Heads Crime"].str.contains("Crimes against children", case=False, na=False)]
caste_df = df[df["Heads Crime"].str.contains("Castes", case=False, na=False)]
print("IPC DataFrame:")
print(ipc_df)   
print("Special crimes & laws DataFrame:")
print(special_df)
print("Cryme Against Scheduled cast DataFrame:")
print(women_df)
print("Cryme Against Women DataFrame:")
print(children_df)
print("Cryme Against children DataFrame:")
print(caste_df)

#Total Crimes by Category (Current Month)
total_ipc = ipc_df["Current Month"].sum()
total_special = special_df["Current Month"].sum()
total_women = special_df["Current Month"].sum()
total_children = special_df["Current Month"].sum()
total_caste = caste_df["Current Month"].sum()

total_ipc_prev = ipc_df["Previous Month"].sum()
total_special_prev = special_df["Previous Month"].sum()
total_women_prev = special_df["Previous Month"].sum()
total_children_prev = special_df["Previous Month"].sum()
total_caste_prev = caste_df["Previous Month"].sum()

crime_groups = {
    "IPC": ipc_df,
    "Special Laws": special_df,
    "Crime against Women" : women_df,
    "Crime against Women" : children_df,
    "Caste" : caste_df,
}

print("Total IPC Crimes:", total_ipc)
print("Total Special Crimes:", total_special)
print("Total Crimes against Women:", total_women)
print("Total Crimes against Children:", total_children)
print("Total crime against Sheduled Castes and Tribes",total_caste)

print("Total IPC Crimes:", total_ipc_prev)
print("Total Special Crimes:", total_special_prev)
print("Total Crimes against Women:", total_women_prev)
print("Total Crimes against Children:", total_children_prev)
print("Total crime against Sheduled Castes and Tribes",total_caste_prev)


# Save cleaned data
df.to_csv("cleaned_crime_data_sept_2025.csv", index=False)


#Data vizualizations
# IPC vs Special vs Women vs Children vs Caste (Current Month)

categories = ["IPC", "SPECIAL", "WOMEN","CHILDREN", "CASTE"]
values = [total_ipc, total_special, total_women, total_children, total_caste]
plt.figure(figsize=(8,6))
plt.bar(categories, values)
plt.bar(categories, values, color=["#E70606", "#058529", "#F3C455", "#1A1596","#96371595" ])
plt.title("IPC vs Sll crimes vs v.Women vs v.Children vs v.Tribes(Current Month)")
plt.xlabel("Crime Category")
plt.ylabel("Total Crimes")
plt.grid(axis='y', linestyle='--', alpha=0.4)
plt.show()

# IPC vs Special vs Women vs Children vs Caste (Previous Month)
categories = ["IPC", "SPECIAL", "WOMEN","CHILDREN", "CASTE"]
values = [total_ipc_prev, total_special_prev, total_women_prev, total_children_prev, total_caste_prev]
plt.figure(figsize=(8,6))
plt.bar(categories, values)
plt.bar(categories, values, color=["#E70606", "#058529", "#F3C455", "#1A1596","#96371595" ])
plt.title("IPC vs Sll vs v.Women vs v.Children vs v.Tribes(Previous Month)")
plt.xlabel("Crime Category")
plt.ylabel("Total Crimes")
plt.grid(axis='y', linestyle='--', alpha=0.4)
plt.show()

# Previous Vs Current Month Comparison
categories = ["IPC", "SPECIAL", "WOMEN", "CHILDREN", "CASTE"]


current_values = [total_ipc, total_special, total_women, total_children, total_caste]
previous_values = [total_ipc_prev, total_special_prev, total_women_prev, total_children_prev, total_caste_prev]


df = pd.DataFrame({
    "Category": categories,
    "Current Month": current_values,
    "Previous Month": previous_values
})


df_melted = df.melt(
    id_vars="Category",
    value_vars=["Current Month", "Previous Month"],
    var_name="Month",
    value_name="Total Crimes"
)


plt.figure(figsize=(10,6))
sns.barplot(
    data=df_melted,
    x="Category",
    y="Total Crimes",
    hue="Month"
)

plt.title("Crime Comparison: Current vs Previous Month")
plt.xlabel("Crime Category")
plt.ylabel("Total Crimes")
plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.tight_layout()
plt.show()




# IPC vs SLL vs Caste vs women vs Children(All Months)
# ipc_total_all = ipc_df[["Current Year Upto Month End", "Corresponding Month Previous Year", "Previous Month", "Current Month"]].sum().sum()
# special_total_all = special_df[["Current Year Upto Month End", "Corresponding Month Previous Year", "Previous Month", "Current Month"]].sum().sum()
# women_total_all = women_df[["Current Year Upto Month End", "Corresponding Month Previous Year", "Previous Month", "Current Month"]].sum().sum()
# children_total_all = children_df[["Current Year Upto Month End", "Corresponding Month Previous Year", "Previous Month", "Current Month"]].sum().sum()
# caste_total_all = caste_df[["Current Year Upto Month End", "Corresponding Month Previous Year", "Previous Month", "Current Month"]].sum().sum()
# categories_all = ["IPC", "Special", "Women", "Children", "Caste"]
# values_all = [ipc_total_all, special_total_all, women_total_all, children_total_all, caste_total_all]
# plt.figure(figsize=(12,12))
# plt.bar(categories_all, values_all, color=["#E70606", "#058529", "#F3C455", "#1A1596","#96371595"])
# plt.title("Comparison of IPC vs SLL vs Cyber Crimes (All Months)")
# plt.xlabel("Crime Category")
# plt.ylabel("Total Crimes")
# plt.grid(axis='y', linestyle='--', alpha=0.4)
# plt.show()










# Summary Observations for PPT



#1. Highest crime causes this month

# Due to Other Causes → 66

# Sudden Quarrel → 11

# Love Intrigue → 4

# Due to Personal Vendetta → 8

# Property dispute → 7

# 2. Low or zero crime causes

# Witchcraft

# Terrorism/Naxalism

# Political reasons

# Casteism

# Professional killings

# Custodial crimes

# These categories remain either 0 or extremely low.

# 3. Month-over-Month Increase

# These increased noticeably:

# Minor Head	Previous	Current
# Sudden Quarrel	6	11
# Revenge/Enmity	4	1
# Due to Personal Vendetta (Attempt to Murder)	1	8
# 4. Correlation Observations

# Strong positive correlation between:

# Current Month vs Previous Month

# Current Year Upto Month vs Current Month

# This means categories that have high yearly totals generally have high current-month values too.
















# plt.figure(figsize=(12, 8))
# sns.barplot(data=df, x='Heads Crime', y='Current Month', hue='Heads Crime', palette='viridis', legend=False)
# plt.title('Current Month Crime Counts by Heads Crime')
# plt.xlabel('Heads Crime')
# plt.ylabel('Current Month Crime Counts')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()




