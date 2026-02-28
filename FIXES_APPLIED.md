# Fixes Applied – OTP Email & Data Recovery

This file summarizes the fixes for:
1. **OTP not arriving in real email**
2. **Recovering old data** (restaurants, riders, users, images) after the database was reset

---

## 1. OTP email fix (real email delivery)

**Cause:**  
- If `EMAIL_HOST_PASSWORD` (SendGrid API key) was not set, the app could not send real emails.  
- SendGrid requires the sender (`EMAIL_FROM`) to be verified.

**Changes made:**
- **`core/email_backends.py`**  
  - Added `ConsoleEmailBackend`: when no API key is set, OTP is printed to the console and the API still returns success (no real email).
- **`foodis/settings.py`**  
  - If `EMAIL_HOST_PASSWORD` is empty → use `ConsoleEmailBackend` (OTP in console only).  
  - If set and `DEBUG` → use `UnsafeEmailBackend` (real SendGrid, relaxed SSL).  
  - If set and production → use standard SMTP backend.
- **`core/services/email_service.py`**  
  - Comment added: for real delivery, set `EMAIL_HOST_PASSWORD` and verify `EMAIL_FROM` in SendGrid.

**What you need to do for real OTP email:**
1. In `.env` (or environment), set:
   ```env
   EMAIL_HOST_PASSWORD=SG.your_actual_sendgrid_api_key
   EMAIL_FROM=foodisindia@gmail.com
   ```
2. In SendGrid dashboard, verify the sender for `EMAIL_FROM` (Single Sender Verification or domain).
3. Restart the backend and test “Send OTP”; check inbox and spam.

---

## 2. Data recovery (restore old restaurants, riders, users, images)

**Cause:**  
Migrations or a DB reset cleared the database; you want to restore existing data, not create new records.

**What was added:**
- **`scripts/restore_database_from_backup.py`**  
  Restores SQLite from a backup file (e.g. `db.sqlite3.backup`). Run from project root:
  ```bash
  python scripts/restore_database_from_backup.py
  ```
- **`DATA_RECOVERY.md`**  
  Step-by-step instructions for:
  - Restoring SQLite from backup
  - Restoring PostgreSQL (production)
  - Restoring local `media/` for images
  - Why OTP might not arrive and how to fix it

**What you need to do to recover data:**
1. **Database**  
   - Get your old database file (e.g. `db.sqlite3` from before the reset).  
   - Copy it to the project root as `db.sqlite3.backup`.  
   - Run: `python scripts/restore_database_from_backup.py`  
   - Then: `python manage.py migrate`
2. **Images**  
   - If you use **local** `media/`: copy your backup `media/` folder over the current one.  
   - If you use **Cloudinary**: no extra step; URLs in the DB work once the DB is restored.

If you do not have a backup of the database, the data cannot be recovered. In future, back up `db.sqlite3` (and `media/` if local) before running migrations or major changes.

---

## 3. File reference

| File | Purpose |
|------|--------|
| `core/email_backends.py` | `ConsoleEmailBackend` + `UnsafeEmailBackend` |
| `foodis/settings.py` | Email backend selection based on `EMAIL_HOST_PASSWORD` and `DEBUG` |
| `core/services/email_service.py` | OTP send (comment for SendGrid) |
| `scripts/restore_database_from_backup.py` | Restore SQLite from backup |
| `DATA_RECOVERY.md` | Full recovery and OTP email instructions |
| `.env.example` | SendGrid and OTP env vars |

All of the above fixes are applied in the codebase; use **DATA_RECOVERY.md** and this file as the single place for “all the fixes” and recovery steps.
