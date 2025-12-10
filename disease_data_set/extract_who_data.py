import pandas as pd
import glob
import numpy as np

# --- Load all WHO MortIcd10 files correctly ---
# Finds all files matching the pattern
mort_files = glob.glob("Morticd10_part*.csv")

all_parts = []
for f in mort_files:
    # autodetect delimiter (, or ;) and encoding
    try:
        df = pd.read_csv(f, sep=None, engine="python", encoding="latin1", dtype=str, on_bad_lines="skip")
        print(f"Loaded {f}: {df.shape[0]} rows, {df.shape[1]} cols")
        all_parts.append(df)
    except Exception as e:
        print(f"Error loading {f}: {e}")

# Combine all into one big DataFrame
deaths = pd.concat(all_parts, ignore_index=True)
print("✅ Combined shape:", deaths.shape)

# --- Step 1: Compute total deaths ---
deaths.columns = deaths.columns.str.lower()

# Detect all age-specific death columns dynamically
death_cols = [c for c in deaths.columns if c.startswith("deaths")]

# Convert to numeric and sum
for c in death_cols:
    deaths[c] = pd.to_numeric(deaths[c], errors="coerce").fillna(0)
deaths["total_deaths"] = deaths[death_cols].sum(axis=1)

# --- Step 2: Filter respiratory-related causes ---
deaths["cause"] = deaths["cause"].astype(str).str.upper().str.strip()

# Respiratory categories
resp_letter_codes = [f"J{str(i).zfill(2)}" for i in range(0,100)]  # J00–J99
lung_cancer_codes = ["C33","C34"]
resp_numeric = ["1072", "1034"]  # numeric list equivalents

deaths = deaths[
    deaths["cause"].str.startswith("J", na=False)
    | deaths["cause"].isin(lung_cancer_codes + resp_numeric)
]

# --- Step 3: Disease mapping ---
def map_disease(code):
    code = str(code)
    if code in ["1072"]: return "Respiratory diseases (WHO list code)"
    if code in ["1034"]: return "Lung cancer (WHO list code)"
    if code.startswith(("J45","J46")): return "Asthma"
    if code.startswith(("J40","J41","J42","J43","J44")): return "COPD"
    if code.startswith("J00") or (code.startswith("J0") and code < "J07"): return "Acute upper respiratory infections"
    if "J09" <= code <= "J18": return "Influenza and pneumonia"
    if "J20" <= code <= "J22": return "Other acute lower respiratory infections"
    if "J30" <= code <= "J39": return "Other diseases of upper respiratory tract"
    if code == "J47": return "Bronchiectasis"
    if "J60" <= code <= "J70": return "Lung diseases due to external agents"
    if "J80" <= code <= "J84": return "Interstitial respiratory diseases"
    if "J85" <= code <= "J86": return "Suppurative and necrotic conditions"
    if "J90" <= code <= "J94": return "Diseases of pleura"
    if "J95" <= code <= "J99": return "Other diseases of the respiratory system"
    if code in ["C33","C34"]: return "Lung cancer"
    return None

deaths["disease_name"] = deaths["cause"].apply(map_disease)

# --- Step 4: Keep and clean relevant columns ---
cols_keep = ["country","year","sex","cause","disease_name","total_deaths"]
deaths = deaths[[c for c in cols_keep if c in deaths.columns]]
deaths["year"] = pd.to_numeric(deaths["year"], errors="coerce").astype("Int64")
deaths = deaths.dropna(subset=["year"])

# --- Step 5: Load population ---
pop = pd.read_csv("Pop.csv", dtype=str)
pop.columns = pop.columns.str.lower()
pop_cols = [c for c in pop.columns if c.startswith("pop")]
for c in pop_cols:
    pop[c] = pd.to_numeric(pop[c], errors="coerce").fillna(0)
pop["population"] = pop[pop_cols].sum(axis=1)
pop = pop[["country","year","sex","population"]]
pop["year"] = pd.to_numeric(pop["year"], errors="coerce")

# --- Step 6: Country mapping ---
countries = pd.read_csv("Country_codes.csv", dtype=str)
countries.columns = countries.columns.str.lower()
if "name" in countries.columns:
    countries = countries.rename(columns={"name": "country_name"})
elif "countryname" in countries.columns:
    countries = countries.rename(columns={"countryname": "country_name"})
if "country" not in countries.columns:
    countries = countries.rename(columns={countries.columns[0]: "country"})

# --- Step 7: Merge ---
merged = (
    deaths
    .merge(pop, on=["country","year","sex"], how="left", suffixes=("","_pop"))
    .merge(countries, on="country", how="left", suffixes=("","_ctry"))
)

# --- Step 8: Compute mortality rates ---
merged["population"] = pd.to_numeric(merged["population"], errors="coerce")
merged["mortality_rate_per_100k"] = merged["total_deaths"] / merged["population"] * 100000

# --- Step 9: Build final dataset ---
final = merged.rename(columns={
    "cause": "icd10_code",
    "total_deaths": "deaths"
})[["country_name","year","sex","disease_name","icd10_code","deaths","population","mortality_rate_per_100k"]]

# --- Step 10: Filter for European countries ---
europe_countries = {
    "Albania","Andorra","Armenia","Austria","Azerbaijan","Belarus","Belgium",
    "Bosnia and Herzegovina","Bulgaria","Croatia","Cyprus","Czech Republic",
    "Denmark","Estonia","Finland","France","Georgia","Germany","Greece",
    "Hungary","Iceland","Ireland","Israel","Italy","Kazakhstan","Kyrgyzstan",
    "Latvia","Lithuania","Luxembourg","Malta","Monaco","Montenegro",
    "Netherlands","North Macedonia","Norway","Poland","Portugal","Republic of Moldova",
    "Romania","Russian Federation","San Marino","Serbia","Slovakia","Slovenia",
    "Spain","Sweden","Switzerland","Tajikistan","Turkey","Turkmenistan",
    "Ukraine","United Kingdom","Uzbekistan"
}
final = final[final["country_name"].isin(europe_countries)]

# --- Step 11: Sort and Save ---
final = final.sort_values(by=["year","country_name"], ascending=[False, True]).reset_index(drop=True)
final.to_csv("WHO_respiratory_mortality_Europe.csv", index=False)
print("✅ Saved WHO_respiratory_mortality_Europe.csv")