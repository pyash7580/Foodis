import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from django.contrib.auth import authenticate

data = """1 | Rakesh Kumar | rakesh.kumar@foodis.com | Rakesh@
2 | Suresh Patel | suresh.patel@foodis.com | Suresh@
3 | Mahesh Sharma | mahesh.sharma@foodis.com | Mahesh@
4 | Ramesh Yadav | ramesh.yadav@foodis.com | Ramesh@
5 | Dinesh Verma | dinesh.verma@foodis.com | Dinesh@
6 | Ganesh Gupta | ganesh.gupta@foodis.com | Ganesh@
7 | Rajesh Singh | rajesh.singh@foodis.com | Rajesh@
8 | Mukesh Joshi | mukesh.joshi@foodis.com | Mukesh@
9 | Naresh Thakur | naresh.thakur@foodis.com | Naresh@
10 | Hitesh Chauhan | hitesh.chauhan@foodis.com | Hitesh@
11 | Amit Tiwari | amit.tiwari@foodis.com | Amit@
12 | Sumit Pandey | sumit.pandey@foodis.com | Sumit@
13 | Rohit Mishra | rohit.mishra@foodis.com | Rohit@
14 | Mohit Dubey | mohit.dubey@foodis.com | Mohit@
15 | Ankit Saxena | ankit.saxena@foodis.com | Ankit@
16 | Vikas Rawat | vikas.rawat@foodis.com | Vikas@
17 | Deepak Nair | deepak.nair@foodis.com | Deepak@
18 | Arun Menon | arun.menon@foodis.com | Arun@
19 | Vijay Reddy | vijay.reddy@foodis.com | Vijay@
20 | Sanjay Patil | sanjay.patil@foodis.com | Sanjay@
21 | Manoj Desai | manoj.desai@foodis.com | Manoj@
22 | Pramod Kulkarni | pramod.kulkarni@foodis.com | Pramod@
23 | Ashok Jadhav | ashok.jadhav@foodis.com | Ashok@
24 | Sunil Pawar | sunil.pawar@foodis.com | Sunil@
25 | Anil Shinde | anil.shinde@foodis.com | Anil@
26 | Ravi Chavan | ravi.chavan@foodis.com | Ravi@
27 | Kiran Bhatt | kiran.bhatt@foodis.com | Kiran@
28 | Nitin Jain | nitin.jain@foodis.com | Nitin@
29 | Sachin Agarwal | sachin.agarwal@foodis.com | Sachin@
30 | Pankaj Bansal | pankaj.bansal@foodis.com | Pankaj@
31 | Yogesh Mehta | yogesh.mehta@foodis.com | Yogesh@
32 | Lokesh Soni | lokesh.soni@foodis.com | Lokesh@
33 | Harish Rathore | harish.rathore@foodis.com | Harish@
34 | Girish Bhatia | girish.bhatia@foodis.com | Girish@
35 | Satish Malhotra | satish.malhotra@foodis.com | Satish@
36 | Pradeep Kapoor | pradeep.kapoor@foodis.com | Pradeep@
37 | Sandeep Arora | sandeep.arora@foodis.com | Sandeep@"""

lines = [line for line in data.split('\n') if line.strip()]

with open('tmp_riders_result.txt', 'w') as f:
    f.write("| # | Name | Email | Exists | Password Match | Has Rider Profile |\n")
    f.write("|---|------|-------|--------|----------------|-------------------|\n")

    for line in lines:
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 4:
            continue
        num, name, email, password = parts[0], parts[1], parts[2], parts[3]
        
        try:
            user = User.objects.get(email=email)
            exists = "Yes"
            is_pwd_correct = user.check_password(password)
            pwd_match = "Yes" if is_pwd_correct else "No"
            has_profile = "Yes" if hasattr(user, 'rider_profile') else "No"
        except User.DoesNotExist:
            exists = "No"
            pwd_match = "-"
            has_profile = "-"
            
        f.write(f"| {num} | {name} | {email} | {exists} | {pwd_match} | {has_profile} |\n")
