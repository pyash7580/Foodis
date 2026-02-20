from django.core.management.base import BaseCommand
from client.models import MenuItem, Restaurant


class Command(BaseCommand):
    help = 'Generate a simple text file with all dish names in table format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='ALL_DISHES_LIST.txt',
            help='Output file path'
        )

    def handle(self, *args, **options):
        file_path = options['file']

        self.stdout.write(self.style.SUCCESS(f'Generating dish list to {file_path}...'))

        # Get all restaurants
        restaurants = Restaurant.objects.all().order_by('name')

        with open(file_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 100 + "\n")
            f.write(" " * 35 + "ALL DISHES - FOODIS PLATFORM\n")
            f.write("=" * 100 + "\n\n")

            total_dishes = 0

            for restaurant in restaurants:
                # Get dishes for this restaurant
                dishes = MenuItem.objects.filter(restaurant=restaurant).order_by('name')
                dish_count = dishes.count()
                total_dishes += dish_count

                if dish_count == 0:
                    continue

                # Restaurant header
                f.write("\n" + "=" * 100 + "\n")
                f.write(f"RESTAURANT: {restaurant.name}\n")
                f.write(f"Location: {restaurant.city}\n")
                f.write(f"Total Dishes: {dish_count}\n")
                f.write("=" * 100 + "\n\n")

                # Table header
                f.write(f"{'No.':<6} {'Dish Name':<50} {'Type':<12} {'Price':>10}\n")
                f.write("-" * 100 + "\n")

                # Dish rows
                for idx, dish in enumerate(dishes, 1):
                    veg_type = dish.veg_type if dish.veg_type else 'VEG'
                    price = f"Rs. {dish.price:.2f}"
                    
                    # Truncate long names
                    dish_name = dish.name[:47] + "..." if len(dish.name) > 50 else dish.name
                    
                    f.write(f"{idx:<6} {dish_name:<50} {veg_type:<12} {price:>10}\n")

                f.write("\n")

            # Summary footer
            f.write("\n" + "=" * 100 + "\n")
            f.write(f"TOTAL DISHES ACROSS ALL RESTAURANTS: {total_dishes}\n")
            f.write("=" * 100 + "\n")

        self.stdout.write(self.style.SUCCESS(
            f'[OK] Generated {total_dishes} dishes to {file_path}'
        ))
