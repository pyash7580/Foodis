# Media folder – logos, covers, dish images

Place your image files here so they show as **restaurant logos**, **cover images**, and **dish images**.

## Folder structure

- **`restaurants/logos/`** – Restaurant logo images (e.g. `restaurant_54.png`, or by name).
- **`restaurants/covers/`** – Restaurant cover/banner images.
- **`menu_items/`** – Dish images (optional; can use subfolders).

## How it works

- The app loads images from **`/media/...`** (this folder is served at that URL).
- Example: `public/media/restaurants/logos/biryani-boulevard.png` → use path **`/media/restaurants/logos/biryani-boulevard.png`** in the app or API.
- If the API returns paths like **`/media/restaurants/xyz.jpg`**, put the file at **`public/media/restaurants/xyz.jpg`** and it will display.

## Quick start

1. Create subfolders: `restaurants/logos`, `restaurants/covers`, `menu_items`.
2. Add your images (e.g. PNG, JPG).
3. In the backend or database, use paths like `/media/restaurants/logos/filename.png` so the frontend can find them here.
