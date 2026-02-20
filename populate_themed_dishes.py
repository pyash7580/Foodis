import os
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')

# Disable OpenBLAS threading to avoid memory issues
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

import django
django.setup()

from client.models import Restaurant, MenuItem
from decimal import Decimal

# Restaurant-specific themed menu items
THEMED_MENUS = {
    'Idli Sambar Express': [
        ('Idli (3 pcs)', 'Soft steamed rice cakes served with sambar and chutneys', 'VEG', 60, 10),
        ('Medu Vada (2 pcs)', 'Crispy lentil donuts with sambar', 'VEG', 70, 12),
        ('Masala Dosa', 'Crispy rice crepe filled with spiced potato filling', 'VEG', 90, 15),
        ('Plain Dosa', 'Thin crispy rice crepe', 'VEG', 70, 12),
        ('Rava Dosa', 'Crispy semolina crepe', 'VEG', 85, 15),
        ('Onion Uttapam', 'Thick rice pancake with onion topping', 'VEG', 80, 15),
        ('Sambar Rice', 'Rice mixed with tangy lentil stew', 'VEG', 95, 18),
        ('Curd Rice', 'Soothing rice with yogurt and tempering', 'VEG', 75, 10),
        ('Filter Coffee', 'Authentic South Indian filter coffee', 'VEG', 40, 5),
        ('Coconut Chutney', 'Fresh coconut chutney', 'VEG', 20, 5),
    ],
    'Dosa Darbar': [
        ('Mysore Masala Dosa', 'Spicy dosa with red chutney and potato filling', 'VEG', 110, 18),
        ('Cheese Dosa', 'Dosa topped with melted cheese', 'VEG', 120, 15),
        ('Paneer Dosa', 'Dosa filled with spiced paneer', 'VEG', 130, 18),
        ('Ghee Roast Dosa', 'Crispy dosa roasted in pure ghee', 'VEG', 100, 15),
        ('Paper Dosa', 'Extra thin and crispy large dosa', 'VEG', 95, 18),
        ('Spring Dosa', 'Dosa with mixed vegetable filling', 'VEG', 115, 20),
        ('Set Dosa (3 pcs)', 'Soft fluffy mini dosas', 'VEG', 90, 15),
        ('Rava Masala Dosa', 'Semolina dosa with potato filling', 'VEG', 105, 18),
        ('Podi Dosa', 'Dosa with spicy gun powder', 'VEG', 85, 15),
        ('Butter Dosa', 'Crispy dosa with generous butter', 'VEG', 90, 15),
    ],
    'Biryani Boulevard': [
        ('Hyderabadi Chicken Dum Biryani', 'Authentic slow-cooked chicken biryani', 'NON_VEG', 280, 40),
        ('Mutton Biryani', 'Tender mutton cooked with fragrant basmati rice', 'NON_VEG', 350, 45),
        ('Egg Biryani', 'Flavorful biryani with boiled eggs', 'NON_VEG', 180, 30),
        ('Veg Biryani', 'Mixed vegetables in aromatic spiced rice', 'VEG', 160, 30),
        ('Paneer Biryani', 'Cottage cheese biryani with rich flavors', 'VEG', 200, 35),
        ('Fish Biryani', 'Coastal style biryani with fresh fish', 'NON_VEG', 320, 40),
        ('Prawns Biryani', 'Succulent prawns in fragrant rice', 'NON_VEG', 380, 42),
        ('Kolkata Biryani', 'Bengali style biryani with potato and egg', 'NON_VEG', 260, 38),
        ('Raita', 'Cool yogurt with vegetables', 'VEG', 50, 5),
        ('Double Ka Meetha', 'Bread pudding dessert', 'VEG', 80, 10),
    ],
    'Biryani House': [
        ('Chicken Biryani', 'Classic chicken biryani with spices', 'NON_VEG', 250, 35),
        ('Lucknowi Biryani', 'Awadhi style aromatic biryani', 'NON_VEG', 300, 40),
        ('Keema Biryani', 'Minced meat biryani', 'NON_VEG', 280, 38),
        ('Boneless Chicken Biryani', 'Tender boneless chicken pieces in rice', 'NON_VEG', 290, 38),
        ('Family Pack Biryani', 'Serves 4-5 people', 'NON_VEG', 850, 50),
        ('Dum Ka Murgh', 'Slow-cooked chicken curry', 'NON_VEG', 320, 35),
        ('Bagara Baingan', 'Eggplant in peanut and sesame gravy', 'VEG', 180, 25),
        ('Mirchi Ka Salan', 'Spicy chili curry', 'VEG', 120, 20),
        ('Gulab Jamun (2 pcs)', 'Sweet milk dumplings', 'VEG', 60, 5),
    ],
    'Taj Palace': [
        ('Butter Chicken', 'Tender chicken in creamy tomato gravy', 'NON_VEG', 340, 28),
        ('Dal Makhani', 'Black lentils cooked overnight with butter', 'VEG', 240, 20),
        ('Paneer Butter Masala', 'Cottage cheese in rich tomato gravy', 'VEG', 280, 22),
        ('Tandoori Murgh Full', 'Full chicken marinated and grilled', 'NON_VEG', 650, 35),
        ('Chicken Seekh Kebab', 'Minced chicken skewers', 'NON_VEG', 320, 25),
        ('Paneer Tikka', 'Grilled cottage cheese cubes', 'VEG', 280, 22),
        ('Rogan Josh', 'Kashmiri lamb curry', 'NON_VEG', 420, 35),
        ('Naan Basket', 'Assorted Indian breads', 'VEG', 150, 15),
        ('Shahi Tukda', 'Royal bread dessert', 'VEG', 120, 10),
    ],
    'Royal Rasoi': [
        ('Chicken Korma', 'Mild creamy chicken curry', 'NON_VEG', 310, 28),
        ('Malai Kofta', 'Cottage cheese balls in creamy gravy', 'VEG', 260, 25),
        ('Palak Paneer', 'Cottage cheese in spinach gravy', 'VEG', 240, 22),
        ('Kadhai Chicken', 'Spicy chicken with bell peppers', 'NON_VEG', 320, 28),
        ('Tandoori Roti', 'Whole wheat flatbread', 'VEG', 30, 8),
        ('Butter Naan', 'Soft leavened bread with butter', 'VEG', 50, 10),
        ('Jeera Rice', 'Cumin flavored basmati rice', 'VEG', 120, 15),
        ('Gajar Ka Halwa', 'Carrot dessert', 'VEG', 90, 10),
    ],
    'Tandoor Treasures': [
        ('Tandoori Chicken Half', 'Half chicken marinated in yogurt and spices', 'NON_VEG', 350, 28),
        ('Chicken Tikka', 'Boneless chicken pieces grilled', 'NON_VEG', 320, 25),
        ('Seekh Kebab', 'Minced meat on skewers', 'NON_VEG', 340, 25),
        ('Tandoori Prawns', 'Grilled jumbo prawns', 'NON_VEG', 480, 28),
        ('Fish Tikka', 'Marinated fish grilled in tandoor', 'NON_VEG', 380, 25),
        ('Paneer Tikka', 'Grilled cottage cheese', 'VEG', 280, 22),
        ('Hara Bhara Kebab', 'Spinach and potato patties', 'VEG', 220, 20),
        ('Tandoori Mushroom', 'Grilled mushrooms', 'VEG', 260, 22),
        ('Afghani Chicken', 'Creamy white chicken tikka', 'NON_VEG', 360, 28),
    ],
    'Kebab Factory': [
        ('Galouti Kebab', 'Melt-in-mouth mutton kebabs', 'NON_VEG', 380, 30),
        ('Shami Kebab', 'Minced meat patties', 'NON_VEG', 320, 25),
        ('Kakori Kebab', 'Soft mutton seekh kebab', 'NON_VEG', 360, 28),
        ('Chicken Malai Tikka', 'Creamy chicken tikka', 'NON_VEG', 340, 25),
        ('Reshmi Kebab', 'Silky smooth chicken kebab', 'NON_VEG', 330, 25),
        ('Mutton Burra', 'Spicy mutton ribs', 'NON_VEG', 420, 32),
        ('Veg Seekh Kebab', 'Vegetable skewers', 'VEG', 240, 22),
        ('Kebab Platter', 'Assorted kebabs', 'NON_VEG', 650, 35),
    ],
    'Thali Treasures': [
        ('Gujarati Thali', 'Traditional unlimited Gujarati meal', 'VEG', 280, 25),
        ('Kathiyawadi Thali', 'Spicy Kathiawad style unlimited meal', 'VEG', 300, 30),
        ('Rajasthani Thali', 'Royal Rajasthani unlimited meal', 'VEG', 320, 30),
        ('North Indian Thali', 'Punjabi style meal', 'VEG', 280, 25),
        ('South Indian Thali', 'Complete South Indian meal', 'VEG', 260, 25),
        ('Mini Thali', 'Smaller portion thali', 'VEG', 180, 20),
        ('Dhokla', 'Steamed snack', 'VEG', 60, 12),
        ('Khandvi', 'Rolled gram flour snack', 'VEG', 80, 15),
        ('Undhiyu', 'Mixed vegetable delicacy', 'VEG', 160, 25),
    ],
    'Royal Rajdhani': [
        ('Rajdhani Special Thali', 'Premium unlimited Gujarati thali', 'VEG', 350, 30),
        ('Dal Dhokli', 'Wheat noodles in lentil curry', 'VEG', 140, 20),
        ('Gujarati Kadhi', 'Yogurt based curry with fritters', 'VEG', 120, 18),
        ('Sev Tameta', 'Tomato curry with sev', 'VEG', 110, 18),
        ('Farsan Platter', 'Assorted Gujarati snacks', 'VEG', 150, 15),
        ('Khaman Dhokla', 'Steamed gram flour cake', 'VEG', 70, 12),
        ('Handvo', 'Savory rice lentil cake', 'VEG', 90, 20),
        ('Mohanthal', 'Gram flour fudge', 'VEG', 80, 10),
    ],
    'The Coastal Kitchen': [
        ('Prawn Curry', 'Coastal style prawn gravy', 'NON_VEG', 380, 30),
        ('Fish Fry', 'Crispy fried fish', 'NON_VEG', 320, 25),
        ('Crab Masala', 'Spicy crab curry', 'NON_VEG', 450, 35),
        ('Lobster Thermidor', 'Grilled lobster in creamy sauce', 'NON_VEG', 850, 40),
        ('Squid Fry', 'Crispy fried squid rings', 'NON_VEG', 340, 25),
        ('Fish Curry', 'Traditional fish curry', 'NON_VEG', 300, 28),
        ('Prawn Biryani', 'Seafood biryani', 'NON_VEG', 380, 40),
        ('Fish Tikka', 'Grilled fish pieces', 'NON_VEG', 360, 25),
    ],
    'Seafood Sensation': [
        ('Butter Garlic Prawns', 'Prawns in butter garlic sauce', 'NON_VEG', 420, 28),
        ('Goan Fish Curry', 'Tangy coconut based fish curry', 'NON_VEG', 340, 30),
        ('Pomfret Fry', 'Whole pomfret fried crispy', 'NON_VEG', 480, 30),
        ('Surmai Tikka', 'Grilled kingfish', 'NON_VEG', 420, 28),
        ('Rawas Masala', 'Spicy Indian salmon curry', 'NON_VEG', 380, 30),
        ('Crab Roast', 'Dry roasted crab', 'NON_VEG', 520, 35),
        ('Seafood Platter', 'Mix of prawns, fish, and squid', 'NON_VEG', 680, 40),
    ],
    'Paneer Paradise': [
        ('Paneer Tikka Masala', 'Grilled paneer in creamy gravy', 'VEG', 260, 25),
        ('Kadhai Paneer', 'Paneer with bell peppers in kadhai gravy', 'VEG', 250, 22),
        ('Paneer Butter Masala', 'Cottage cheese in rich tomato gravy', 'VEG', 270, 25),
        ('Palak Paneer', 'Paneer in spinach gravy', 'VEG', 240, 22),
        ('Paneer Bhurji', 'Scrambled cottage cheese', 'VEG', 230, 20),
        ('Shahi Paneer', 'Royal paneer curry with nuts', 'VEG', 280, 25),
        ('Paneer Lababdar', 'Paneer in tangy tomato gravy', 'VEG', 260, 24),
        ('Paneer Do Pyaza', 'Paneer with double onions', 'VEG', 250, 22),
        ('Malai Paneer', 'Paneer in creamy white gravy', 'VEG', 270, 25),
    ],
    'The Dhaba Deluxe': [
        ('Highway Chicken Curry', 'Rustic dhaba style chicken', 'NON_VEG', 280, 25),
        ('Amritsari Kulcha', 'Stuffed bread from Amritsar', 'VEG', 80, 15),
        ('Chole Bhature', 'Spicy chickpeas with fried bread', 'VEG', 140, 20),
        ('Aloo Paratha', 'Potato stuffed flatbread', 'VEG', 70, 15),
        ('Lassi (Sweet/Salted)', 'Traditional yogurt drink', 'VEG', 60, 8),
        ('Dal Tadka', 'Yellow lentils with tempering', 'VEG', 180, 18),
        ('Mixed Veg', 'Seasonal vegetables curry', 'VEG', 160, 20),
        ('Sarson Ka Saag', 'Mustard greens curry', 'VEG', 200, 25),
        ('Makki Ki Roti', 'Corn flour flatbread', 'VEG', 40, 12),
    ],
    'Butter Chicken Co': [
        ('Signature Butter Chicken', 'Our special butter chicken recipe', 'NON_VEG', 350, 28),
        ('Butter Paneer', 'Vegetarian butter chicken style', 'VEG', 280, 25),
        ('Butter Naan', 'Soft naan with lots of butter', 'VEG', 60, 12),
        ('Butter Garlic Naan', 'Naan with butter and garlic', 'VEG', 70, 12),
        ('Butter Chicken Biryani', 'Butter chicken in rice form', 'NON_VEG', 320, 35),
        ('Butter Chicken Roll', 'Butter chicken wrapped in paratha', 'NON_VEG', 180, 15),
        ('Dal Butter Fry', 'Lentils with butter tempering', 'VEG', 200, 20),
        ('Makhani Gravy Bowl', 'Extra bowl of our signature gravy', 'VEG', 80, 10),
    ],
    'Chaat Corner Premium': [
        ('Pani Puri', 'Crispy puris with tangy water (8 pcs)', 'VEG', 60, 10),
        ('Sev Puri', 'Crispy puris topped with chutneys', 'VEG', 70, 10),
        ('Dahi Puri', 'Puris filled with yogurt and chutneys', 'VEG', 80, 12),
        ('Bhel Puri', 'Puffed rice mixture', 'VEG', 60, 10),
        ('Papdi Chaat', 'Crispy wafers with yogurt and chutneys', 'VEG', 80, 12),
        ('Raj Kachori', 'Large stuffed kachori', 'VEG', 100, 15),
        ('Dahi Vada', 'Lentil dumplings in yogurt', 'VEG', 90, 15),
        ('Samosa Chaat', 'Samosa topped with chole and chutneys', 'VEG', 80, 12),
        ('Aloo Tikki Chaat', 'Potato patty with toppings', 'VEG', 75, 12),
    ],
    'Bombay Sandwich Co': [
        ('Bombay Veg Sandwich', 'Classic Mumbai sandwich', 'VEG', 80, 12),
        ('Cheese Sandwich', 'Grilled cheese sandwich', 'VEG', 90, 12),
        ('Paneer Sandwich', 'Grilled paneer sandwich', 'VEG', 100, 15),
        ('Corn Cheese Sandwich', 'Sweet corn with cheese', 'VEG', 110, 15),
        ('Schezwan Sandwich', 'Spicy Indo-Chinese sandwich', 'VEG', 100, 15),
        ('Club Sandwich', 'Triple decker sandwich', 'VEG', 130, 18),
        ('Grilled Veg Sandwich', 'Grilled mixed vegetables', 'VEG', 90, 15),
        ('Chocolate Sandwich', 'Sweet chocolate sandwich', 'VEG', 80, 10),
    ],
    'The Paratha Place': [
        ('Aloo Paratha', 'Potato stuffed paratha', 'VEG', 70, 15),
        ('Paneer Paratha', 'Cottage cheese stuffed paratha', 'VEG', 90, 15),
        ('Gobi Paratha', 'Cauliflower stuffed paratha', 'VEG', 80, 15),
        ('Mix Veg Paratha', 'Mixed vegetable stuffed paratha', 'VEG', 90, 18),
        ('Onion Paratha', 'Onion stuffed paratha', 'VEG', 70, 15),
        ('Mooli Paratha', 'Radish stuffed paratha', 'VEG', 70, 15),
        ('Dal Paratha', 'Lentil stuffed paratha', 'VEG', 75, 15),
        ('Paratha Combo', '2 Parathas with curd and pickle', 'VEG', 160, 20),
    ],
    'Wok This Way': [
        ('Veg Hakka Noodles', 'Stir-fried noodles', 'VEG', 160, 18),
        ('Chicken Hakka Noodles', 'Noodles with chicken', 'NON_VEG', 200, 20),
        ('Veg Fried Rice', 'Stir-fried rice with vegetables', 'VEG', 150, 18),
        ('Chicken Fried Rice', 'Rice stir-fried with chicken', 'NON_VEG', 190, 20),
        ('Chilli Chicken', 'Spicy chicken with bell peppers', 'NON_VEG', 280, 25),
        ('Manchurian (Dry/Gravy)', 'Veg/chicken manchurian balls', 'VEG', 180, 20),
        ('Spring Rolls', 'Crispy vegetable rolls', 'VEG', 140, 18),
        ('Schezwan Noodles', 'Spicy schezwan style noodles', 'VEG', 170, 18),
    ],
    'Masala Magic': [
        ('Chilli Paneer', 'Spicy paneer in Indo-Chinese style', 'VEG', 240, 20),
        ('Veg Manchurian', 'Vegetable balls in spicy gravy', 'VEG', 180, 20),
        ('Gobi Manchurian', 'Cauliflower manchurian', 'VEG', 170, 18),
        ('Paneer Schezwan', 'Paneer in schezwan sauce', 'VEG', 250, 22),
        ('Dragon Paneer', 'Spicy paneer in dragon sauce', 'VEG', 260, 22),
        ('Veg Crispy', 'Crispy vegetables in sauce', 'VEG', 200, 20),
        ('American Chopsuey', 'Noodles with sweet-spicy sauce', 'VEG', 190, 22),
    ],
    'Momo Mania Deluxe': [
        ('Veg Steamed Momos (8 pcs)', 'Steamed vegetable dumplings', 'VEG', 120, 15),
        ('Chicken Steamed Momos (8 pcs)', 'Steamed chicken dumplings', 'NON_VEG', 160, 18),
        ('Veg Fried Momos (8 pcs)', 'Crispy fried veg momos', 'VEG', 140, 18),
        ('Chicken Fried Momos (8 pcs)', 'Crispy fried chicken momos', 'NON_VEG', 180, 20),
        ('Paneer Momos (8 pcs)', 'Cottage cheese momos', 'VEG', 150, 18),
        ('Cheese Momos (8 pcs)', 'Cheese filled momos', 'VEG', 160, 18),
        ('Schezwan Momos (8 pcs)', 'Spicy schezwan momos', 'VEG', 150, 18),
        ('Tandoori Momos (8 pcs)', 'Grilled momos', 'VEG', 160, 20),
    ],
    'Urban Tadka': [
        ('Pav Bhaji', 'Spicy vegetable mash with bread', 'VEG', 100, 18),
        ('Vada Pav', 'Mumbai style potato fritter burger', 'VEG', 40, 10),
        ('Misal Pav', 'Spicy sprouts curry with bread', 'VEG', 90, 18),
        ('Dabeli', 'Gujarati style burger', 'VEG', 50, 12),
        ('Pani Puri (12 pcs)', 'Street style pani puri', 'VEG', 60, 10),
        ('Sev Puri', 'Crispy puris with toppings', 'VEG', 70, 10),
        ('Pav Bhaji Fondue', 'Cheese pav bhaji fusion', 'VEG', 180, 20),
    ],
    'Bombay Brasserie': [
        ('Vada Pav', 'Iconic Mumbai snack', 'VEG', 40, 10),
        ('Misal Pav', 'Spicy misal with pav', 'VEG', 90, 18),
        ('Pav Bhaji', 'Vegetable curry with buttered pav', 'VEG', 100, 18),
        ('Bhel Puri', 'Mumbai style bhel', 'VEG', 60, 10),
        ('Samosa Pav', 'Samosa in pav bread', 'VEG', 50, 12),
        ('Khaman Dhokla', 'Soft steamed snack', 'VEG', 60, 12),
        ('Kanda Poha', 'Flattened rice with onions', 'VEG', 70, 15),
    ],
    'Fusion Flames': [
        ('Butter Chicken Pizza', 'Pizza with butter chicken topping', 'NON_VEG', 320, 25),
        ('Paneer Tikka Pizza', 'Indian fusion pizza', 'VEG', 280, 25),
        ('Schezwan Paneer Dosa', 'Dosa with Indo-Chinese filling', 'VEG', 140, 18),
        ('Cheese Burst Paratha', 'Paratha with cheese burst', 'VEG', 150, 18),
        ('Tandoori Pasta', 'Pasta in tandoori sauce', 'VEG', 220, 22),
        ('Masala Mac & Cheese', 'Indian spiced mac and cheese', 'VEG', 200, 20),
        ('Curry Quesadilla', 'Indian curry in Mexican style', 'VEG', 180, 20),
    ],
    'The Naan Stop': [
        ('Butter Naan', 'Soft butter naan', 'VEG', 50, 12),
        ('Garlic Naan', 'Naan with garlic topping', 'VEG', 60, 12),
        ('Cheese Naan', 'Naan stuffed with cheese', 'VEG', 90, 15),
        ('Keema Naan', 'Naan stuffed with minced meat', 'NON_VEG', 120, 18),
        ('Peshawari Naan', 'Sweet naan with dry fruits', 'VEG', 100, 15),
        ('Tandoori Roti', 'Whole wheat flatbread', 'VEG', 30, 10),
        ('Lachha Paratha', 'Layered paratha', 'VEG', 70, 15),
        ('Naan Basket (Assorted)', '4 different naans', 'VEG', 180, 18),
    ],
    'Sizzler Palace': [
        ('Veg Sizzler', 'Sizzling vegetables with rice/noodles', 'VEG', 320, 30),
        ('Chicken Sizzler', 'Sizzling chicken with sides', 'NON_VEG', 380, 35),
        ('Paneer Sizzler', 'Paneer tikka sizzler', 'VEG', 340, 30),
        ('Fish Sizzler', 'Grilled fish sizzler', 'NON_VEG', 420, 35),
        ('Prawns Sizzler', 'Grilled prawns sizzler', 'NON_VEG', 480, 38),
        ('Mixed Grill Sizzler', 'Assorted grills on sizzler', 'NON_VEG', 520, 40),
        ('Brownie Sizzler', 'Chocolate brownie sizzler dessert', 'VEG', 180, 15),
    ],
}

def populate_themed_dishes():
    """Populate restaurants with themed dishes based on their names"""
    print("Starting to populate themed dishes...\n")

    
    updated_count = 0
    skipped_count = 0
    
    for restaurant_name, menu_items in THEMED_MENUS.items():
        try:
            # Try to find restaurant by name (case insensitive)
            restaurant = Restaurant.objects.filter(name__iexact=restaurant_name).first()
            
            if not restaurant:
                print(f"WARNING: Restaurant '{restaurant_name}' not found. Skipping...")
                skipped_count += 1
                continue
            
            # Delete existing menu items for this restaurant to avoid duplicates
            deleted_count = MenuItem.objects.filter(restaurant=restaurant).delete()[0]
            print(f"Deleted {deleted_count} old items from {restaurant.name}")
            
            # Add new themed menu items
            items_added = 0
            for item_data in menu_items:
                name, desc, veg_type, price, prep_time = item_data
                
                MenuItem.objects.create(
                    restaurant=restaurant,
                    name=name,
                    description=desc,
                    price=Decimal(str(price)),
                    category=None,  # You can assign categories if needed
                    veg_type=veg_type,
                    is_available=True,
                    preparation_time=prep_time,
                )
                items_added += 1
            
            print(f"SUCCESS: {restaurant.name}: Added {items_added} themed dishes")
            updated_count += 1
            
        except Exception as e:
            print(f"ERROR processing {restaurant_name}: {str(e)}")
            continue
    
    print(f"\n{'='*60}")
    print(f"SUCCESS!")
    print(f"   - Updated: {updated_count} restaurants")
    print(f"   - Skipped: {skipped_count} restaurants")
    print(f"{'='*60}")
    print(f"\nAll dishes are now themed according to restaurant names!")
    print(f"Visit http://localhost:3000 to see the updated menus!\n")

if __name__ == '__main__':
    populate_themed_dishes()
