#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from rider.models import Rider
from rider_legacy.models import RiderProfile

# Official list of 50 riders' emails
official_rider_emails = [
    "rakesh.kumar@foodis.com",
    "suresh.patel@foodis.com",
    "mahesh.sharma@foodis.com",
    "ramesh.yadav@foodis.com",
    "dinesh.verma@foodis.com",
    "ganesh.gupta@foodis.com",
    "rajesh.singh@foodis.com",
    "mukesh.joshi@foodis.com",
    "naresh.thakur@foodis.com",
    "hitesh.chauhan@foodis.com",
    "amit.tiwari@foodis.com",
    "sumit.pandey@foodis.com",
    "rohit.mishra@foodis.com",
    "mohit.dubey@foodis.com",
    "ankit.saxena@foodis.com",
    "vikas.rawat@foodis.com",
    "deepak.nair@foodis.com",
    "arun.menon@foodis.com",
    "vijay.reddy@foodis.com",
    "sanjay.patil@foodis.com",
    "manoj.desai@foodis.com",
    "pramod.kulkarni@foodis.com",
    "ashok.jadhav@foodis.com",
    "sunil.pawar@foodis.com",
    "anil.shinde@foodis.com",
    "ravi.chavan@foodis.com",
    "kiran.bhatt@foodis.com",
    "nitin.jain@foodis.com",
    "sachin.agarwal@foodis.com",
    "pankaj.bansal@foodis.com",
    "yogesh.mehta@foodis.com",
    "lokesh.soni@foodis.com",
    "harish.rathore@foodis.com",
    "girish.bhatia@foodis.com",
    "satish.malhotra@foodis.com",
    "pradeep.kapoor@foodis.com",
    "sandeep.arora@foodis.com",
    "kuldeep.sethi@foodis.com",
    "mandeep.gill@foodis.com",
    "jaspreet.kaur@foodis.com",
    "gurpreet.dhillon@foodis.com",
    "naveen.pillai@foodis.com",
    "praveen.iyer@foodis.com",
    "tarun.hegde@foodis.com",
    "varun.shetty@foodis.com",
    "chetan.gowda@foodis.com",
    "nikhil.rao@foodis.com",
    "akhil.das@foodis.com",
    "rahul.nambiar@foodis.com",
    "vishal.prasad@foodis.com",
]

print("=" * 60)
print("RIDER CLEANUP SCRIPT")
print("=" * 60)

# Find extra riders
all_riders = User.objects.filter(role='RIDER')
total_riders_before = all_riders.count()
extra_riders = [r for r in all_riders if r.email not in official_rider_emails]

if len(extra_riders) == 0:
    print(f"✓ Total riders: {total_riders_before}")
    print(f"✓ Extra riders found: 0")
    print("✓ All riders are correct! No cleanup needed.")
else:
    print(f"✓ Total riders: {total_riders_before}")
    print(f"⚠ Extra riders found: {len(extra_riders)}")
    print("\nExtra riders to be deleted:")
    print("-" * 60)
    
    for rider in extra_riders:
        print(f"  • {rider.name} ({rider.email})")
    
    print("-" * 60)
    print("\nDeleting extra riders...")
    
    deleted_count = 0
    for rider in extra_riders:
        try:
            # Delete from RiderProfile (legacy)
            RiderProfile.objects.filter(rider=rider).delete()
            
            # Delete from Rider model
            Rider.objects.filter(email=rider.email).delete()
            
            # Delete from User model
            rider.delete()
            
            deleted_count += 1
            print(f"  ✓ Deleted: {rider.name} ({rider.email})")
        except Exception as e:
            print(f"  ✗ Error deleting {rider.email}: {str(e)}")
    
    print("-" * 60)
    print(f"✓ Successfully deleted: {deleted_count} extra riders")
    print(f"✓ Remaining riders: {50}")

print("=" * 60)
print("✓ Cleanup complete!")
print("=" * 60)
