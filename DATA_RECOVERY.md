# Data Recovery – Restore Restaurants, Riders, Users & Images

If your database was reset (e.g. after running migrations or switching to email OTP) and you want to **bring back your old data** (restaurants, riders, users) **without creating new records**, use this guide.

---

## What you need

- A **backup of your database** from before it was cleared:
  - **SQLite**: a copy of `db.sqlite3`
  - **PostgreSQL**: a dump or your host’s backup (e.g. Neon, Render)
- If you stored images in **local `media/`**, a backup of the **`media/`** folder.
- If you use **Cloudinary**, image URLs in the DB will work again once the DB is restored (no file restore needed).

---

## Restore SQLite (local development)

1. **Locate your old database file**  
   e.g. from another machine, backup drive, or a copy you made before migrations.

2. **Copy it into the project root** as:
   ```
   db.sqlite3.backup
   ```
   Or place it anywhere and pass the path in step 4.

3. **Run the restore script** from the project root:
   ```bash
   python scripts/restore_database_from_backup.py
   ```
   If your backup is not named `db.sqlite3.backup`:
   ```bash
   python scripts/restore_database_from_backup.py path/to/your/backup.sqlite3
   ```

4. **Confirm** when prompted. The script will:
   - Replace the current `db.sqlite3` with your backup.
   - Save the current DB as `db.sqlite3.before_restore` (so you can revert if needed).

5. **Run migrations** (in case the backup is from an older schema):
   ```bash
   python manage.py migrate
   ```

6. **Restore images (if you use local media)**  
   Copy your backup `media/` folder over the project’s `media/` directory so logos, dish images, etc. are available again.

---

## Restore PostgreSQL (production)

- Use your provider’s backup/restore (e.g. Neon, Render, Railway).
- Restore the dump into your current database; then run:
  ```bash
  python manage.py migrate
  ```
- Images: if you use Cloudinary, no extra step. If you use local/media storage, restore the media files on the server as well.

---

## OTP email not arriving in real inbox

OTP is sent via **SendGrid**. If emails are not received:

1. **Set the SendGrid API key** in your environment (or `.env`):
   ```
   EMAIL_HOST_PASSWORD=SG.your_sendgrid_api_key_here
   ```
   If this is not set, the app uses a **console-only** backend: OTP is printed in the terminal and **no real email** is sent.

2. **Verify the sender in SendGrid**  
   The address in `EMAIL_FROM` (e.g. `foodisindia@gmail.com`) must be verified in SendGrid (Single Sender Verification or domain authentication). Otherwise SendGrid may reject or drop messages.

3. **Check spam**  
   First emails often land in spam until reputation improves.

4. **Test**  
   After setting `EMAIL_HOST_PASSWORD` and verifying `EMAIL_FROM`, trigger “Send OTP” and check inbox (and spam). The server log will show whether the send succeeded.

---

## Summary

| Goal | Action |
|------|--------|
| Restore old DB (SQLite) | Copy backup to `db.sqlite3.backup`, run `python scripts/restore_database_from_backup.py`, then `python manage.py migrate`. |
| Restore old DB (Postgres) | Use provider backup/restore, then `python manage.py migrate`. |
| Restore images (local) | Copy backup `media/` folder over project `media/`. |
| OTP in real email | Set `EMAIL_HOST_PASSWORD` (SendGrid API key) and verify `EMAIL_FROM` in SendGrid. |

Your existing restaurant, rider, and user data (and images, if restored as above) will be back; no need to create new records.
