#!/usr/bin/env python3
import pandas as pd
import sqlite3

def extract_and_update_houses():
    # Read the Excel file
    df = pd.read_excel("attached_assets/ds trẻ em 2023_1752948027529.xlsx", sheet_name=0)
    
    # Initialize variables
    current_house = None
    students_data = []
    
    # Process each row to extract student names and house assignments
    for idx, row in df.iterrows():
        # Check if this row indicates a house
        first_col = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
        
        if "NHÀ T" in first_col or "NHÀ N" in first_col:
            if "T2" in first_col:
                current_house = "T2"
            elif "T3" in first_col:
                current_house = "T3"
            elif "T4" in first_col:
                current_house = "T4" 
            elif "T5" in first_col:
                current_house = "T5"
            elif "T6" in first_col:
                current_house = "T6"
            elif "N02" in first_col:
                current_house = "N02"
            print(f"Found house section: {current_house}")
            continue
            
        # Check for student names in the second column
        if pd.notna(row.iloc[1]) and current_house:
            student_name = str(row.iloc[1]).strip()
            # Skip headers and empty rows
            if student_name and student_name != "Họ và tên" and not student_name.isdigit() and student_name != "nan":
                students_data.append({
                    'name': student_name,
                    'house': current_house
                })
                print(f"Student: {student_name} -> House: {current_house}")
    
    print(f"\nTotal students found: {len(students_data)}")
    
    # Connect to database and update
    conn = sqlite3.connect('lang_huu_nghi.db')
    cursor = conn.cursor()
    
    updated_count = 0
    not_found_count = 0
    
    for student in students_data:
        # Try to find student by name (fuzzy match)
        cursor.execute("SELECT id, full_name FROM students WHERE full_name LIKE ?", (f"%{student['name']}%",))
        result = cursor.fetchone()
        
        if result:
            student_id, db_name = result
            cursor.execute("UPDATE students SET nha_chu_t_info = ? WHERE id = ?", (student['house'], student_id))
            updated_count += 1
            print(f"✓ Updated: {db_name} (ID: {student_id}) -> {student['house']}")
        else:
            not_found_count += 1
            print(f"✗ Not found: {student['name']}")
    
    conn.commit()
    conn.close()
    
    print(f"\nUpdate Summary:")
    print(f"- Students updated: {updated_count}")
    print(f"- Students not found: {not_found_count}")
    
    # Show current house distribution
    conn = sqlite3.connect('lang_huu_nghi.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nha_chu_t_info, COUNT(*) as count FROM students GROUP BY nha_chu_t_info ORDER BY nha_chu_t_info")
    
    print(f"\nCurrent house distribution:")
    for house, count in cursor.fetchall():
        print(f"- {house}: {count} students")
    
    conn.close()

if __name__ == "__main__":
    extract_and_update_houses()