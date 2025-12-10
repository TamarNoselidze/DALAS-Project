import pandas as pd
import numpy as np

# --- 1. Load Data ---
# Ensure 'pre_clean_data.csv' is the output from your previous step
main_df = pd.read_csv('pre_clean_data.csv') 
ihme_sex_df = pd.read_csv('IHME_POP.csv')

# --- 2. Define Sex Mapping ---
sex_map = {
    'Male': 1,
    'Female': 2
}

# --- 3. Prepare IHME Population Data ---
ihme_pop_data = ihme_sex_df[['location', 'year', 'sex', 'val']].copy()
ihme_pop_data['sex'] = ihme_pop_data['sex'].map(sex_map)
ihme_pop_data.rename(columns={
    'location': 'country_name',
    'val': 'ihme_population'
}, inplace=True)
ihme_pop_data = ihme_pop_data[['country_name', 'year', 'sex', 'ihme_population']].drop_duplicates()

# --- 4. Prepare Main Data ---
main_df['population'] = pd.to_numeric(main_df['population'], errors='coerce')

# --- 5. Merge DataFrames ---
merged_df = pd.merge(
    main_df,
    ihme_pop_data,
    on=['country_name', 'year', 'sex'],
    how='left'
)

# --- 6. Impute Missing Population Values ---
merged_df['population'].fillna(merged_df['ihme_population'], inplace=True)

# --- 7. Recalculate Mortality Rate ---
merged_df['mortality_rate_per_100k'] = (merged_df['deaths'] / merged_df['population']) * 100000

# --- 8. Apply Rounding ---
merged_df['population'] = merged_df['population'].round().astype('Int64')

# --- 9. Final Cleanup and Save ---
merged_df.drop(columns=['ihme_population'], inplace=True)

output_filename = 'pre_clean_data_population_final.csv'
merged_df.to_csv(output_filename, index=False)
print(f"Saved imputed population data to {output_filename}")