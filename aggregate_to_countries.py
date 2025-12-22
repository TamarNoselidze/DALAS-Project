import xarray as xr
import numpy as np
import pandas as pd
import geopandas as gpd
import regionmask

COUNTRY_CODES = [
    'AFG', 'AGO', 'ALB', 'AND', 'ARE', 'ARG', 'ARM', 'ASM', 'ATG', 'AUS', 'AUT', 'AZE', 
    'BDI', 'BEL', 'BEN', 'BFA', 'BGD', 'BGR', 'BHR', 'BHS', 'BIH', 'BLR', 'BLZ', 'BMU', 
    'BOL', 'BRA', 'BRN', 'BTN', 'BWA', 'CAF', 'CAN', 'CHE', 'CHL', 'CHN', 'CIV', 
    'CMR', 'COD', 'COG', 'COL', 'COM', 'CPV', 'CRI', 'CUB', 'CYP', 'CZE', 'DEU', 
    'DJI', 'DNK', 'DOM', 'DZA', 'ECU', 'EGY', 'ERI', 'ESP', 'EST', 'ETH', 'FIN', 
    'FJI', 'FRA', 'GAB', 'GBR', 'GEO', 'GHA', 'GIN', 'GMB', 'GNB', 'GNQ', 'GRC', 
    'GRL', 'GTM', 'GUM', 'GUY', 'HND', 'HRV', 'HTI', 'HUN', 'IDN', 'IND', 'IRL', 
    'IRN', 'IRQ', 'ISL', 'ISR', 'ITA', 'JAM', 'JOR', 'JPN', 'KAZ', 'KEN', 'KGZ', 'KHM', 
    'KIR', 'KNA', 'KOR', 'KWT', 'LAO', 'LBN', 'LBR', 'LBY', 'LCA', 'LKA', 'LSO', 'LTU', 
    'LUX', 'LVA', 'MAR', 'MDA', 'MDG', 'MEX', 'MKD', 'MLI',  
    'MMR', 'MNE', 'MNG', 'MOZ', 'MRT', 'MUS', 'MWI', 'MYS', 'NAM', 'NER', 'NGA', 
    'NIC', 'NLD', 'NOR', 'NPL', 'NZL', 'OMN', 'PAK', 'PAN', 'PER', 'PHL', 
    'PNG', 'POL', 'PRI', 'PRK', 'PRT', 'PRY', 'PSX', 'QAT', 'ROU', 'RUS', 'RWA', 
    'SAU', 'SDN', 'SEN', 'SGP', 'SLB', 'SLE', 'SLV', 'SMR', 'SOM', 'SRB', 'STP', 
    'SUR', 'SVK', 'SVN', 'SWE', 'SWZ', 'SYC', 'SYR', 'TCD', 'TGO', 'THA', 'TJK',  
    'TKM', 'TLS', 'TON', 'TTO', 'TUN', 'TUR', 'TWN', 'TZA', 'UGA', 'UKR', 'URY', 
    'USA', 'UZB', 'VCT', 'VEN', 'VIR', 'VNM', 'VUT', 'WSM', 'YEM', 'ZAF', 'ZMB', 'ZWE'
]
ISO_COLUMN = "ADM0_A3"


# 1. LOAD DATA
def load_dataset(ds, fine_resolution=0.25) -> xr.Dataset:
    print(f"Loading dataset")
    print("  Dimensions:", dict(ds.dims))
    print("  Variables:", list(ds.data_vars))

    # print(f"Interpolating to {fine_resolution} degree grid...")
    # new_lat = np.arange(ds.latitude.min(), ds.latitude.max() + fine_resolution, fine_resolution)
    # new_lon = np.arange(ds.longitude.min(), ds.longitude.max() + fine_resolution, fine_resolution)
    
    # ds = ds.interp(latitude=new_lat, longitude=new_lon, method="linear")

    # Ensure we have a 'time' coordinate and it's datetime64
    if "time" in ds.coords and not np.issubdtype(ds["time"].dtype, np.datetime64):
        ds["time"] = ("time", pd.to_datetime(ds["time"].values))

    # Wrap longitude 0..360 -> -180..180 (in case merging changed coords)
    if float(ds.longitude.max()) > 180:
        lon = ds["longitude"]
        lon_wrapped = ((lon + 180) % 360) - 180
        ds = ds.assign_coords(longitude=lon_wrapped)
        ds = ds.sortby("longitude")
    print("  Wrapped lon min/max:", float(ds.longitude.min()), float(ds.longitude.max()))

    # Sort latitude from South -> North
    if ds.latitude.values[0] > ds.latitude.values[-1]:
        print("Sorting latitude (descending → ascending)")
        ds = ds.sortby("latitude")

    print("Lat min/max:", float(ds.latitude.min()), float(ds.latitude.max()))



    return ds



# 2. LOAD COUNTRY SHAPES (Natural Earth)
def load_countries():
    print("Loading Natural Earth country boundaries...")

    # url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    url = "https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_0_countries.zip"
    world = gpd.read_file(url)

    iso_col = ISO_COLUMN
    name_col = "NAME" if "NAME" in world.columns else "ADMIN"

    world = world[world[iso_col].isin(COUNTRY_CODES)].copy()
    world = world.to_crs("EPSG:4326")

    # Rename
    world = world.rename(columns={iso_col: "ADM0_A3", name_col: "NAME"})

    # Reset index so region numbers are 0..N-1
    world = world.reset_index(drop=True)

    found = sorted(world["ADM0_A3"].unique())
    missing = sorted(set(COUNTRY_CODES) - set(found))

    print(f"  Found {len(found)} countries: {found}")
    if missing:
        print(f"  WARNING: These codes not found in Natural Earth: {missing}")

    return world


# 3. BUILD REGION MASK & AREA WEIGHTS
def build_region_mask(ds: xr.Dataset, countries_gdf: gpd.GeoDataFrame):
    
    print("Creating region mask for the grid...")

    regions = regionmask.from_geopandas(
        countries_gdf,
        names="NAME",
        abbrevs="ADM0_A3",
        name="countries"
    )

    # mask: (latitude, longitude) with region indices (0..N-1) or NaN over ocean
    mask = regions.mask(ds.longitude, ds.latitude)
    print("Mask all NaN?:", np.isnan(mask).all())

    print("  Mask shape:", mask.shape)
    print("  Number of regions:", len(regions.names))

    return regions, mask


def compute_area_weights(ds: xr.Dataset) -> xr.DataArray:
    # Approximate grid-cell area weights as cos(latitude) (regular lat-lon grid).
    print("Computing area weights (cos(lat))...")
    lat_rad = np.deg2rad(ds["latitude"])
    weights = np.cos(lat_rad)

    return weights


# 4. AGGREGATE TO COUNTRY LEVEL
def aggregate_to_countries(ds, regions, mask, weights):

    print("Preparing 2D area weights...")
    # Broadcast weights (lat) to 2D (lat, lon) to match mask
    weights_2d = weights.broadcast_like(mask)

    n_regions = len(regions.names)
    print(f"Aggregating {n_regions} regions...")

    country_datasets = []

    for rid in range(n_regions):
        rname = regions.names[rid]
        rcode = regions.abbrevs[rid]

        # Boolean mask for this region
        region_mask = (mask == rid)

        # if not region_mask.any().item():
        if not region_mask.any().compute().item():
            print(f"  Region {rid} ({rcode}) has no grid cells, skipping.")
            continue

        # Restrict weights and data to that region
        ds_r = ds.where(region_mask)
        w_r = weights_2d.where(region_mask, 0.0)

        sample_var = list(ds.data_vars)[0]
        w_r_broadcast = w_r.broadcast_like(ds_r[sample_var]).fillna(0.0)

        # Now weights have no NaNs, only 0 outside the country
        ds_mean = ds_r.weighted(w_r_broadcast).mean(dim=("latitude", "longitude"))
        ds_mean = ds_mean.compute()
        
        ds_mean = ds_mean.assign_coords(
            country_code=rcode,
            country_name=rname,
        )

        country_datasets.append(ds_mean)

    if not country_datasets:
        raise RuntimeError(
            "No regions had any grid cells with data. "
            "Check region definitions and domain."
        )

    ds_country = xr.concat(country_datasets, dim="country")
    print("  Final aggregated dataset dimensions:", dict(ds_country.dims))

    return ds_country


# 5. CONVERT TO DATAFRAME
def to_tidy_dataframe(ds_country: xr.Dataset, cams=False) -> pd.DataFrame:
    # Convert country x time x variable dataset to tidy DataFrame.

    print("Converting aggregated dataset to DataFrame...")

    # Move all coords into DataFrame
    df = ds_country.to_dataframe().reset_index()
    df = df[df["country_code"].isin(COUNTRY_CODES)].copy()
    if "time" not in df.columns:
        if cams:
            df = df.rename(columns={'valid_time' : 'time'})
        else:
            raise RuntimeError("No 'time' column present after aggregation. Check time coordinate.")
    if not np.issubdtype(df["time"].dtype, np.datetime64):
        df["time"] = pd.to_datetime(df["time"])

    df = df[df["country_code"].isin(COUNTRY_CODES)].copy()

    # Add year/month
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month

    # Reorder columns to have identifiers first
    id_cols = ["country_code", "country_name", "time", "year", "month"]
    other_cols = [c for c in df.columns if c not in id_cols + ["country"]]

    df = df[id_cols + other_cols]

    print("  Final DataFrame shape:", df.shape)
    print("  Variables in DataFrame:", [c for c in other_cols if c not in ("country")])

    return df





if __name__ == "__main__":
    # path = './axali_cams/data_allhours_sfc.nc'
    path = './till2011/ERA5_merged_11.nc'

    # output_csv = "CAMS_aggregated_axali.csv"
    output_csv = "ERA5_aggregated_plstn.csv"

    # raw_dataset = xr.open_dataset(path)
    raw_dataset = xr.open_dataset(path, chunks={'time': 400})

    ds = load_dataset(raw_dataset)

    countries = load_countries()

    regions, mask = build_region_mask(ds, countries)

    weights = compute_area_weights(ds)

    ds_country = aggregate_to_countries(ds, regions, mask, weights)

    df = to_tidy_dataframe(ds_country, cams=True)

    print(f"Saving CSV to: {output_csv}")
    df.to_csv(output_csv, index=False)

