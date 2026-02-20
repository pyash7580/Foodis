import os
import time
import requests
import uuid
from django.conf import settings
from django.core.files.base import ContentFile
from client.models import MenuItem
from django.core.cache import cache
import openai
from decouple import config

# Configure OpenAI
openai.api_key = config('OPENAI_API_KEY', default='')

class DishImageGenerator:
    def __init__(self):
        self.api_key = openai.api_key
        
    def generate_dish_prompt(self, dish):
        """
        Create a detailed prompt for the dish
        """
        cuisine = dish.restaurant.cuisine if dish.restaurant and dish.restaurant.cuisine else "delicious"
        category = dish.category.name if dish.category else "food"
        
        prompt = (
            f"High-quality professional restaurant food photography of {dish.name}, "
            f"{cuisine} cuisine, {category} category. "
            f"Appetizing lighting, realistic plating, shallow depth of field, 8k resolution, "
            f"cinematic lighting, photorealistic, no text, no watermarks, clean background."
        )
        return prompt

    def generate_image(self, prompt):
        """
        Generate image using OpenAI DALL-E 3 or 2
        """
        if not self.api_key:
            print("Error: OPENAI_API_KEY not found.")
            return None

        try:
            # Using DALL-E 3 for better quality if available, or DALL-E 2
            # Adjust model based on cost preference, DALL-E 2 is cheaper for bulk
            response = openai.images.generate(
                model="dall-e-2", 
                prompt=prompt,
                n=1,
                size="512x512"
            )
            
            # Get the image URL
            image_url = response.data[0].url
            return image_url
            
        except Exception as e:
            print(f"Error generating image: {e}")
            return None

    def save_image_locally(self, image_url, dish_id):
        """
        Download image and save to media/dishes/
        """
        if not image_url:
            return None
            
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                file_name = f"dish_{dish_id}.jpg"
                return ContentFile(response.content, name=f"dishes/{file_name}")
        except Exception as e:
            print(f"Error saving image: {e}")
        
        return None

    def process_batch(self, limit=20, dry_run=False):
        """
        Process a batch of dishes without images
        """
        # Fetch dishes without images or with empty images
        dishes = MenuItem.objects.filter(image='').order_by('id')[:limit]
        
        results = {
            'total': dishes.count(),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        print(f"Found {results['total']} dishes to process.")
        
        for dish in dishes:
            print(f"Processing Dish ID {dish.id}: {dish.name}...")
            
            if dry_run:
                print(f"[DRY RUN] Would generate for: {dish.name}")
                results['success'] += 1
                continue
                
            try:
                # 1. Generate Prompt
                prompt = self.generate_dish_prompt(dish)
                
                # 2. Call AI API
                image_url = self.generate_image(prompt)
                
                if image_url:
                    # 3. Save Image
                    image_content = self.save_image_locally(image_url, dish.id)
                    
                    if image_content:
                        # 4. Update DB
                        dish.image = image_content
                        dish.save()
                        results['success'] += 1
                        print(f"Successfully updated {dish.name}")
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Failed to save image for {dish.name}")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to generate image for {dish.name}")
                
                # Sleep to avoid rate limits
                time.sleep(2)
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
                print(f"Error processing {dish.name}: {e}")
                
        return results

    def process_single(self, dish_id):
        """
        Process a single dish by ID
        """
        try:
            dish = MenuItem.objects.get(id=dish_id)
            if dish.image:
                return {'status': 'skipped', 'message': 'Image already exists'}
                
            prompt = self.generate_dish_prompt(dish)
            image_url = self.generate_image(prompt)
            
            if image_url:
                image_content = self.save_image_locally(image_url, dish.id)
                if image_content:
                    dish.image = image_content
                    dish.save()
                    return {'status': 'success', 'url': dish.image.url}
            
            return {'status': 'failed', 'message': 'Generation failed'}
            
        except MenuItem.DoesNotExist:
            return {'status': 'error', 'message': 'Dish not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
