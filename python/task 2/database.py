import os
import csv
from datetime import datetime

class DatabaseError(Exception):
    """Custom exception for CSV database errors."""
    pass

CSV_HEADER = ["user_name", "age", "gender", "weight_kg", "height_m", "bmi", "recorded_at"]

def init_csv(file_path):
    """Creates the CSV file with headers if it does not exist."""
    if not file_path:
        raise DatabaseError("CSV file path is empty.")
    
    try:
        # Create directory if it doesn't exist
        dir_name = os.path.dirname(file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADER)
    except IOError as e:
        raise DatabaseError(f"Failed to initialize CSV file: {e}")

def load_raw_rows(file_path):
    """Reads all rows from the CSV file, skipping the header."""
    init_csv(file_path)
    try:
        rows = []
        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None) # Skip header
            for row in reader:
                if row:  # skip empty lines
                    # Pad row if columns are missing for some reason
                    if len(row) < len(CSV_HEADER):
                        row = row + [""] * (len(CSV_HEADER) - len(row))
                    rows.append(row)
        return rows
    except IOError as e:
        raise DatabaseError(f"Failed to read CSV database: {e}")

def save_raw_rows(file_path, rows):
    """Writes the header and all provided rows back to the CSV file."""
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)
            writer.writerows(rows)
    except IOError as e:
        raise DatabaseError(f"Failed to write to CSV database: {e}")

def get_users(file_path):
    """Retrieves all unique user profiles from the CSV file."""
    rows = load_raw_rows(file_path)
    users_dict = {}
    
    for row in rows:
        name = row[0].strip()
        if not name:
            continue
            
        age_str = row[1].strip()
        gender = row[2].strip()
        
        age = int(age_str) if (age_str and age_str.isdigit()) else None
        if not gender:
            gender = "Unspecified"
            
        # Compile unique profile metadata. Keep valid entries if they exist.
        if name not in users_dict:
            users_dict[name] = {"id": name, "name": name, "age": age, "gender": gender}
        else:
            if age is not None:
                users_dict[name]["age"] = age
            if gender and gender != "Unspecified":
                users_dict[name]["gender"] = gender
                
    # Sort alphabetically by username
    return sorted(users_dict.values(), key=lambda u: u["name"].lower())

def add_user(file_path, name, age=None, gender=None):
    """Creates a new user profile by appending a placeholder row in the CSV file."""
    name_stripped = name.strip()
    if not name_stripped:
        raise DatabaseError("User name cannot be empty.")
        
    users = get_users(file_path)
    # Check duplicate (case-insensitive)
    for u in users:
        if u["name"].lower() == name_stripped.lower():
            raise DatabaseError(f"A profile with the name '{name_stripped}' already exists.")
            
    # Append profile placeholder row (weight, height, bmi, recorded_at are empty)
    age_val = str(age) if age is not None else ""
    gender_val = gender if gender else "Unspecified"
    
    rows = load_raw_rows(file_path)
    rows.append([name_stripped, age_val, gender_val, "", "", "", ""])
    save_raw_rows(file_path, rows)
    return name_stripped

def delete_user(file_path, name):
    """Deletes a user profile and all their associated records from the CSV file."""
    rows = load_raw_rows(file_path)
    # Filter out rows belonging to this user
    filtered_rows = [row for row in rows if row[0].strip().lower() != name.strip().lower()]
    save_raw_rows(file_path, filtered_rows)

def get_bmi_records(file_path, name):
    """Retrieves all BMI records for a specific user, sorted by date descending."""
    rows = load_raw_rows(file_path)
    records = []
    
    for row in rows:
        r_name = row[0].strip()
        if r_name.lower() != name.strip().lower():
            continue
            
        weight_str = row[3].strip()
        height_str = row[4].strip()
        bmi_str = row[5].strip()
        date_str = row[6].strip()
        
        # Only parse actual records (skip placeholder rows that lack weight/height/bmi/date)
        if not weight_str or not height_str or not bmi_str or not date_str:
            continue
            
        try:
            records.append({
                "id": date_str,  # Use timestamp as record ID
                "weight": float(weight_str),
                "height": float(height_str),
                "bmi": float(bmi_str),
                "date": date_str
            })
        except ValueError:
            # Skip corrupted rows silently
            continue
            
    # Sort by date descending
    return sorted(records, key=lambda x: x["date"], reverse=True)

def get_all_bmi_records(file_path):
    """Retrieves all BMI records for all users, sorted by date descending."""
    rows = load_raw_rows(file_path)
    records = []
    for row in rows:
        name = row[0].strip()
        weight_str = row[3].strip()
        height_str = row[4].strip()
        bmi_str = row[5].strip()
        date_str = row[6].strip()
        if not weight_str or not height_str or not bmi_str or not date_str:
            continue
        try:
            records.append({
                "name": name,
                "weight": float(weight_str),
                "height": float(height_str),
                "bmi": float(bmi_str),
                "date": date_str
            })
        except ValueError:
            continue
    return sorted(records, key=lambda x: x["date"], reverse=True)

def add_bmi_record(file_path, name, weight_kg, height_m, bmi, recorded_at=None):
    """Adds a BMI record for a user. Replaces any placeholder row for the user if it exists."""
    if weight_kg <= 0 or height_m <= 0:
        raise DatabaseError("Weight and height must be positive values.")
        
    users = get_users(file_path)
    user_meta = next((u for u in users if u["name"].lower() == name.lower()), None)
    if not user_meta:
        raise DatabaseError(f"User profile '{name}' not found.")
        
    age_val = str(user_meta["age"]) if user_meta["age"] is not None else ""
    gender_val = user_meta["gender"]
    
    recorded_at_str = recorded_at if recorded_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    rows = load_raw_rows(file_path)
    
    # Check if there's a placeholder row for this user (where weight, height, bmi, and date are empty)
    # and remove it to keep the file clean.
    new_rows = []
    for r in rows:
        r_name = r[0].strip()
        if r_name.lower() == name.lower():
            # If it's a placeholder row, discard it
            is_placeholder = (not r[3].strip() and not r[4].strip() and not r[5].strip() and not r[6].strip())
            if is_placeholder:
                continue
        new_rows.append(r)
        
    # Append the new record row
    new_rows.append([
        name, 
        age_val, 
        gender_val, 
        f"{weight_kg:.2f}", 
        f"{height_m:.4f}", 
        f"{bmi:.2f}", 
        recorded_at_str
    ])
    
    save_raw_rows(file_path, new_rows)
    return recorded_at_str

def delete_bmi_record(file_path, name, recorded_at):
    """Deletes a single BMI record matching the username and recorded timestamp."""
    rows = load_raw_rows(file_path)
    
    # Filter out the specific record
    new_rows = []
    deleted = False
    for r in rows:
        r_name = r[0].strip()
        r_date = r[6].strip()
        if r_name.lower() == name.lower() and r_date == recorded_at:
            deleted = True
            continue
        new_rows.append(r)
        
    # If we deleted the only record, we should write back a placeholder row so the profile isn't lost!
    users = get_users(file_path)
    user_meta = next((u for u in users if u["name"].lower() == name.lower()), None)
    
    # Check if user has any other rows left
    has_other_rows = any(r[0].strip().lower() == name.lower() for r in new_rows)
    if not has_other_rows and user_meta:
        age_val = str(user_meta["age"]) if user_meta["age"] is not None else ""
        gender_val = user_meta["gender"]
        new_rows.append([name, age_val, gender_val, "", "", "", ""])
        
    save_raw_rows(file_path, new_rows)
