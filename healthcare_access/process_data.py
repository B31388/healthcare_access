# clean_data.py
import pandas as pd

URL = "https://raw.githubusercontent.com/ongei001/healthcare-disease-dashboard/main/african_healthcare_data.csv"
df = pd.read_csv(URL)

# Standardize column names
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
df['country'] = df['country'].str.title().str.strip()

# Fill missing numeric values (should be none per schema, but safe)
num_cols = df.select_dtypes(include=['float64','int64']).columns
df[num_cols] = df[num_cols].fillna(df[num_cols].median())

# Drop the duplicated row
df = df.drop_duplicates()
print(f"Duplicate Rows After Dropping: {df.duplicated().sum()}")

# Save cleaned dataset
df.to_csv("cleaned_africa_health_data.csv", index=False)
print("Cleaned dataset saved.")
