#!/usr/bin/env python3
import pandas as pd

def check_for_t2_and_n02():
    # Read the Excel file more thoroughly
    df = pd.read_excel("attached_assets/ds trẻ em 2023_1752948027529.xlsx", sheet_name=0)
    
    print("Looking for T2 and N02 house data...")
    
    # Look for T2 section
    t2_found = False
    n02_found = False
    
    for idx, row in df.iterrows():
        for col_idx, cell in enumerate(row):
            cell_str = str(cell) if pd.notna(cell) else ""
            
            if "T2" in cell_str and "NHÀ" in cell_str:
                print(f"Found T2 reference at row {idx}, col {col_idx}: {cell_str}")
                t2_found = True
                
                # Check the next few rows for student data
                for next_idx in range(idx+1, min(idx+20, len(df))):
                    next_row = df.iloc[next_idx]
                    if pd.notna(next_row.iloc[1]):
                        name = str(next_row.iloc[1]).strip()
                        if name and name != "Họ và tên" and not name.isdigit() and name != "nan":
                            print(f"  T2 Student: {name}")
            
            if "N02" in cell_str:
                print(f"Found N02 reference at row {idx}, col {col_idx}: {cell_str}")
                n02_found = True
    
    if not t2_found:
        print("No T2 house section found in the Excel file")
    if not n02_found:
        print("No N02 house section found in the Excel file")
    
    # Check if there are specific patterns we missed
    print("\nLooking for 'Bùi Thị Tiềm' (first student mentioned in headers):")
    for idx, row in df.iterrows():
        for col_idx, cell in enumerate(row):
            cell_str = str(cell) if pd.notna(cell) else ""
            if "Bùi Thị Tiềm" in cell_str:
                print(f"Found 'Bùi Thị Tiềm' at row {idx}, col {col_idx}")
                print(f"Row context: {list(row)}")

if __name__ == "__main__":
    check_for_t2_and_n02()