#!/usr/bin/env python3
import pandas as pd
import sys

def read_excel_houses(file_path):
    try:
        # Read Excel file
        df = pd.read_excel(file_path, sheet_name=None)  # Read all sheets
        
        print("Available sheets:", list(df.keys()))
        
        # Check each sheet for data
        for sheet_name, sheet_data in df.items():
            print(f"\n=== Sheet: {sheet_name} ===")
            print("Columns:", list(sheet_data.columns))
            print("Shape:", sheet_data.shape)
            
            # Look for house-related columns
            house_columns = [col for col in sheet_data.columns if any(keyword in str(col).lower() for keyword in ['nhà', 'house', 't2', 't3', 't4', 't5', 't6', 'n02'])]
            if house_columns:
                print("House-related columns found:", house_columns)
            
            # Show first few rows
            print("First 5 rows:")
            print(sheet_data.head())
            
            # Look for specific house patterns in the data
            for col in sheet_data.columns:
                if sheet_data[col].dtype == 'object':
                    unique_vals = sheet_data[col].dropna().unique()
                    house_vals = [val for val in unique_vals if any(h in str(val) for h in ['T2', 'T3', 'T4', 'T5', 'T6', 'N02'])]
                    if house_vals:
                        print(f"Houses found in column '{col}': {house_vals}")
                        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

if __name__ == "__main__":
    file_path = "attached_assets/ds trẻ em 2023_1752948027529.xlsx"
    read_excel_houses(file_path)