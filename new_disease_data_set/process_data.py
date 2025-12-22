import pandas as pd

df = pd.read_csv("IHME-GBD_2023_DATA-ac7bf47f-1.csv")

df["sex"] = df["sex"].str.lower()

# Create pivot table
pivot_df = df.pivot_table(
    index=["measure", "location", "year"],
    columns=["cause", "sex"],
    values=["val", "upper", "lower"]
)


# Flatten index into columns
final_df = pivot_df.reset_index()

# -----------------------------
# Create clear, consistent column names
# Format: cause_stat_sex
# -----------------------------
clean_columns = []

for col in final_df.columns:
    if isinstance(col, tuple):
        stat, cause, sex = col
        clean_columns.append(f"{cause}_{stat}_{sex}")
    else:
        clean_columns.append(col.capitalize())

final_df.columns = clean_columns


final_df.to_csv("transformed_gbd_data_2.csv", index=False)

