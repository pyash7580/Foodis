"""
Django Management Command: Assign Pexels Images to Dishes
Automatically fetch and assign food images from Pexels API to dishes.
"""

from django.core.management.base import BaseCommand
from client.models import MenuItem
from ai_engine.pexels_image_assigner import PexelsImageAssigner


class Command(BaseCommand):
    help = 'Automatically assign Pexels food images to dishes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dish-id',
            type=str,
            default=None,
            help='Comma-separated dish IDs to process (e.g., 1,2,3)'
        )
        parser.add_argument(
            '--restaurant-id',
            type=int,
            default=None,
            help='Filter dishes by restaurant ID'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of dishes to process'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if dish already has image_url'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate without making actual API calls or database changes'
        )
        parser.add_argument(
            '--rate-limit',
            type=int,
            default=1,
            help='Seconds to wait between API requests (default: 1)'
        )

    def handle(self, *args, **options):
        dish_ids = options['dish_id']
        restaurant_id = options['restaurant_id']
        limit = options['limit']
        force = options['force']
        dry_run = options['dry_run']
        rate_limit = options['rate_limit']

        # Display header
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('   PEXELS IMAGE ASSIGNMENT FOR DISHES'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN MODE - No changes will be made]\n'))

        # Build queryset
        if dish_ids:
            # Process specific dish IDs
            ids = [int(id.strip()) for id in dish_ids.split(',')]
            queryset = MenuItem.objects.filter(id__in=ids).select_related('restaurant', 'category')
            self.stdout.write(f"Processing specific dishes: {ids}")
        else:
            # Process dishes without image_url
            queryset = MenuItem.objects.select_related('restaurant', 'category')
            
            if not force:
                # Only dishes without existing image_url
                queryset = queryset.filter(image_url__isnull=True) | queryset.filter(image_url='')
                self.stdout.write("Processing dishes without image_url...")
            else:
                self.stdout.write(self.style.WARNING("FORCE MODE: Will update all dishes"))
            
            # Filter by restaurant if specified
            if restaurant_id:
                queryset = queryset.filter(restaurant_id=restaurant_id)
                self.stdout.write(f"Filtered by Restaurant ID: {restaurant_id}")
            
            # Apply limit
            if limit:
                queryset = queryset[:limit]
                self.stdout.write(f"Limited to {limit} dishes")

        # Check if any dishes to process
        count = queryset.count()
        if count == 0:
            self.stdout.write(self.style.WARNING('\nNo dishes to process.'))
            return

        # Initialize assigner
        assigner = PexelsImageAssigner()
        
        # Check API key
        if not assigner.pexels_api_key and not dry_run:
            self.stdout.write(self.style.ERROR('\n[ERROR] PEXELS_API_KEY not configured in .env file'))
            self.stdout.write('Please add: PEXELS_API_KEY=your_api_key_here')
            return

        # Process dishes
        if force and not dry_run:
            # For force mode, we need to handle differently
            results = self._process_with_force(assigner, queryset, rate_limit)
        else:
            results = assigner.process_batch(queryset, dry_run=dry_run, rate_limit_seconds=rate_limit)

        # Display final report
        self._display_report(results)

    def _process_with_force(self, assigner, queryset, rate_limit):
        """Process dishes with force flag (override existing image_url)."""
        import time
        
        results = {
            'total': queryset.count(),
            'processed': 0,
            'images_added': 0,
            'skipped': 0,
            'cached': 0,
            'not_found': 0,
            'errors': 0,
            'warnings': [],
            'error_details': [],
            'api_calls': 0,
            'start_time': time.time()
        }
        
        for dish in queryset:
            self.stdout.write(f"[{results['processed'] + 1}/{results['total']}] {dish.name}")
            
            result = assigner.assign_image_url_to_dish(dish, force=True)
            results['processed'] += 1
            
            if result['success']:
                if result['status'] == 'cached':
                    results['cached'] += 1
                else:
                    results['images_added'] += 1
                    results['api_calls'] += 1
                self.stdout.write(self.style.SUCCESS(f"  [OK] {result['message']}"))
            else:
                if result['status'] == 'not_found':
                    results['not_found'] += 1
                    results['warnings'].append(f"No Image Found – {dish.name}")
                else:
                    results['errors'] += 1
                    results['error_details'].append(result['message'])
                self.stdout.write(self.style.WARNING(f"  ! {result['message']}"))
            
            # Rate limiting
            if result.get('status') != 'cached':
                time.sleep(rate_limit)
        
        results['end_time'] = time.time()
        results['duration'] = results['end_time'] - results['start_time']
        
        return results

    def _display_report(self, results):
        """Display comprehensive final report."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('   FINAL REPORT'))
        self.stdout.write('='*60 + '\n')

        # Summary statistics
        self.stdout.write(self.style.SUCCESS(f"Processed: {results['processed']} dishes"))
        self.stdout.write(self.style.SUCCESS(f"Images Added: {results['images_added']}"))
        self.stdout.write(f"Cached Hits: {results['cached']}")
        self.stdout.write(f"Skipped (Already Exists): {results['skipped']}")
        self.stdout.write(f"Not Found: {results['not_found']}")
        
        if results['errors'] > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {results['errors']}"))
        
        # Warnings
        if results['warnings']:
            self.stdout.write('\n' + self.style.WARNING('Warnings:'))
            for warning in results['warnings'][:10]:  # Show first 10
                self.stdout.write(self.style.WARNING(f"  - {warning}"))
            if len(results['warnings']) > 10:
                self.stdout.write(f"  ... and {len(results['warnings']) - 10} more warnings")
        
        # Errors
        if results['error_details']:
            self.stdout.write('\n' + self.style.ERROR('Errors:'))
            for error in results['error_details'][:10]:  # Show first 10
                self.stdout.write(self.style.ERROR(f"  - {error}"))
            if len(results['error_details']) > 10:
                self.stdout.write(f"  ... and {len(results['error_details']) - 10} more errors")
        
        # Performance metrics
        self.stdout.write('\n' + '-'*60)
        duration_min = int(results['duration'] // 60)
        duration_sec = int(results['duration'] % 60)
        self.stdout.write(f"Total Time: {duration_min} minutes {duration_sec} seconds")
        self.stdout.write(f"API Calls Made: {results['api_calls']}")
        self.stdout.write(f"Cache Hits: {results['cached']}")
        
        if results['api_calls'] > 0:
            self.stdout.write(f"Avg Time per API Call: {results['duration'] / results['api_calls']:.2f}s")
        
        self.stdout.write('='*60 + '\n')
        
        # Success/failure message
        if results['errors'] == 0 and results['not_found'] == 0:
            self.stdout.write(self.style.SUCCESS('[OK] All dishes processed successfully!'))
        elif results['images_added'] > 0:
            self.stdout.write(self.style.SUCCESS(f'[OK] Completed with {results["images_added"]} images assigned'))
        else:
            self.stdout.write(self.style.WARNING('[!] Completed with warnings/errors. See details above.'))
