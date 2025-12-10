# Fixing "Dangerous Site" Warning on Heroku

## Your Heroku App
Production URL: https://cs3240-a21-12d856f83fd4.herokuapp.com/

## Step-by-Step Fix

### 1. Update Heroku Environment Variables

Run these commands to set the required environment variables:

```bash
# Set DEBUG to False for production
heroku config:set DEBUG=False --app cs3240-a21

# Generate and set a new SECRET_KEY
# First, generate a new key (run in Python):
# from django.core.management.utils import get_random_secret_key
# print(get_random_secret_key())
heroku config:set SECRET_KEY="your-generated-secret-key-here" --app cs3240-a21

# Set allowed hosts
heroku config:set ALLOWED_HOSTS="cs3240-a21-12d856f83fd4.herokuapp.com" --app cs3240-a21

# Set CSRF trusted origins (MUST include https://)
heroku config:set CSRF_TRUSTED_ORIGINS="https://cs3240-a21-12d856f83fd4.herokuapp.com" --app cs3240-a21
```

### 2. Update Google OAuth Configuration

The Google OAuth redirect URI needs to be updated for your Heroku domain.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to: **APIs & Services** → **Credentials**
3. Click on your OAuth 2.0 Client ID
4. Under **Authorized JavaScript origins**, add:
   ```
   https://cs3240-a21-12d856f83fd4.herokuapp.com
   ```
5. Under **Authorized redirect URIs**, add:
   ```
   https://cs3240-a21-12d856f83fd4.herokuapp.com/accounts/google/login/callback/
   ```
6. Click **Save**

### 3. Update Django Site in Production Database

After deploying, you need to update the Site in the production database:

**Option A: Using Heroku Console**
```bash
heroku run python manage.py shell --app cs3240-a21
```

Then in the Python shell:
```python
from django.contrib.sites.models import Site
site = Site.objects.get_current()
site.domain = 'cs3240-a21-12d856f83fd4.herokuapp.com'
site.name = 'CataLog'
site.save()
print(f"Site updated: {site.domain}")
exit()
```

**Option B: Using Django Admin**
1. Go to https://cs3240-a21-12d856f83fd4.herokuapp.com/admin/
2. Log in as superuser
3. Go to **Sites** → **example.com**
4. Change:
   - Domain name: `cs3240-a21-12d856f83fd4.herokuapp.com`
   - Display name: `CataLog`
5. Save

### 4. Verify Google Social App

Check that the Social App is configured correctly:

```bash
heroku run python manage.py shell --app cs3240-a21
```

Then run:
```python
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Get or update the Google app
try:
    google_app = SocialApp.objects.get(provider='google')
    site = Site.objects.get_current()

    # Make sure the site is associated
    if site not in google_app.sites.all():
        google_app.sites.add(site)
        print("✅ Site added to Google Social App")
    else:
        print("✅ Site already associated with Google Social App")

    print(f"Provider: {google_app.provider}")
    print(f"Client ID: {google_app.client_id}")
    print(f"Sites: {[s.domain for s in google_app.sites.all()]}")
except SocialApp.DoesNotExist:
    print("❌ Google Social App not found - you need to create it in Django admin")

exit()
```

### 5. Deploy Updated Settings

Commit and push the changes:

```bash
git add a21/settings.py
git commit -m "Fix Heroku production security settings"
git push heroku main
```

Or if you're on a different branch:
```bash
git push heroku your-branch:main
```

### 6. Run Migrations (if needed)

```bash
heroku run python manage.py migrate --app cs3240-a21
```

### 7. Verify the Fix

After deployment, check:

1. **Visit your site**: https://cs3240-a21-12d856f83fd4.herokuapp.com/
2. **Check for HTTPS**: The URL should show a padlock icon
3. **Test Google Login**: Try logging in with Google
4. **Check browser console**: No security warnings should appear

### Common Issues & Fixes

#### Issue: "Dangerous site" still appears
**Cause**: Heroku HTTPS is working, but the site might be flagged for another reason

**Fix**:
1. Check if site is flagged: https://transparencyreport.google.com/safe-browsing/search?url=cs3240-a21-12d856f83fd4.herokuapp.com
2. If flagged, request a review with Google Safe Browsing
3. Ensure no malicious content or suspicious behavior in your code

#### Issue: "CSRF verification failed"
**Cause**: Missing or incorrect `CSRF_TRUSTED_ORIGINS`

**Fix**:
```bash
heroku config:set CSRF_TRUSTED_ORIGINS="https://cs3240-a21-12d856f83fd4.herokuapp.com" --app cs3240-a21
```

#### Issue: "Error 400 Bad Request"
**Cause**: Domain not in `ALLOWED_HOSTS`

**Fix**:
```bash
heroku config:set ALLOWED_HOSTS="cs3240-a21-12d856f83fd4.herokuapp.com" --app cs3240-a21
```

#### Issue: Google OAuth redirect error
**Cause**: Redirect URI not added in Google Cloud Console

**Fix**: Add `https://cs3240-a21-12d856f83fd4.herokuapp.com/accounts/google/login/callback/` to Google Cloud Console

### 8. Check Current Heroku Config

View all current environment variables:
```bash
heroku config --app cs3240-a21
```

You should see:
- `DEBUG=False`
- `SECRET_KEY=<your-secret-key>`
- `ALLOWED_HOSTS=cs3240-a21-12d856f83fd4.herokuapp.com`
- `CSRF_TRUSTED_ORIGINS=https://cs3240-a21-12d856f83fd4.herokuapp.com`
- Plus your AWS and database credentials

### 9. Heroku SSL Information

Good news: Heroku automatically provides SSL certificates for all apps! Your site already has HTTPS enabled at:
- https://cs3240-a21-12d856f83fd4.herokuapp.com/

You don't need to install or configure SSL manually on Heroku.

### Quick Commands Summary

```bash
# 1. Set environment variables
heroku config:set DEBUG=False --app cs3240-a21
heroku config:set SECRET_KEY="<new-secret-key>" --app cs3240-a21
heroku config:set ALLOWED_HOSTS="cs3240-a21-12d856f83fd4.herokuapp.com" --app cs3240-a21
heroku config:set CSRF_TRUSTED_ORIGINS="https://cs3240-a21-12d856f83fd4.herokuapp.com" --app cs3240-a21

# 2. Deploy
git push heroku main

# 3. Update Site domain
heroku run "python manage.py shell -c \"from django.contrib.sites.models import Site; site = Site.objects.get_current(); site.domain = 'cs3240-a21-12d856f83fd4.herokuapp.com'; site.name = 'CataLog'; site.save(); print('Site updated')\""

# 4. Check config
heroku config --app cs3240-a21
```

## After Following These Steps

The "Dangerous site" warning should be resolved. If you still see it:

1. Clear your browser cache
2. Try in an incognito/private window
3. Check the actual URL - make sure it's HTTPS, not HTTP
4. Wait a few minutes for DNS/SSL propagation
5. Check Google Safe Browsing status

Need help? Check the Heroku logs:
```bash
heroku logs --tail --app cs3240-a21
```
