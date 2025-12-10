import pandas as pd

# --- File Names ---
WHO_MORTALITY_FILE = "final_data_renamed.csv"
EUROSTAT_DISCHARGES_FILE = "hlth_co_disch2__custom_19049826_linear.csv"
OUTPUT_FILE = "combined_mortality_and_discharge_rates.csv"

# --- 1. Define ICD-10 Mapping Logic ---
def map_icd10_to_group(icd_code):
    """Maps granular ICD-10 codes from the WHO data to the broad Eurostat groups."""
    if pd.isna(icd_code): return None
    code = str(icd_code).upper()

    if code.startswith('C33') or code.startswith('C34'):
        return 'Malignant neoplasm of trachea, bronchus and lung'
    elif code.startswith('J0') or code.startswith('J1'):
        return 'Acute upper respiratory infections and influenza'
    elif code.startswith('J2'):
        return 'Other acute lower respiratory infections'
    elif code.startswith('J3'):
        if code.startswith(('J30', 'J31', 'J32', 'J33', 'J34', 'J36', 'J37', 'J38', 'J39')):
            return 'Other diseases of upper respiratory tract (J30-J34, J36-J39)'
        return None
    elif any(code.startswith(x) for x in ['J4','J5','J6','J7','J8','J9']):
        return 'Other lower respiratory diseases'
    return None

# --- 2. Load Data ---
df_who = pd.read_csv(WHO_MORTALITY_FILE)
df_eurostat = pd.read_csv(EUROSTAT_DISCHARGES_FILE, skiprows=[1]) # Skipping metadata row

# --- 3. Clean Eurostat Data ---
df_eurostat = df_eurostat.rename(columns={
    'geo': 'country_name',
    'TIME_PERIOD': 'year',
    'icd10': 'icd10_group_name',
    'OBS_VALUE': 'discharge_rate_per_100k'
})
df_eurostat = df_eurostat[['country_name', 'year', 'sex', 'icd10_group_name', 'discharge_rate_per_100k']].copy()

# Standardize 'sex' (Females=2, Males=1)
sex_map_eurostat = {'Females': 2, 'Males': 1}
df_eurostat = df_eurostat[df_eurostat['sex'].isin(['Females', 'Males'])].copy()
df_eurostat['sex'] = df_eurostat['sex'].map(sex_map_eurostat)

# Drop overall total group
df_eurostat = df_eurostat[df_eurostat['icd10_group_name'] != 'Diseases of the respiratory system (J00-J99)'].copy()

# --- 4. Prepare WHO Mortality Data ---
df_who = df_who[df_who['sex'].isin([1, 2])].copy()
df_who['icd10_group_name'] = df_who['icd10_code'].apply(map_icd10_to_group)
df_who_grouped = df_who.dropna(subset=['icd10_group_name']).copy()

# Aggregate WHO data to the Eurostat group level (taking the first rate found per group)
df_who_aggregated = df_who_grouped.groupby(['country_name', 'year', 'sex', 'icd10_group_name'])[['mortality_rate_per_100k']].first().reset_index()

# --- 5. Merge ---
df_combined = pd.merge(
    df_who_aggregated,
    df_eurostat,
    on=['country_name', 'year', 'sex', 'icd10_group_name'],
    how='inner'
)

# --- 6. Final Cleaning ---
sex_map_final = {1: 'Male', 2: 'Female'}
df_combined['sex'] = df_combined['sex'].map(sex_map_final)

df_final = df_combined[[
    'country_name', 'year', 'sex', 'icd10_group_name',
    'mortality_rate_per_100k', 'discharge_rate_per_100k'
]]

df_final.to_csv(OUTPUT_FILE, index=False)
print(f"Successfully generated {OUTPUT_FILE}")