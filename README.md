# Universal LLMs.txt Generator

<div align="center">

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Platforms](https://img.shields.io/badge/platforms-WordPress%20%7C%20Static%20%7C%20Django%20%7C%20Flask%20%7C%20Any-brightgreen.svg)

**A powerful, universal Python tool that automatically generates and maintains `llms.txt` files for ANY website, regardless of the technology stack.**

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-installation-methods) • [🤝 Contributing](#-contributing) • [💬 Support](#-support)

</div>

---

## 🌟 What is LLMs.txt?

LLMs.txt is a proposed standard for websites to provide structured information about their content to Large Language Models (LLMs). It helps AI systems better understand and index your website's content, similar to how `robots.txt` helps search engines.

**Learn more:** [LLMs.txt Specification](https://llmstxt.org/) | [Why Your Website Needs LLMs.txt](https://llmstxt.org/why)

---

## ✨ Key Features

### 🌐 **Universal Compatibility - Works with ANY Stack**
- **WordPress** - Direct REST API integration
- **Static Sites** - Hugo, Jekyll, Gatsby, Next.js, Nuxt.js
- **Python Frameworks** - Django, Flask, FastAPI
- **JavaScript Frameworks** - React, Vue, Angular (with static generation)
- **PHP Frameworks** - Laravel, Symfony, CodeIgniter
- **Ruby Frameworks** - Rails, Sinatra
- **Any Website** - Sitemap.xml based extraction (universal fallback)

### 🔄 **Auto-Update System - Never Miss New Content**
- ⚡ **Real-time Updates** - Webhook support for instant updates
- ⏰ **Scheduled Updates** - Cron job integration (hourly/daily/weekly)
- 👁️ **File Watching** - Monitor content directories for changes
- 🔗 **CMS Integration** - Direct hooks into WordPress, Django, etc.
- 🧠 **Smart Caching** - Only updates when content actually changes

### 🛠 **Automatic File Management**
- 📄 **LLMs.txt Generation** - Creates properly formatted llms.txt files
- 🗺️ **Sitemap.xml Updates** - Automatically adds llms.txt to your sitemap
- 🤖 **Robots.txt Updates** - Adds llms.txt reference to robots.txt  
- 💾 **Backup System** - Keeps backups of all modified files

### 🎯 **Easy Installation & Setup**
- 🚀 **One-Command Install** - Works on any platform
- 🐳 **Docker Support** - Containerized deployment
- ⚙️ **GitHub Actions** - CI/CD integration
- 🔧 **Plugin System** - Easy to extend and customize

---

## 📋 System Requirements

- **Python 3.8+** (Python 3.9+ recommended)
- **Internet connection** (for API-based extractors)
- **Write permissions** to your website directory

### Install Python (if not already installed):

<details>
<summary><strong>🐧 Linux (Ubuntu/Debian)</strong></summary>

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv
```
</details>

<details>
<summary><strong>🍎 macOS</strong></summary>

```bash
# Using Homebrew (recommended)
brew install python3

# Or download from python.org
# https://www.python.org/downloads/mac-osx/
```
</details>

<details>
<summary><strong>🪟 Windows</strong></summary>

```powershell
# Download from python.org and install
# https://www.python.org/downloads/windows/

# Or using Chocolatey
choco install python3

# Or using winget
winget install Python.Python.3
```
</details>

---

## 🚀 Quick Start

Get up and running in under 2 minutes:

```bash
# 1. Install the generator
pip install git+https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git

# 2. Navigate to your website directory
cd /path/to/your/website

# 3. Initialize configuration (auto-detects your setup)
python -m llms_txt_generator --init

# 4. Generate your first llms.txt
python -m llms_txt_generator --generate

# 5. Set up automatic updates (optional)
python -m llms_txt_generator --setup-cron --interval daily --time "02:00"
```

**That's it!** Your website now has a proper `llms.txt` file that auto-updates whenever your content changes.

---

## 🔧 Installation Methods

### Method 1: Quick Install (Recommended)

**For most users - works with any website:**

```bash
# Install directly from GitHub
pip install git+https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git

# Or download and install with one command
curl -sSL https://raw.githubusercontent.com/AsifMinar/Universal-LLMS.txt-Generator/main/install.sh | bash
```

### Method 2: Manual Installation

**For developers who want to customize:**

```bash
# Clone the repository
git clone https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git
cd Universal-LLMS.txt-Generator

# Install dependencies
pip install -r requirements.txt

# Make the script executable
chmod +x llms_txt_generator.py
```

### Method 3: Docker (Recommended for Production)

**For scalable, containerized deployments:**

```bash
# Create a directory for your website
mkdir my-website && cd my-website

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  llms-generator:
    image: python:3.9-slim
    volumes:
      - ./:/app/website
      - ./config:/app/config
    working_dir: /app
    command: >
      bash -c "
        pip install git+https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git &&
        python -m llms_txt_generator --config /app/config/llms_config.yaml --webhook --port 8080
      "
    ports:
      - "8080:8080"
EOF

# Run with Docker Compose
docker-compose up -d
```

---

## 🛠 Platform-Specific Setup Guides

### 🟦 WordPress Integration

WordPress is one of the easiest to set up because it has a built-in REST API.

#### Step 1: Install the Generator
```bash
# Install on your server or local machine
pip install git+https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git
```

#### Step 2: Initialize for WordPress
```bash
# Navigate to your WordPress root directory
cd /path/to/your/wordpress/site

# Initialize configuration
python -m llms_txt_generator --init --type wordpress
```

#### Step 3: Configure Settings
Edit the generated `llms_config.yaml`:

```yaml
site_url: 'https://yourwordpresssite.com'
site_name: 'Your WordPress Site'
description: 'Your site description'
extractor: 'wordpress'

wordpress:
  api_url: 'auto'  # Will auto-detect your WP REST API
  per_page: 100
  post_types: ['posts', 'pages']
  exclude_categories: ['uncategorized', 'private']

output_path: './llms.txt'
auto_update_sitemap: true
auto_update_robots: true
```

#### Step 4: Generate LLMs.txt
```bash
# Generate your first llms.txt
python -m llms_txt_generator --generate

# The script will create:
# - llms.txt (main file)
# - Update sitemap.xml (adds llms.txt entry)
# - Update robots.txt (allows llms.txt access)
```

#### Step 5: Set Up Auto-Updates
```bash
# Option A: Cron job (recommended)
python -m llms_txt_generator --setup-cron --interval daily --time "02:00"

# Option B: Webhook server for real-time updates
python -m llms_txt_generator --webhook --port 8080 &
```

#### Step 6: WordPress Plugin Integration (Optional)
Add this to your theme's `functions.php` or create a custom plugin:

```php
<?php
// Auto-update llms.txt when posts are saved
function update_llms_txt_on_save($post_id) {
    if (wp_is_post_revision($post_id) || wp_is_post_autosave($post_id)) {
        return;
    }
    
    // Trigger webhook update
    $webhook_url = 'http://localhost:8080/update';
    $webhook_data = array('secret' => 'your-webhook-secret');
    
    wp_remote_post($webhook_url, array(
        'body' => json_encode($webhook_data),
        'headers' => array('Content-Type' => 'application/json'),
        'timeout' => 10
    ));
}

add_action('save_post', 'update_llms_txt_on_save');
add_action('delete_post', 'update_llms_txt_on_save');
?>
```

---

### 🟩 Static Sites (Hugo, Jekyll, Gatsby, Next.js, etc.)

Perfect for blogs, documentation sites, and marketing websites.

#### Step 1: Install in Your Static Site Directory
```bash
# Navigate to your static site root
cd /path/to/your/static/site

# Install the generator
pip install git+https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git
```

#### Step 2: Initialize for Static Sites
```bash
# Initialize with your content directory
python -m llms_txt_generator --init --type static --content-dir ./content
```

#### Step 3: Configure for Your Static Site Generator

**For Hugo:**
```yaml
site_url: 'https://yourhugosite.com'
site_name: 'Your Hugo Site'
extractor: 'static'

static:
  content_directory: './content'
  file_patterns: ['*.md', '*.html']
  exclude_patterns: ['drafts/*', '_index.md']

output_path: './static/llms.txt'  # Hugo static files
```

**For Jekyll:**
```yaml
site_url: 'https://yourjekyllsite.com'
site_name: 'Your Jekyll Site'
extractor: 'static'

static:
  content_directory: './_posts'
  file_patterns: ['*.md', '*.markdown']
  exclude_patterns: ['_drafts/*']

output_path: './llms.txt'  # Jekyll root
```

**For Gatsby/Next.js:**
```yaml
site_url: 'https://yourgatsby.com'
site_name: 'Your Gatsby Site'
extractor: 'static'

static:
  content_directory: './content'
  file_patterns: ['*.md', '*.mdx']
  exclude_patterns: ['drafts/*']

output_path: './public/llms.txt'  # Gatsby/Next.js public folder
```

#### Step 4: Integrate with Your Build Process

**Hugo (add to your build script):**
```bash
#!/bin/bash
# Generate llms.txt before building
python -m llms_txt_generator --generate
# Build Hugo site
hugo --minify
```

**Jekyll (add to _config.yml):**
```yaml
plugins:
  - jekyll-feed
  
# Add build hook
gems:
  - jekyll-feed

# Create _plugins/llms_txt_generator.rb
```

**GitHub Actions Integration:**
```yaml
# .github/workflows/build.yml
name: Build and Deploy
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install LLMs.txt Generator
        run: pip install git+https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git
        
      - name: Generate LLMs.txt
        run: python -m llms_txt_generator --generate
        
      - name: Setup Node.js (for Hugo/Gatsby/Next.js)
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          
      - name: Build site
        run: |
          npm install
          npm run build  # or hugo, gatsby build, etc.
          
      - name: Deploy
        # Your deployment steps here
```

#### Step 5: Set Up File Watching for Development
```bash
# Watch content directory for changes during development
python -m llms_txt_generator --watch --content-dir ./content --debounce 3
```

---

### 🟨 Django Integration

Perfect integration with Django's ORM and URL system.

#### Step 1: Install in Your Django Project
```bash
# Navigate to your Django project
cd /path/to/your/django/project

# Install the generator
pip install git+https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git

# Add to requirements.txt
echo "git+https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git" >> requirements.txt
```

#### Step 2: Configure Django Settings
```python
# settings.py
INSTALLED_APPS = [
    # ... your existing apps
    'django.contrib.sitemaps',  # Enable if not already
]

# LLMs.txt Configuration
LLMS_TXT_CONFIG = {
    'site_url': 'https://yourdjangosite.com',
    'site_name': 'Your Django Site',
    'extractor': 'django',
    'output_path': os.path.join(BASE_DIR, 'static', 'llms.txt'),
    'django': {
        'models': ['blog.Post', 'pages.Page'],  # Your content models
        'url_field': 'get_absolute_url',
        'title_field': 'title',
        'content_field': 'content',
    }
}
```

#### Step 3: Create Django Management Command
```python
# management/commands/generate_llms_txt.py
from django.core.management.base import BaseCommand
from django.conf import settings
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class Command(BaseCommand):
    help = 'Generate LLMs.txt file'
    
    def handle(self, *args, **options):
        from llms_txt_generator import LLMsTxtGenerator
        
        config = getattr(settings, 'LLMS_TXT_CONFIG', {})
        generator = LLMsTxtGenerator(config_dict=config)
        
        success = generator.generate_llms_txt()
        if success:
            self.stdout.write(
                self.style.SUCCESS('Successfully generated llms.txt')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No updates needed')
            )
```

#### Step 4: Create Django Views (Optional)
```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json

@csrf_exempt
@require_http_methods(["POST"])
def update_llms_txt(request):
    """Webhook endpoint to update llms.txt"""
    try:
        from llms_txt_generator import LLMsTxtGenerator
        
        config = getattr(settings, 'LLMS_TXT_CONFIG', {})
        generator = LLMsTxtGenerator(config_dict=config)
        
        success = generator.generate_llms_txt()
        
        return JsonResponse({
            'status': 'success' if success else 'no_update',
            'message': 'LLMs.txt updated' if success else 'No update needed'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ... your existing URLs
    path('update-llms-txt/', views.update_llms_txt, name='update_llms_txt'),
]
```

#### Step 5: Set Up Auto-Updates
```python
# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.management import call_command
from .models import Post, Page  # Your content models

@receiver([post_save, post_delete], sender=Post)
@receiver([post_save, post_delete], sender=Page)
def update_llms_txt_on_content_change(sender, **kwargs):
    """Auto-update llms.txt when content changes"""
    try:
        call_command('generate_llms_txt')
    except Exception as e:
        print(f"Error updating llms.txt: {e}")

# apps.py
from django.apps import AppConfig

class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'your_app'
    
    def ready(self):
        import your_app.signals
```

#### Step 6: Run Generation
```bash
# Generate llms.txt manually
python manage.py generate_llms_txt

# Set up cron job for regular updates
# Add to crontab: 0 2 * * * cd /path/to/django/project && python manage.py generate_llms_txt
```

---

### 🟪 Flask Integration

Lightweight integration for Flask applications.

#### Step 1: Install in Your Flask Project
```bash
# Navigate to your Flask project
cd /path/to/your/flask/app

# Install the generator
pip install git+https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git
```

#### Step 2: Create Flask Configuration
```python
# app.py or config.py
LLMS_TXT_CONFIG = {
    'site_url': 'https://yourflaskapp.com',
    'site_name': 'Your Flask App',
    'extractor': 'sitemap',  # or 'static' if you have markdown files
    'output_path': './static/llms.txt',
    'sitemap_url': 'https://yourflaskapp.com/sitemap.xml'
}
```

#### Step 3: Create Flask Commands
```python
# app.py
from flask import Flask
import click
from llms_txt_generator import LLMsTxtGenerator

app = Flask(__name__)

@app.cli.command()
def generate_llms_txt():
    """Generate LLMs.txt file"""
    generator = LLMsTxtGenerator(config_dict=app.config['LLMS_TXT_CONFIG'])
    success = generator.generate_llms_txt()
    
    if success:
        click.echo('✅ LLMs.txt generated successfully!')
    else:
        click.echo('ℹ️ No updates needed')

@app.route('/webhook/update-llms-txt', methods=['POST'])
def webhook_update_llms_txt():
    """Webhook endpoint for updates"""
    try:
        generator = LLMsTxtGenerator(config_dict=app.config['LLMS_TXT_CONFIG'])
        success = generator.generate_llms_txt()
        
        return {
            'status': 'success' if success else 'no_update',
            'message': 'LLMs.txt updated' if success else 'No update needed'
        }
    except Exception as e:
        return {'error': str(e)}, 500
```

#### Step 4: Run Generation
```bash
# Generate llms.txt
flask generate-llms-txt

# Or run with Python
python -c "
from app import app
from llms_txt_generator import LLMsTxtGenerator
generator = LLMsTxtGenerator(config_dict=app.config['LLMS_TXT_CONFIG'])
generator.generate_llms_txt()
"
```

---

### 🔶 Universal Sitemap Method (Works with ANY Website)

This method works with any website that has a sitemap.xml file, regardless of the technology stack.

#### Step 1: Install Anywhere
```bash
# Install on your server, local machine, or CI/CD
pip install git+https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git
```

#### Step 2: Initialize with Sitemap
```bash
# Initialize for any website
python -m llms_txt_generator --init --type sitemap
```

#### Step 3: Configure for Any Website
```yaml
# Works with ANY website that has sitemap.xml
site_url: 'https://anywebsite.com'
site_name: 'Any Website'
description: 'Works with any technology stack'
extractor: 'sitemap'

# Optional: Custom sitemap URL
sitemap_url: 'https://anywebsite.com/custom-sitemap.xml'

# Output to any location
output_path: '/path/to/website/public/llms.txt'
```

#### Step 4: Generate and Deploy
```bash
# Generate llms.txt
python -m llms_txt_generator --generate

# Copy to your website (if needed)
cp llms.txt /path/to/your/website/public/

# Or upload via FTP, rsync, etc.
rsync -av llms.txt user@yourserver:/var/www/html/
```

#### Step 5: Automate with Cron
```bash
# Set up automatic updates
crontab -e

# Add this line for daily updates at 2 AM
0 2 * * * cd /path/to/generator && python -m llms_txt_generator --generate && rsync -av llms.txt user@yourserver:/var/www/html/
```

---

## 🔄 Auto-Update Configuration Guide

### Method 1: Cron Jobs (Recommended for Most Cases)
```bash
# Daily updates at 2 AM
python -m llms_txt_generator --setup-cron --interval daily --time "02:00"

# Hourly updates
python -m llms_txt_generator --setup-cron --interval hourly

# Weekly updates on Sunday at 3 AM
python -m llms_txt_generator --setup-cron --interval weekly --time "03:00"
```

### Method 2: Webhook Server (Real-time Updates)
```bash
# Start webhook server
python -m llms_txt_generator --webhook --port 8080 --secret your-webhook-secret

# Your CMS/application can POST to:
# http://yourserver:8080/update
# With JSON: {"secret": "your-webhook-secret"}
```

### Method 3: File Watching (Development)
```bash
# Watch content directory for changes
python -m llms_txt_generator --watch --content-dir ./content --debounce 5
```

### Method 4: CI/CD Integration (GitHub Actions, etc.)
See the GitHub Actions example in the Static Sites section above.

---

## 🧪 Testing Your Setup

### Quick Test
```bash
# Test your configuration
python -m llms_txt_generator --validate-config

# Test content extraction without generating files
python -m llms_txt_generator --test

# Test with specific URL
python -m llms_txt_generator --test --url https://yourwebsite.com
```

### Verify Generated Files
```bash
# Check if llms.txt was created
ls -la llms.txt

# View the content
head -20 llms.txt

# Check if sitemap.xml was updated
grep -i "llms.txt" sitemap.xml

# Check if robots.txt was updated
grep -i "llms.txt" robots.txt
```

---

## 🔧 Advanced Configuration

### Complete Configuration Example
```yaml
# Complete configuration with all options
site_url: 'https://yourwebsite.com'
site_name: 'Your Website'
description: 'Website description for AI systems'
contact_email: 'contact@yourwebsite.com'

# Extractor type: wordpress, static, django, flask, sitemap
extractor: 'wordpress'

# Output settings
output_path: './llms.txt'
max_items: 1000
min_word_count: 50
include_drafts: false

# Auto-update settings
auto_update: true
auto_update_sitemap: true
auto_update_robots: true
backup_files: true

# Cache settings
cache_file: '.llms_cache.json'
cache_duration: 3600  # 1 hour

# Content filtering
include_patterns: ['*.html', '*.md', '*.php']
exclude_patterns: ['admin/*', 'private/*', 'wp-admin/*']

# WordPress specific
wordpress:
  api_url: 'auto'
  per_page: 100
  post_types: ['posts', 'pages', 'products']
  exclude_categories: ['uncategorized', 'private']

# Static site specific
static:
  content_directory: './content'
  file_patterns: ['*.md', '*.html', '*.mdx']
  front_matter: true
  excerpt_length: 200

# Django specific
django:
  models: ['blog.Post', 'pages.Page', 'products.Product']
  url_field: 'get_absolute_url'
  title_field: 'title'
  content_field: 'content'

# Webhook settings
webhook:
  enabled: true
  port: 8080
  secret: 'your-secure-webhook-secret'
  allowed_ips: ['127.0.0.1', '192.168.1.0/24']
```

---

## 🐳 Docker Deployment

### Simple Docker Usage
```bash
# Create a directory for your project
mkdir llms-txt-project && cd llms-txt-project

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  llms-generator:
    image: python:3.9-slim
    volumes:
      - ./website:/app/website
      - ./config:/app/config
    working_dir: /app
    environment:
      - PYTHONUNBUFFERED=1
    command: >
      bash -c "
        pip install git+https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git &&
        cd /app/website &&
        python -m llms_txt_generator --config /app/config/llms_config.yaml --webhook --port 8080
      "
    ports:
      - "8080:8080"
    restart: unless-stopped
EOF

# Create config directory
mkdir -p config website

# Create configuration
cat > config/llms_config.yaml << 'EOF'
site_url: 'https://yourwebsite.com'
site_name: 'Your Website'
extractor: 'sitemap'
output_path: '/app/website/llms.txt'
auto_update: true
webhook:
  enabled: true
  port: 8080
  secret: 'your-webhook-secret'
EOF

# Start the service
docker-compose up -d

# Check logs
docker-compose logs -f
```

---

## 🚨 Troubleshooting Guide

### Common Issues and Solutions

#### 1. Permission Denied Errors
```bash
# Solution: Fix file permissions
chmod +x llms_txt_generator.py
sudo chown -R $USER:$USER /path/to/your/website
```

#### 2. WordPress REST API Not Accessible
```bash
# Check if WordPress REST API is working
curl https://yoursite.com/wp-json/wp/v2/posts

# If it fails, check WordPress settings:
# - Go to Settings > Permalinks and click "Save Changes"
# - Check if any security plugins are blocking the API
# - Add this to wp-config.php if needed:
# add_filter('rest_authentication_errors', '__return_true');
```

#### 3. Python Module Not Found
```bash
# Ensure you're using the right Python version
python3 --version

# Install in the correct environment
pip3 install --user git+https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install git+https://github.com/AsifMinar/Universal-LLMS.txt-Generator.git
```

#### 4. Sitemap.xml Not Found
```bash
# Check common sitemap locations
curl https://yoursite.com/sitemap.xml
curl https://yoursite.com/sitemap_index.xml
curl https://yoursite.com/wp-sitemap.xml

# Generate sitemap if missing (WordPress)
# Install Yoast SEO or similar plugin

# Generate sitemap for static sites
# Hugo: set enableRobotsTXT = true in config
# Jekyll: use jekyll-sitemap plugin
```

#### 5. Webhook Not Receiving Requests
```bash
# Check if the port is open
netstat -tulpn | grep :8080

# Check firewall
sudo ufw allow 8080

# Test webhook manually
curl -X POST http://localhost:8080/update \
  -H "Content-Type: application/json" \
  -d '{"secret": "your-webhook-secret"}'
```

#### 6. Cron Job Not Working
```bash
# Check if cron service is running
sudo systemctl status cron

# Check cron logs
sudo tail -f /var/log/cron.log

# Test cron command manually
cd /path/to/generator && python -m llms_txt_generator --generate
```

---

## 🤝 Contributing

We welcome contributions from developers of all skill levels! Here's how you can help:

### Types of Contributions
- 🐛 **Bug Reports** - Found an issue? Let us know!
- 💡 **Feature Requests** - Have an idea? We'd love to hear it!
- 📝 **Documentation** - Help improve our guides
- 🔧 **Code** - Submit pull requests
- 🧪 **Testing** - Test with different platforms
- 🌍 **Integrations** - Add support for new CMSs

### Getting Started with Development
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/Universal-LLMS.txt-Generator.git
cd Universal-LLMS.txt-Generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .

# Run tests
pytest

# Make your changes and test
python -m llms_txt_generator --test

# Submit a pull request
```

---

## 📄 License

This project is licensed under the MIT License 

---

