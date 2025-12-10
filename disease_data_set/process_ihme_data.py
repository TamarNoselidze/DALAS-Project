import pandas as pd

# Define the input and output file names
INPUT_FILE = "IHME-GBD_2023_DATA-66fac8b1-1.csv" # Or "IHME.csv" based on your needs
OUTPUT_FILE = "IHME_GBD_Aggregated_Deaths.csv"

# Load the IHME GBD dataset
ihme_df = pd.read_csv(INPUT_FILE)

# 1. Filter the data to include only the 'Deaths' measure
ihme_deaths_df = ihme_df[ihme_df['measure'] == 'Deaths'].copy()

# 2. Filter for relevant metrics
ihme_deaths_df = ihme_deaths_df[ihme_deaths_df['metric'] == 'Number']

# 3. Rename columns for easier merging
ihme_deaths_df = ihme_deaths_df.rename(columns={
    'location': 'country_name',
    'val': 'gbd_deaths_total',
    'upper': 'gbd_deaths_upper',
    'lower': 'gbd_deaths_lower'
})

# 4. Aggregate the data by summing the modeled deaths (val) across all age groups
agg_gbd_deaths = ihme_deaths_df.groupby(['country_name', 'year', 'sex', 'cause']).agg(
    gbd_deaths_total=('gbd_deaths_total', 'sum'),
    gbd_deaths_upper_sum=('gbd_deaths_upper', 'sum'),
    gbd_deaths_lower_sum=('gbd_deaths_lower', 'sum')
).reset_index()

# 5. Output the aggregated and cleaned data
agg_gbd_deaths.to_csv(OUTPUT_FILE, index=False)
print(f"Successfully aggregated data and saved to {OUTPUT_FILE}")