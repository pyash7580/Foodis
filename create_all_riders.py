#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from rider.models import Rider
from rider_legacy.models import RiderProfile
from django.contrib.auth.hashers import make_password

# List of all 50 riders
riders_data = [
    ("Rakesh Kumar", "rakesh.kumar@foodis.com", "Rakesh@"),
    ("Suresh Patel", "suresh.patel@foodis.com", "Suresh@"),
    ("Mahesh Sharma", "mahesh.sharma@foodis.com", "Mahesh@"),
    ("Ramesh Yadav", "ramesh.yadav@foodis.com", "Ramesh@"),
    ("Dinesh Verma", "dinesh.verma@foodis.com", "Dinesh@"),
    ("Ganesh Gupta", "ganesh.gupta@foodis.com", "Ganesh@"),
    ("Rajesh Singh", "rajesh.singh@foodis.com", "Rajesh@"),
    ("Mukesh Joshi", "mukesh.joshi@foodis.com", "Mukesh@"),
    ("Naresh Thakur", "naresh.thakur@foodis.com", "Naresh@"),
    ("Hitesh Chauhan", "hitesh.chauhan@foodis.com", "Hitesh@"),
    ("Amit Tiwari", "amit.tiwari@foodis.com", "Amit@"),
    ("Sumit Pandey", "sumit.pandey@foodis.com", "Sumit@"),
    ("Rohit Mishra", "rohit.mishra@foodis.com", "Rohit@"),
    ("Mohit Dubey", "mohit.dubey@foodis.com", "Mohit@"),
    ("Ankit Saxena", "ankit.saxena@foodis.com", "Ankit@"),
    ("Vikas Rawat", "vikas.rawat@foodis.com", "Vikas@"),
    ("Deepak Nair", "deepak.nair@foodis.com", "Deepak@"),
    ("Arun Menon", "arun.menon@foodis.com", "Arun@"),
    ("Vijay Reddy", "vijay.reddy@foodis.com", "Vijay@"),
    ("Sanjay Patil", "sanjay.patil@foodis.com", "Sanjay@"),
    ("Manoj Desai", "manoj.desai@foodis.com", "Manoj@"),
    ("Pramod Kulkarni", "pramod.kulkarni@foodis.com", "Pramod@"),
    ("Ashok Jadhav", "ashok.jadhav@foodis.com", "Ashok@"),
    ("Sunil Pawar", "sunil.pawar@foodis.com", "Sunil@"),
    ("Anil Shinde", "anil.shinde@foodis.com", "Anil@"),
    ("Ravi Chavan", "ravi.chavan@foodis.com", "Ravi@"),
    ("Kiran Bhatt", "kiran.bhatt@foodis.com", "Kiran@"),
    ("Nitin Jain", "nitin.jain@foodis.com", "Nitin@"),
    ("Sachin Agarwal", "sachin.agarwal@foodis.com", "Sachin@"),
    ("Pankaj Bansal", "pankaj.bansal@foodis.com", "Pankaj@"),
    ("Yogesh Mehta", "yogesh.mehta@foodis.com", "Yogesh@"),
    ("Lokesh Soni", "lokesh.soni@foodis.com", "Lokesh@"),
    ("Harish Rathore", "harish.rathore@foodis.com", "Harish@"),
    ("Girish Bhatia", "girish.bhatia@foodis.com", "Girish@"),
    ("Satish Malhotra", "satish.malhotra@foodis.com", "Satish@"),
    ("Pradeep Kapoor", "pradeep.kapoor@foodis.com", "Pradeep@"),
    ("Sandeep Arora", "sandeep.arora@foodis.com", "Sandeep@"),
    ("Kuldeep Sethi", "kuldeep.sethi@foodis.com", "Kuldeep@"),
    ("Mandeep Gill", "mandeep.gill@foodis.com", "Mandeep@"),
    ("Jaspreet Kaur", "jaspreet.kaur@foodis.com", "Jaspreet@"),
    ("Gurpreet Dhillon", "gurpreet.dhillon@foodis.com", "Gurpreet@"),
    ("Naveen Pillai", "naveen.pillai@foodis.com", "Naveen@"),
    ("Praveen Iyer", "praveen.iyer@foodis.com", "Praveen@"),
    ("Tarun Hegde", "tarun.hegde@foodis.com", "Tarun@"),
    ("Varun Shetty", "varun.shetty@foodis.com", "Varun@"),
    ("Chetan Gowda", "chetan.gowda@foodis.com", "Chetan@"),
    ("Nikhil Rao", "nikhil.rao@foodis.com", "Nikhil@"),
    ("Akhil Das", "akhil.das@foodis.com", "Akhil@"),
    ("Rahul Nambiar", "rahul.nambiar@foodis.com", "Rahul@"),
    ("Vishal Prasad", "vishal.prasad@foodis.com", "Vishal@"),
]

created_count = 0
skipped_count = 0

print(f"Creating {len(riders_data)} rider accounts...")
print("=" * 60)

for name, email, password in riders_data:
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        skipped_count += 1
        continue
    
    # Create user in core.User
    user = User.objects.create_user(
        email=email,
        password=password,
        name=name,
        role='RIDER',
        is_active=True,
        is_verified=True,
        email_verified=True
    )
    
    # Create rider profile
    Rider.objects.create(
        email=email,
        password=make_password(password),
        full_name=name,
        city='Mehsana',
        is_active=True,
        is_online=False,
        wallet_balance=0.0,
    )
    
    # Create RiderProfile for legacy compatibility
    RiderProfile.objects.create(
        rider=user,
        city='Mehsana',
        status='APPROVED',
        is_online=False,
        wallet_balance=0.0,
    )
    
    created_count += 1

print(f"✓ Created: {created_count} riders")
print(f"✓ Skipped (already exist): {skipped_count} riders")
print("=" * 60)
print("All riders are now ready to login!")
