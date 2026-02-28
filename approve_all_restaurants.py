#!/usr/bin/env python
"""
Script to approve all restaurants in the database.
This enables them to appear in the restaurant list API.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Restaurant

def approve_all_restaurants():
    """Approve all restaurants by setting status to APPROVED"""
    # Get all restaurants
    restaurants = Restaurant.objects.all()
    total_count = restaurants.count()
    
    if total_count == 0:
        print("❌ No restaurants found in database")
        return
    
    print(f"📋 Found {total_count} restaurants")
    print("⏳ Approving all restaurants...\n")
    
    # Get restaurants that are still PENDING
    pending_count = restaurants.filter(status='PENDING').count()
    approved_count = restaurants.filter(status='APPROVED').count()
    other_count = total_count - pending_count - approved_count
    
    print(f"Current status breakdown:")
    print(f"  - PENDING: {pending_count}")
    print(f"  - APPROVED: {approved_count}")
    print(f"  - OTHER: {other_count}\n")
    
    # Update all to APPROVED
    updated_count = restaurants.exclude(status='APPROVED').update(status='APPROVED')
    
    print(f"✅ Updated {updated_count} restaurants to APPROVED status")
    
    # Verify
    final_approved = Restaurant.objects.filter(status='APPROVED').count()
    print(f"✅ Total APPROVED restaurants now: {final_approved}/{total_count}")
    
    if final_approved == total_count:
        print("\n🎉 SUCCESS! All restaurants are now approved and will display in the app!")
    else:
        print(f"\n⚠️  WARNING: {total_count - final_approved} restaurants still not approved")

if __name__ == '__main__':
    approve_all_restaurants()
