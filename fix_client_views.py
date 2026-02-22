import os

filepath = r'd:\Foodis\client\views.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target1 = '''        if latitude and longitude:
            try:
                user_location = (float(latitude), float(longitude))
                filtered_ids = []
                for restaurant in queryset:
                    res_location = (float(restaurant.latitude), float(restaurant.longitude))
                    if distance(user_location, res_location).km <= radius:
                        filtered_ids.append(restaurant.id)
                queryset = queryset.filter(id__in=filtered_ids)
            except (ValueError, TypeError):
                pass'''

replacement1 = '''        if latitude and longitude:
            try:
                user_location = (float(latitude), float(longitude))
                filtered_ids = []
                for restaurant in queryset:
                    try:
                        res_location = (float(restaurant.latitude), float(restaurant.longitude))
                        if distance(user_location, res_location).km <= radius:
                            filtered_ids.append(restaurant.id)
                    except (ValueError, TypeError):
                        pass
                queryset = queryset.filter(id__in=filtered_ids)
            except (ValueError, TypeError):
                pass'''

target2 = '''            for restaurant in self.queryset:
                restaurant_location = (float(restaurant.latitude), float(restaurant.longitude))
                dist = distance(user_location, restaurant_location).km
                if dist <= radius:
                    restaurants.append({
                        'restaurant': RestaurantSerializer(restaurant, context={'request': request}).data,
                        'distance': round(dist, 2)
                    })'''

replacement2 = '''            for restaurant in self.queryset:
                try:
                    restaurant_location = (float(restaurant.latitude), float(restaurant.longitude))
                    dist = distance(user_location, restaurant_location).km
                    if dist <= radius:
                        restaurants.append({
                            'restaurant': RestaurantSerializer(restaurant, context={'request': request}).data,
                            'distance': round(dist, 2)
                        })
                except (ValueError, TypeError):
                    pass'''

if target1 in content:
    content = content.replace(target1, replacement1)
elif target1.replace('\n', '\r\n') in content:
    content = content.replace(target1.replace('\n', '\r\n'), replacement1.replace('\n', '\r\n'))
else:
    print('Failed to find target1 in client/views.py')

if target2 in content:
    content = content.replace(target2, replacement2)
elif target2.replace('\n', '\r\n') in content:
    content = content.replace(target2.replace('\n', '\r\n'), replacement2.replace('\n', '\r\n'))
else:
    print('Failed to find target2 in client/views.py')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('client/views.py replaced')
