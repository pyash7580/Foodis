from django.contrib.auth import get_user_model
from client.models import Restaurant, MenuItem
from decimal import Decimal
import random

User = get_user_model()

# Create restaurant owner users
owners = []
for i in range(45):
    email = f'restaurant{i+1}@foodis.com'
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'phone': f'+91{9000000000 + i}',
            'name': f'Restaurant Owner {i+1}',
            'role': 'RESTAURANT'
        }
    )
    if created:
        user.set_password('password123')
        user.save()
    owners.append(user)

# Premium Indian restaurant data
restaurants_data = [
    {'name': 'Taj Palace', 'cuisine': ['Mughlai', 'North Indian'], 'city': 'Mumbai', 'delivery_fee': 45},
    {'name': 'The Grand Bhoj', 'cuisine': ['Fine Dining'], 'city': 'Delhi', 'delivery_fee': 60},
    {'name': 'Spice Symphony', 'cuisine': ['South Indian'], 'city': 'Bangalore', 'delivery_fee': 35},
    {'name': 'Royal Rasoi', 'cuisine': ['North Indian'], 'city': 'Jaipur', 'delivery_fee': 40},
    {'name': 'Saffron Lounge', 'cuisine': ['Mughlai'], 'city': 'Mumbai', 'delivery_fee': 55},
    {'name': 'Curry Craft', 'cuisine': ['Bengali'], 'city': 'Kolkata', 'delivery_fee': 30},
    {'name': 'The Dhaba Deluxe', 'cuisine': ['North Indian'], 'city': 'Chandigarh', 'delivery_fee': 38},
    {'name': 'Masala Magic', 'cuisine': ['Chinese'], 'city': 'Pune', 'delivery_fee': 42},
    {'name': 'Biryani Boulevard', 'cuisine': ['Biryani'], 'city': 'Hyderabad', 'delivery_fee': 48},
    {'name': 'The Coastal Kitchen', 'cuisine': ['Seafood'], 'city': 'Goa', 'delivery_fee': 50},
    {'name': 'Nawab Delight', 'cuisine': ['North Indian'], 'city': 'Lucknow', 'delivery_fee': 44},
    {'name': 'Tandoor Treasures', 'cuisine': ['North Indian'], 'city': 'Delhi', 'delivery_fee': 46},
    {'name': 'The Spice Route', 'cuisine': ['South Indian'], 'city': 'Kochi', 'delivery_fee': 36},
    {'name': 'Urban Tadka', 'cuisine': ['Street Food'], 'city': 'Mumbai', 'delivery_fee': 32},
    {'name': 'Fusion Flames', 'cuisine': ['Chinese'], 'city': 'Bangalore', 'delivery_fee': 52},
    {'name': 'The Royal Platter', 'cuisine': ['Maharashtrian'], 'city': 'Pune', 'delivery_fee': 39},
    {'name': 'Charcoal Grill', 'cuisine': ['BBQ'], 'city': 'Delhi', 'delivery_fee': 58},
    {'name': 'Dosa Darbar', 'cuisine': ['South Indian'], 'city': 'Chennai', 'delivery_fee': 28},
    {'name': 'Thali Treasures', 'cuisine': ['Gujarati'], 'city': 'Ahmedabad', 'delivery_fee': 34},
    {'name': 'The Curry Club', 'cuisine': ['Multi-Cuisine'], 'city': 'Mumbai', 'delivery_fee': 47},
    {'name': 'Bombay Brasserie', 'cuisine': ['Street Food'], 'city': 'Mumbai', 'delivery_fee': 41},
    {'name': 'Kebab Factory', 'cuisine': ['Mughlai'], 'city': 'Delhi', 'delivery_fee': 49},
    {'name': 'Chaat Corner Premium', 'cuisine': ['Street Food'], 'city': 'Jaipur', 'delivery_fee': 31},
    {'name': 'Biryani House', 'cuisine': ['Biryani'], 'city': 'Hyderabad', 'delivery_fee': 43},
    {'name': 'Paneer Paradise', 'cuisine': ['North Indian'], 'city': 'Amritsar', 'delivery_fee': 37},
    {'name': 'Seafood Sensation', 'cuisine': ['Seafood'], 'city': 'Mangalore', 'delivery_fee': 54},
    {'name': 'The Vintage Kitchen', 'cuisine': ['Continental'], 'city': 'Bangalore', 'delivery_fee': 62},
    {'name': 'Spicy Affairs', 'cuisine': ['Andhra'], 'city': 'Vijayawada', 'delivery_fee': 33},
    {'name': 'Emperor Table', 'cuisine': ['Fine Dining'], 'city': 'Mumbai', 'delivery_fee': 65},
    {'name': 'Desi Delights', 'cuisine': ['North Indian'], 'city': 'Ludhiana', 'delivery_fee': 35},
    {'name': 'Golden Fork', 'cuisine': ['Continental'], 'city': 'Gurgaon', 'delivery_fee': 56},
    {'name': 'Moksha Dining', 'cuisine': ['Modern Indian'], 'city': 'Bangalore', 'delivery_fee': 59},
    {'name': 'Spice Garden', 'cuisine': ['South Indian'], 'city': 'Kochi', 'delivery_fee': 38},
    {'name': 'Momo Mania Deluxe', 'cuisine': ['Tibetan'], 'city': 'Darjeeling', 'delivery_fee': 29},
    {'name': 'The Paratha Place', 'cuisine': ['North Indian'], 'city': 'Delhi', 'delivery_fee': 30},
    {'name': 'Wok This Way', 'cuisine': ['Chinese'], 'city': 'Mumbai', 'delivery_fee': 51},
    {'name': 'Butter Chicken Co', 'cuisine': ['North Indian'], 'city': 'Delhi', 'delivery_fee': 45},
    {'name': 'Idli Sambar Express', 'cuisine': ['South Indian'], 'city': 'Bangalore', 'delivery_fee': 27},
    {'name': 'The Rajwada', 'cuisine': ['Rajasthani'], 'city': 'Udaipur', 'delivery_fee': 53},
    {'name': 'Curry House Deluxe', 'cuisine': ['Multi-Cuisine'], 'city': 'Pune', 'delivery_fee': 48},
    {'name': 'Sizzler Palace', 'cuisine': ['Continental'], 'city': 'Mumbai', 'delivery_fee': 57},
    {'name': 'Bombay Sandwich Co', 'cuisine': ['Fast Food'], 'city': 'Mumbai', 'delivery_fee': 25},
    {'name': 'The Naan Stop', 'cuisine': ['North Indian'], 'city': 'Delhi', 'delivery_fee': 42},
    {'name': 'Royal Rajdhani', 'cuisine': ['Gujarati'], 'city': 'Ahmedabad', 'delivery_fee': 40},
    {'name': 'The Coastal Spice', 'cuisine': ['Mangalorean'], 'city': 'Mangalore', 'delivery_fee': 36},
]

created_restaurants = []
for i, rest_data in enumerate(restaurants_data):
    restaurant, created = Restaurant.objects.get_or_create(
        name=rest_data['name'],
        owner=owners[i],
        defaults={
            'description': f"Premium {', '.join(rest_data['cuisine'])} restaurant offering authentic flavors",
            'city': rest_data['city'],
            'state': 'India',
            'pincode': f'{110001 + i}',
            'latitude': 28.6139 + (i * 0.01),
            'longitude': 77.2090 + (i * 0.01),
            'phone': f'+91{8000000000 + i}',
            'delivery_fee': Decimal(str(rest_data['delivery_fee'])),
            'is_open': True,
        }
    )
    
    if created:
        print(f'Created restaurant: {restaurant.name}')
        created_restaurants.append((restaurant, rest_data['cuisine']))

# Menu items data
menu_data = [
    ('Butter Chicken', 'Tender chicken in creamy tomato gravy', 'NON_VEG', 320, 25, 'North Indian'),
    ('Dal Makhani', 'Black lentils slow-cooked with butter', 'VEG', 240, 20, 'North Indian'),
    ('Paneer Tikka Masala', 'Grilled cottage cheese in spiced gravy', 'VEG', 280, 22, 'North Indian'),
    ('Tandoori Chicken', 'Marinated chicken grilled in clay oven', 'NON_VEG', 380, 25, 'North Indian'),
    ('Palak Paneer', 'Cottage cheese in creamy spinach', 'VEG', 250, 20, 'North Indian'),
    ('Aloo Gobi', 'Potato and cauliflower dry curry', 'VEG', 180, 18, 'North Indian'),
    ('Chicken Tikka', 'Grilled chicken pieces', 'NON_VEG', 340, 22, 'North Indian'),
    ('Veg Pulao', 'Fragrant basmati rice with vegetables', 'VEG', 200, 20, 'North Indian'),
    ('Garlic Naan', 'Soft bread with garlic', 'VEG', 60, 10, 'North Indian'),
    ('Masala Dosa', 'Crispy rice crepe with spiced potato', 'VEG', 120, 15, 'South Indian'),
    ('Idli Sambar', 'Steamed rice cakes with lentil soup', 'VEG', 80, 12, 'South Indian'),
    ('Medu Vada', 'Crispy lentil donuts', 'VEG', 100, 12, 'South Indian'),
    ('Rava Dosa', 'Crispy semolina crepe', 'VEG', 130, 15, 'South Indian'),
    ('Uttapam', 'Thick rice pancake', 'VEG', 110, 15, 'South Indian'),
    ('Filter Coffee', 'Traditional South Indian coffee', 'VEG', 50, 5, 'South Indian'),
    ('Hakka Noodles', 'Stir-fried noodles with vegetables', 'VEG', 180, 15, 'Chinese'),
    ('Manchurian', 'Fried vegetable balls in sauce', 'VEG', 200, 18, 'Chinese'),
    ('Chilli Chicken', 'Spicy chicken with bell peppers', 'NON_VEG', 280, 20, 'Chinese'),
    ('Fried Rice', 'Stir-fried rice with vegetables', 'VEG', 160, 15, 'Chinese'),
    ('Spring Rolls', 'Crispy rolls with vegetables', 'VEG', 140, 12, 'Chinese'),
    ('Hyderabadi Biryani', 'Aromatic rice with marinated meat', 'NON_VEG', 350, 35, 'Biryani'),
    ('Veg Biryani', 'Fragrant rice with mixed vegetables', 'VEG', 250, 25, 'Biryani'),
    ('Mutton Biryani', 'Tender mutton with basmati rice', 'NON_VEG', 420, 40, 'Biryani'),
    ('Chicken Dum Biryani', 'Slow-cooked chicken biryani', 'NON_VEG', 380, 35, 'Biryani'),
]

# Add menu items to restaurants
for restaurant, cuisines in created_restaurants:
    items_added = 0
    cuisine_type = cuisines[0]
    
    relevant_items = [item for item in menu_data if cuisine_type in item[5]]
    if not relevant_items:
        relevant_items = menu_data[:10]
    
    for item in relevant_items[:10]:
        name, desc, veg_type, price, prep_time, category = item
        menu_item, created = MenuItem.objects.get_or_create(
            restaurant=restaurant,
            name=name,
            defaults={
                'description': desc,
                'price': Decimal(str(price)),
                'category': category,
                'veg_type': veg_type,
                'is_available': True,
                'preparation_time': prep_time,
                'is_bestseller': random.choice([True, False, False]),
            }
        )
        if created:
            items_added += 1
    
    print(f'Added {items_added} menu items to {restaurant.name}')

print(f'Successfully seeded {len(created_restaurants)} premium restaurants!')
