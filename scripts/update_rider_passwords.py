import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
from rider.models import RiderProfile

def update_passwords():
    print("Starting password update from RIDER_DETAILS.txt...")
    
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'RIDER_DETAILS.txt')
    
    updated_count = 0
    not_found_count = 0
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    # Skip header lines (first 3 lines)
    for line in lines[3:]:
        if not line.strip() or line.startswith('='):
            continue
            
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 5:
            continue
            
        email = parts[2]
        password = parts[3]
        
        # Determine user based on email
        # Note: In the file, email is unique. User model connects to RiderProfile via OneToOne
        
        try:
            rider_profile = RiderProfile.objects.get(rider__email=email)
            rider_profile.password_plain = password
            rider_profile.save()
            # print(f"Updated password for {email} -> {password}")
            updated_count += 1
        except RiderProfile.DoesNotExist:
            print(f"Rider not found for email: {email}")
            not_found_count += 1
        except Exception as e:
            print(f"Error updating {email}: {e}")

    print(f"\nSummary:")
    print(f"Updated: {updated_count}")
    print(f"Not Found: {not_found_count}")

if __name__ == "__main__":
    update_passwords()
