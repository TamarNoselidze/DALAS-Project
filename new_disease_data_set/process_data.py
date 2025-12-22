import pandas as pd


input_path = "IHME-GBD_2023_DATA-ac7bf47f-1.csv"
output_path = "GBD_data.csv"


df = pd.read_csv(input_path)

df["sex"] = df["sex"].str.lower()

# Create pivot table
pivot_df = df.pivot_table(
    index=["measure", "location", "year"],
    columns=["cause", "sex"],
    values=["val", "upper", "lower"]
)


# Flatten index into columns
flattened_df = pivot_df.reset_index()

# Create clear, consistent column names
# Format: cause_stat_sex
clean_columns = []

for col in flattened_df.columns:
    if isinstance(col, tuple):
        stat, cause, sex = col
        clean_columns.append(f"{cause}_{stat}_{sex}")
    else:
        clean_columns.append(col.capitalize())

flattened_df.columns = clean_columns


countries_map = {
    # 'Saint Vincent and the Grenadines': 'St. Vin. and Gren.',
    # 'Equatorial Guinea': 'Eq. Guinea',
    # 'Türkiye': 'Turkey',
    'Democratic Republic of the Congo': 'Dem. Rep. Congo',
    # 'Eswatini': 'eSwatini',
    'Iran (Islamic Republic of)': 'Iran',
    # 'Solomon Islands': 'Solomon Is.',
    # 'Sao Tome and Principe': 'São Tomé and Principe',
    'United Republic of Tanzania': 'Tanzania',
    "Lao People's Democratic Republic": 'Laos',
    'Russian Federation': 'Russia',
    'Syrian Arab Republic': 'Syria',
    'Bolivia (Plurinational State of)': 'Bolivia',
    'Venezuela (Bolivarian Republic of)': 'Venezuela',
    'Republic of Korea': 'South Korea',
    # 'Antigua and Barbuda': 'Antigua and Barb.',
    "Democratic People's Republic of Korea": 'North Korea',
    # 'Dominican Republic': 'Dominican Rep.',
    # 'United States Virgin Islands': 'U.S. Virgin Is.',
    # 'Central African Republic': 'Central African Rep.',
    'Brunei Darussalam': 'Brunei',
    # 'Bosnia and Herzegovina': 'Bosnia and Herz.',
    'Republic of Moldova': 'Moldova',
    'Viet Nam': 'Vietnam'
}


flattened_df['_location_'] = flattened_df['_location_'].replace(countries_map)


flattened_df.drop(columns=["_measure_"], axis=1, inplace=True)

column_rename_map = {
    '_location_' : 'country_name',
    '_year_' : 'year',
    'Asthma_lower_female': 'asthma_lo_F',
    'Asthma_lower_male': 'asthma_lo_M',
    'Chronic obstructive pulmonary disease_lower_female': 'copd_lo_F',
    'Chronic obstructive pulmonary disease_lower_male': 'copd_lo_M',
    'Lower respiratory infections_lower_female': 'lri_lo_F',
    'Lower respiratory infections_lower_male': 'lri_lo_M',
    'Tracheal, bronchus, and lung cancer_lower_female': 'lung_cancer_lo_F',
    'Tracheal, bronchus, and lung cancer_lower_male': 'lung_cancer_lo_M',
    'Asthma_upper_female': 'asthma_up_F',
    'Asthma_upper_male': 'asthma_up_M',
    'Chronic obstructive pulmonary disease_upper_female': 'copd_up_F',
    'Chronic obstructive pulmonary disease_upper_male': 'copd_up_M',
    'Lower respiratory infections_upper_female': 'lri_up_F',
    'Lower respiratory infections_upper_male': 'lri_up_M',
    'Tracheal, bronchus, and lung cancer_upper_female': 'lung_cancer_up_F',
    'Tracheal, bronchus, and lung cancer_upper_male': 'lung_cancer_up_M',
    'Asthma_val_female': 'asthma_F',
    'Asthma_val_male': 'asthma_M',
    'Chronic obstructive pulmonary disease_val_female': 'copd_F',
    'Chronic obstructive pulmonary disease_val_male': 'copd_M',
    'Lower respiratory infections_val_female': 'lri_F',
    'Lower respiratory infections_val_male': 'lri_M',
    'Tracheal, bronchus, and lung cancer_val_female': 'lung_cancer_F',
    'Tracheal, bronchus, and lung cancer_val_male': 'lung_cancer_M'
}


flattened_df = flattened_df.rename(columns=column_rename_map)

flattened_df = flattened_df.sort_values(by=['country_name', 'year'], ascending=True)

flattened_df.to_csv(output_path, index=False)

