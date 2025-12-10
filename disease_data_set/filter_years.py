import pandas as pd

# Load the clean dataset
df = pd.read_csv('data_with_filled_names.csv')

# --- 1. Filter Years ---
df_filtered = df[df['year'] >= 2003]

# --- 2. Remove Specific Countries ---
countries_to_remove = [
    'Armenia', 'Azerbaijan', 'Tajikistan', 'Cyprus', 'Israel', 'Belarus',
    'San Marino', 'Malta', 'Turkmenistan', 'Kyrgyzstan', 'Andorra',
    'Uzbekistan', 'Kazakhstan'
]
df_filtered = df_filtered[~df_filtered['country_name'].isin(countries_to_remove)]

# --- 3. Rename Countries ---
country_renames = {
    'Russian Federation': 'Russia',
    'Republic of Moldova': 'Moldova'
}
df_filtered['country_name'] = df_filtered['country_name'].replace(country_renames)

# Save the final dataset ready for analysis
output_file_name = 'final_data_renamed.csv'
df_filtered.to_csv(output_file_name, index=False)
print(f"Finalized data saved to {output_file_name}")