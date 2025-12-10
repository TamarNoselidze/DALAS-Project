import pandas as pd

# 1. Load the dataset (with the Total rows included)
df = pd.read_csv('final_data_with_total_sex_rows.csv')

# 2. Pivot the table for DEATHS
# Index: country_name, year, sex (These define the unique rows)
# Columns: disease_name (These become the new columns)
# Values: deaths
# Aggfunc: 'sum' (To combine deaths of different ICD10 codes falling under the same disease)
pivot_deaths_df = df.pivot_table(
    index=['country_name', 'year', 'sex'],
    columns='disease_name',
    values='deaths',
    aggfunc='sum',
    fill_value=0
).reset_index()

# 3. Handle the Population column
# We extract the correct population for each group separately.
# Using 'max' ensures that for the 'Total' rows (sex=3), we pick up the full 
# combined population (Male + Female).
pop_df = df.groupby(['country_name', 'year', 'sex'])['population'].max().reset_index()

# 4. Merge the population column back into the pivoted DataFrame
final_deaths_df = pd.merge(pop_df, pivot_deaths_df, on=['country_name', 'year', 'sex'])

# 5. Save the pivoted data to a CSV file
final_deaths_df.to_csv('final_data_pivoted_deaths.csv', index=False)

# Optional: Inspect the first few rows
print(final_deaths_df.head())