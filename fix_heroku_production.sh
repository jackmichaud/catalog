#!/bin/bash

# Script to fix Heroku production deployment
# Run this script to configure all necessary environment variables

echo "🚀 Fixing Heroku Production Deployment"
echo "========================================"
echo ""

APP_NAME="cs3240-a21"
HEROKU_DOMAIN="cs3240-a21-12d856f83fd4.herokuapp.com"

# Check if heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed. Please install it first:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo "✅ Heroku CLI found"
echo ""

# Generate a new SECRET_KEY
echo "📝 Generating a new SECRET_KEY..."
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
echo "✅ SECRET_KEY generated"
echo ""

# Set environment variables
echo "🔧 Setting Heroku environment variables..."
echo ""

echo "Setting DEBUG=False..."
heroku config:set DEBUG=False --app $APP_NAME

echo "Setting SECRET_KEY..."
heroku config:set SECRET_KEY="$SECRET_KEY" --app $APP_NAME

echo "Setting ALLOWED_HOSTS..."
heroku config:set ALLOWED_HOSTS="$HEROKU_DOMAIN" --app $APP_NAME

echo "Setting CSRF_TRUSTED_ORIGINS..."
heroku config:set CSRF_TRUSTED_ORIGINS="https://$HEROKU_DOMAIN" --app $APP_NAME

echo ""
echo "✅ Environment variables set!"
echo ""

# Show current config
echo "📋 Current Heroku configuration:"
heroku config --app $APP_NAME

echo ""
echo "========================================"
echo "✅ Configuration complete!"
echo ""
echo "Next steps:"
echo "1. Deploy to Heroku: git push heroku main"
echo "2. Update Django Site domain:"
echo "   heroku run python manage.py shell --app $APP_NAME"
echo "   Then run:"
echo "   from django.contrib.sites.models import Site"
echo "   site = Site.objects.get_current()"
echo "   site.domain = '$HEROKU_DOMAIN'"
echo "   site.name = 'CataLog'"
echo "   site.save()"
echo ""
echo "3. Update Google OAuth redirect URIs in Google Cloud Console:"
echo "   - Authorized JavaScript origins: https://$HEROKU_DOMAIN"
echo "   - Authorized redirect URIs: https://$HEROKU_DOMAIN/accounts/google/login/callback/"
echo ""
echo "4. Visit: https://$HEROKU_DOMAIN"
echo ""
