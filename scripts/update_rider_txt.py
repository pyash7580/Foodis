
import random
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = os.path.join(BASE_DIR, 'RIDER_DETAILS.txt')
TEMP_PATH = os.path.join(BASE_DIR, 'RIDER_DETAILS_NEW.txt')

def generate_license(state="GJ"):
    return f"{state}{random.randint(1, 38):02d}{random.randint(10000000000, 99999999999)}"

def generate_bank_details(name):
    banks = ['HDFC', 'SBI', 'ICICI', 'Axis', 'Kotak']
    bank_name = random.choice(banks)
    acc_no = str(random.randint(10000000000, 99999999999))
    ifsc = f"{bank_name[:4].upper()}0{random.randint(100000, 999999)}"
    return bank_name, acc_no, ifsc

def process_file():
    if not os.path.exists(FILE_PATH):
        print("File not found!")
        return

    with open(FILE_PATH, 'r') as f:
        lines = f.readlines()

    new_lines = []
    
    # Header
    header = "ID    | NAME                 | EMAIL (LOGIN)                  | PASSWORD        | PHONE           | VEHICLE         | LICENSE            | ACCOUNT_HLDR         | ACCOUNT_NO      | IFSC          | BANK      | STATUS   | CITY            \n"
    separator = "=" * 230 + "\n"
    
    new_lines.append(separator)
    new_lines.append(header)
    new_lines.append(separator)

    for line in lines:
        if line.startswith('=') or line.startswith('ID') or not line.strip():
            continue
            
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 8:
            continue

        # Extract existing
        rid = parts[0]
        name = parts[1]
        email = parts[2]
        pwd = parts[3]
        phone = parts[4]
        vehicle = parts[5]
        status = parts[6]
        city = parts[7]

        # Generate new
        license_no = generate_license()
        bank, acc, ifsc = generate_bank_details(name)
        
        # Format line
        # Use simple string formatting with fixed widths for alignment similar to original
        new_line = f"{rid:<6}| {name:<21}| {email:<31}| {pwd:<16}| {phone:<16}| {vehicle:<16}| {license_no:<19}| {name:<21}| {acc:<16}| {ifsc:<14}| {bank:<10}| {status:<9}| {city:<16}\n"
        new_lines.append(new_line)

    new_lines.append(separator)
    new_lines.append(f"Total Riders: {len(new_lines) - 4}\n")

    with open(FILE_PATH, 'w') as f:
        f.writelines(new_lines)
    
    print("Successfully updated RIDER_DETAILS.txt")

if __name__ == "__main__":
    process_file()
