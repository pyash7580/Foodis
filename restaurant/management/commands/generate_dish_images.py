from django.core.management.base import BaseCommand
from ai_engine.image_generation import DishImageGenerator
from ai_engine.stock_image_fetcher import StockImageFetcher
from client.models import MenuItem

class Command(BaseCommand):
    help = 'Generate images for dishes that do not have one'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Number of dishes to process per batch'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate generation without calling API'
        )
        parser.add_argument(
            '--source',
            type=str,
            default='stock',
            choices=['ai', 'stock'],
            help='Image source: "ai" (OpenAI DALL-E) or "stock" (Pexels API)'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']
        source = options['source']
        
        self.stdout.write(self.style.SUCCESS(
            f"Starting bulk image generation (Source: {source.upper()}, Limit: {limit})..."
        ))
        
        # Select appropriate generator
        if source == 'ai':
            generator = DishImageGenerator()
            
            # Check API Key for AI
            if not generator.api_key and not dry_run:
                self.stdout.write(self.style.ERROR("OPENAI_API_KEY is missing. Please set it in .env"))
                return
        else:  # stock
            generator = StockImageFetcher()
            
            # Check API Key for Stock
            if not generator.pexels_api_key and not dry_run:
                self.stdout.write(self.style.WARNING(
                    "PEXELS_API_KEY is missing. Please set it in .env for best results."
                ))
                return
            
        try:
            results = generator.process_batch(limit=limit, dry_run=dry_run)
            
            self.stdout.write(self.style.SUCCESS(f"Batch Processing Completed:"))
            self.stdout.write(f"- Total Processed: {results['total']}")
            self.stdout.write(f"- Success: {results['success']}")
            self.stdout.write(f"- Failed: {results['failed']}")
            if results['errors']:
                self.stdout.write(f"- Errors: {len(results['errors'])} errors")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Critical Error: {str(e)}"))

