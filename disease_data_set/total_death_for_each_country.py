
import pandas as pd
import numpy as np

# 1. Load the dataset
df = pd.read_csv('final_data_post_2003 (3).csv')

# 2. Filter for Male (1) and Female (2) to calculate the Total
# We exclude existing aggregate rows if any (like sex=9) from this calculation
subset = df[df['sex'].isin([1, 2])]

# 3. Group by the key identifiers to sum deaths and population
# Keys: country_name, year, disease_name, icd10_code
grouped = subset.groupby(
    ['country_name', 'year', 'disease_name', 'icd10_code'], 
    as_index=False
)[['deaths', 'population']].sum()

# 4. Calculate the new mortality rate
# Formula: (Total Deaths / Total Population) * 100,000
grouped['mortality_rate_per_100k'] = grouped.apply(
    lambda row: (row['deaths'] / row['population'] * 100000) 
    if (pd.notnull(row['population']) and row['population'] > 0) 
    else np.nan, 
    axis=1
)

# 5. Assign the new sex identifier '3' for "Both Sexes"
grouped['sex'] = 3

# 6. Ensure columns match the original DataFrame order
grouped = grouped[df.columns]

# 7. Concatenate the new rows with the original DataFrame
final_df = pd.concat([df, grouped], ignore_index=True)

# 8. Sort the data for better readability
final_df = final_df.sort_values(by=['country_name', 'year', 'disease_name', 'sex'])

# 9. Save the result to a new CSV file
final_df.to_csv('final_data_with_total_sex_rows.csv', index=False)

# Optional: Inspect the result
print("New rows added:")
print(final_df[final_df['sex'] == 3].head())