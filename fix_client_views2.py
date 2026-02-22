import os
import re

filepath = r'd:\Foodis\client\views.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace block 1
pattern1 = r"(for restaurant in queryset:\s*)(res_location = \(float\(restaurant\.latitude\), float\(restaurant\.longitude\)\)\s*if distance\(user_location, res_location\)\.km <= radius:\s*filtered_ids\.append\(restaurant\.id\))"

replacement1 = r"\1try:\n                        \2\n                    except (ValueError, TypeError):\n                        pass"

content = re.sub(pattern1, replacement1, content)

# Replace block 2
pattern2 = r"(for restaurant in self\.queryset:\s*)(restaurant_location = \(float\(restaurant\.latitude\), float\(restaurant\.longitude\)\)\s*dist = distance\(user_location, restaurant_location\)\.km\s*if dist <= radius:\s*restaurants\.append\(\{\s*'restaurant': RestaurantSerializer\(restaurant, context=\{'request': request\}\)\.data,\s*'distance': round\(dist, 2\)\s*\}\))"

replacement2 = r"\1try:\n                    \2\n                except (ValueError, TypeError):\n                    pass"

content = re.sub(pattern2, replacement2, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Regex client/views.py replace complete')
