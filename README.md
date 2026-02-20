# Foodis - Premium Food Ordering Platform

A complete, production-ready online food ordering web application similar to Zomato or Swiggy, built with Django, Django REST Framework, React, and real-time WebSocket support.

## Features

### Client Side
- ✅ OTP-based authentication
- ✅ Google Maps location detection
- ✅ Browse nearby restaurants
- ✅ AI-based food search and recommendations
- ✅ Advanced filters (price, rating, veg/non-veg, delivery time)
- ✅ Restaurant detail pages with full menus
- ✅ Menu item customization
- ✅ Shopping cart and checkout
- ✅ Coupon system
- ✅ Razorpay payments (test mode) and Cash on Delivery
- ✅ Live order tracking on map
- ✅ Real-time notifications
- ✅ Order history and re-order
- ✅ Wallet and refunds system

### Restaurant Side
- ✅ Onboarding with admin approval
- ✅ Profile and menu management
- ✅ Real-time order alerts
- ✅ Accept or reject orders
- ✅ Cooking status updates
- ✅ Preparation timers
- ✅ Earnings dashboard
- ✅ Sales analytics
- ✅ AI insights (best-selling items, peak times, price optimization, low-stock alerts)

### Rider Side
- ✅ OTP login
- ✅ Online/offline toggle
- ✅ Auto order assignment based on distance
- ✅ Google Maps navigation
- ✅ Live location tracking
- ✅ Pickup and delivery confirmation with OTP
- ✅ Real-time sync with client tracking
- ✅ Earnings with daily and weekly summaries

### Admin Side
- ✅ Super-admin dashboard
- ✅ Full control over users, restaurants, and riders
- ✅ Approvals system
- ✅ Commission management
- ✅ Categories, banners, coupons management
- ✅ Orders, payments, refunds, wallets management
- ✅ AI analytics dashboard
- ✅ City-wise trends
- ✅ Demand prediction
- ✅ Peak hours analysis
- ✅ Restaurant and rider performance metrics
- ✅ Fraud detection

### AI Engine
- ✅ Food recommendations (no paid APIs)
- ✅ Trending food detection
- ✅ User behavior analysis
- ✅ Restaurant ranking
- ✅ Rider efficiency scoring
- ✅ Demand forecasting

## Tech Stack

### Backend
- Django 4.2.7
- Django REST Framework
- Django Channels (WebSockets)
- PostgreSQL
- Redis (caching & OTP)
- Celery (background tasks)
- Razorpay (payments)
- Google Maps API

### Frontend
- React
- Tailwind CSS
- WebSocket client

### AI/ML
- scikit-learn
- pandas
- numpy

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL
- Redis
- Node.js 16+ (for frontend)

### Backend Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd Foodis
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Set up PostgreSQL database**
```bash
# Create database
createdb foodis_db

# Or using psql
psql -U postgres
CREATE DATABASE foodis_db;
```

6. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

9. **Start Redis**
```bash
# On Linux/Mac
redis-server

# On Windows, download and run Redis
```

10. **Start Celery worker** (in a new terminal)
```bash
celery -A foodis worker -l info
```

11. **Start Celery beat** (in another terminal, for scheduled tasks)
```bash
celery -A foodis beat -l info
```

12. **Run development server**
```bash
python manage.py runserver
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm start
```

The frontend will run on `http://localhost:3000` and backend on `http://localhost:8000`.

## API Documentation

### Authentication
- `POST /api/auth/send-otp/` - Send OTP
- `POST /api/auth/verify-otp/` - Verify OTP and login
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/profile/` - Get user profile

### Client APIs
- `GET /api/client/restaurants/` - List restaurants
- `GET /api/client/restaurants/{id}/` - Restaurant details
- `GET /api/client/menu-items/` - List menu items
- `GET /api/client/cart/` - Get cart
- `POST /api/client/cart/{id}/add_item/` - Add item to cart
- `POST /api/client/orders/` - Create order
- `GET /api/client/orders/{id}/track/` - Track order
- `GET /api/client/search/` - Search restaurants/food
- `GET /api/client/recommendations/` - Get recommendations
- `GET /api/client/trending/` - Get trending items

### Restaurant APIs
- `GET /api/restaurant/restaurant/` - Get restaurant profile
- `PUT /api/restaurant/restaurant/{id}/` - Update restaurant
- `GET /api/restaurant/menu-items/` - List menu items
- `POST /api/restaurant/menu-items/` - Create menu item
- `GET /api/restaurant/orders/` - List orders
- `POST /api/restaurant/orders/{id}/accept/` - Accept order
- `POST /api/restaurant/orders/{id}/reject/` - Reject order
- `POST /api/restaurant/orders/{id}/start_preparing/` - Start preparing
- `POST /api/restaurant/orders/{id}/mark_ready/` - Mark ready
- `GET /api/restaurant/earnings/summary/` - Earnings summary

### Rider APIs
- `GET /api/rider/profile/` - Get rider profile
- `POST /api/rider/profile/{id}/toggle_online/` - Toggle online/offline
- `POST /api/rider/profile/{id}/update_location/` - Update location
- `GET /api/rider/orders/available/` - Get available orders
- `POST /api/rider/orders/{id}/accept/` - Accept order
- `POST /api/rider/orders/{id}/pickup/` - Confirm pickup
- `POST /api/rider/orders/{id}/deliver/` - Confirm delivery
- `GET /api/rider/earnings/summary/` - Earnings summary

### Admin APIs
- `GET /api/admin/dashboard/stats/` - Dashboard statistics
- `GET /api/admin/analytics/` - AI analytics
- `GET /api/admin/fraud-detection/` - Fraud detection
- `POST /api/admin/restaurants/{id}/approve/` - Approve restaurant
- `POST /api/admin/riders/{id}/approve/` - Approve rider

## WebSocket Endpoints

- `ws/notifications/{user_id}/` - Real-time notifications
- `ws/order/{order_id}/` - Real-time order tracking

## Sample Data

To create sample data for testing:

```bash
python manage.py shell
```

```python
from core.models import User
from client.models import Category, Restaurant, MenuItem
from django.contrib.auth import get_user_model

# Create sample categories
Category.objects.create(name="Pizza", slug="pizza")
Category.objects.create(name="Burger", slug="burger")
Category.objects.create(name="Chinese", slug="chinese")

# Create sample restaurant owner
User = get_user_model()
owner = User.objects.create_user(phone="+919876543210", name="Restaurant Owner", role="RESTAURANT")

# Create sample restaurant
restaurant = Restaurant.objects.create(
    owner=owner,
    name="Pizza Palace",
    slug="pizza-palace",
    address="123 Main Street",
    city="Mumbai",
    state="Maharashtra",
    pincode="400001",
    latitude=19.0760,
    longitude=72.8777,
    phone="+919876543210",
    status="APPROVED",
    is_active=True
)

# Create sample menu items
MenuItem.objects.create(
    restaurant=restaurant,
    name="Margherita Pizza",
    price=299.00,
    veg_type="VEG",
    is_available=True
)
```

## 📸 Screenshots

*(Add your screenshots here by replacing the placeholder URLs after uploading to GitHub)*

| Client App | Restaurant Dashboard |
|:---:|:---:|
| ![Client Home](https://via.placeholder.com/400x250?text=Client+Home+Page) | ![Restaurant Panel](https://via.placeholder.com/400x250?text=Restaurant+Dashboard) |
| *Home page with restaurants & food* | *Live order tracking and earnings* |

| Rider App | Admin Dashboard |
|:---:|:---:|
| ![Rider Home](https://via.placeholder.com/400x250?text=Rider+Home+Page) | ![Admin Panel](https://via.placeholder.com/400x250?text=Admin+Dashboard) |
| *Order assignment and map navigation* | *Super admin analytics and controls* |


## 🚀 How to Deploy to GitHub (The Easy Way)

If you haven't uploaded this project to GitHub yet, follow these simple steps using your terminal (VS Code terminal works perfectly):

**1. Create a New Repository on GitHub:**
- Go to [github.com](https://github.com) -> Login -> Click the `+` icon -> **New repository**.
- Name it `Foodis` (or anything you like).
- **IMPORTANT:** Leave the boxes for "Add a README file" and "Add .gitignore" **UNCHECKED**.
- Click **Create repository**.

**2. Initialize and Push (Run these commands in your `d:\Foodis` folder):**
```bash
# Initialize git if you haven't already
git init

# Add all your files
git add .

# Create your first commit
git commit -m "Initial commit: Food ordering platform complete with AI and matching logic"

# Link to your new GitHub repo (Replace YOUR_USERNAME with your actual GitHub username)
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/Foodis.git

# Push the code to GitHub
git push -u origin main
```

*(Note: If you use VS Code, you can also just click the "Source Control" icon on the left, and click "Publish to GitHub".)*


## Production Deployment

1. **Set DEBUG=False in settings**
2. **Configure proper ALLOWED_HOSTS**
3. **Set up proper database credentials**
4. **Configure Redis for production**
5. **Set up SSL certificates**
6. **Use gunicorn/uwsgi for WSGI**
7. **Use daphne for ASGI (WebSockets)**
8. **Set up proper logging**
9. **Configure email backend**
10. **Set up monitoring and error tracking**

## Project Structure

```
Foodis/
├── foodis/              # Main project settings
├── core/                # Core app (User, Auth, Address)
├── client/              # Client-side app
├── restaurant/          # Restaurant-side app
├── rider/               # Rider-side app
├── admin_panel/         # Admin dashboard app
├── ai_engine/           # AI/ML utilities
├── frontend/            # React frontend
├── media/               # User uploaded files
├── static/              # Static files
└── requirements.txt     # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, email support@foodis.com or create an issue in the repository.

## Acknowledgments

- Django and Django REST Framework
- React and Tailwind CSS communities
- All open-source contributors

