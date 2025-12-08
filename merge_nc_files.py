import xarray as xr
import numpy as np
import pandas as pd

input_files = [
    "ERA_data/data_stream-moda_stepType-avgad.nc",
    "ERA_data/data_stream-moda_stepType-avgid.nc",
    "ERA_data/data_stream-moda_stepType-avgua.nc",
]

def normalize_and_prepare_dataset(path):
    print(f"Loading: {path}")
    ds = xr.open_dataset(path)

    # Drop completely-empty data variables
    empty_vars = [v for v in ds.data_vars if ds[v].isnull().all().item()]
    if empty_vars:
        print(f"  Dropping empty variables in {path}: {empty_vars}")
        ds = ds.drop_vars(empty_vars)

    # Rename 'valid_time' coordinate/dimension to 'time'
    # This preserves the dimension while giving it the canonical name
    if "valid_time" in ds.coords or "valid_time" in ds.dims:
        print("  Renaming 'valid_time' -> 'time'")
        ds = ds.rename({"valid_time": "time"})

    if "time" in ds.coords:
        # sometimes times are integers/strings so we need to convert
        try:
            if not np.issubdtype(ds["time"].dtype, np.datetime64):
                ds["time"] = ("time", pd.to_datetime(ds["time"].values))
        except Exception as e:
            print("  Warning converting time to datetime:", e)

        # Normalise timestamps to hourly resolution
        ds["time"] = ("time", pd.to_datetime(ds["time"].values).round("H"))

    # Wrap lon if needed and sort coords 
    if float(ds.longitude.max()) > 180:
        lon = ds["longitude"]
        lon_wrapped = ((lon + 180) % 360) - 180
        ds = ds.assign_coords(longitude=lon_wrapped)
        ds = ds.sortby("longitude")
    if ds.latitude.values[0] > ds.latitude.values[-1]:
        ds = ds.sortby("latitude")

    return ds


# load and prepare each file
prepared = [normalize_and_prepare_dataset(p) for p in input_files]

# Align files on a common time / lat / lon grid using outer join for time
print("Aligning datasets (outer join on shared coords)...")
aligned = xr.align(*prepared, join="outer", copy=False)

# Merge aligned datasets
ds_merged = xr.merge(aligned, compat="override")  # 'override' if small attr conflicts are ok


# Save merged dataset
output_path = "./ERA_data/ERA5_merged.nc"
ds_merged.to_netcdf(output_path)
print(f"Merged dataset saved to: {output_path}")
