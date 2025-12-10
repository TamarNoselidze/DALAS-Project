import pandas as pd
import numpy as np

# Load the dataset
# Adjust filename to match the output of the previous step (e.g., 'pre_clean_data_population_final.csv')
file_name = "data_with_fixed_pop.csv" 
df = pd.read_csv(file_name)

# 1. Define the ICD-10 code to disease name mapping
icd10_map = {
    'J180': 'Bronchopneumonia, unspecified',
    'J181': 'Lobar pneumonia, unspecified',
    'J182': 'Hypostatic pneumonia, unspecified',
    'J188': 'Other pneumonia, organism unspecified',
    'J189': 'Pneumonia, unspecified',
    'J390': 'Retropharyngeal and parapharyngeal abscess',
    'J391': 'Other abscess of pharynx',
    'J392': 'Other diseases of pharynx',
    'J393': 'Upper respiratory tract hypersensitivity reaction, site unspecified',
    'J398': 'Other specified diseases of upper respiratory tract',
    'J399': 'Disease of upper respiratory tract, unspecified',
    'J700': 'Acute pulmonary manifestations due to radiation',
    'J701': 'Chronic and other pulmonary manifestations due to radiation',
    'J702': 'Acute drug-induced interstitial lung disorders',
    'J703': 'Chronic drug-induced interstitial lung disorders',
    'J704': 'Drug-induced interstitial lung disorders, unspecified',
    'J708': 'Respiratory conditions due to other specified external agents',
    'J709': 'Respiratory conditions due to unspecified external agent',
    'J840': 'Alveolar and parietoalveolar conditions',
    'J841': 'Other interstitial pulmonary diseases with fibrosis',
    'J848': 'Other specified interstitial pulmonary diseases',
    'J849': 'Interstitial pulmonary disease, unspecified',
    'J860': 'Pyothorax with fistula',
    'J869': 'Pyothorax without fistula',
    'J940': 'Chylous effusion',
    'J941': 'Fibrothorax',
    'J942': 'Hemothorax',
    'J948': 'Other specified pleural conditions',
    'J949': 'Pleural condition, unspecified',
    'C34': 'Malignant neoplasm of bronchus and lung',
    'J44': 'Other chronic obstructive pulmonary disease',
    'J45': 'Asthma'
}

# 2. Convert 'disease_name' column to string, replacing empty strings/whitespace with NaN
df['disease_name'] = df['disease_name'].replace(r'^\s*$', np.nan, regex=True)

# 3. Use the mapping to fill NaN values in 'disease_name'
new_names = df['icd10_code'].map(icd10_map)
df['disease_name'] = df['disease_name'].fillna(new_names)

# 4. Save the updated DataFrame
output_file_name = "data_with_filled_names.csv"
df.to_csv(output_file_name, index=False)
print(f"Updated data saved to {output_file_name}")