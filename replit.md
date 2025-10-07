# Campus Entity Resolution & Security Monitoring System

## Overview

The Campus Entity Resolution & Security Monitoring System is a Django-based web application designed to unify and analyze campus data from multiple sources. The system provides entity resolution capabilities, timeline reconstruction, predictive analytics, and security monitoring for students, staff, and assets across a campus environment.

The application enables security personnel and administrators to:
- Search and resolve entities (students, staff, assets) with confidence scoring
- Reconstruct chronological timelines of campus activities
- Predict entity locations using AI-powered inference
- Monitor security alerts for inactive or suspicious entities

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack:**
- HTML templates with Django templating engine
- Tailwind CSS v4.1.14 for styling
- Vanilla JavaScript for client-side interactivity

**Design Pattern:**
- Template inheritance using a base template (`base.html`) for consistent layout
- Separate page templates for each major feature (search, timeline, predictions, alerts)
- Client-side data fetching via async/await fetch API
- Real-time UI updates with DOM manipulation

**Styling Approach:**
- Utility-first CSS with Tailwind
- Custom animations for gradient backgrounds
- Build process using Tailwind CLI to generate minified CSS
- Responsive design with mobile-first breakpoints

### Backend Architecture

**Framework:** Django 5.2.7

**Application Structure:**
- Monolithic Django project (`campus_monitor`)
- Single app (`dashboard`) containing all business logic
- Function-based views for page rendering and API endpoints
- RESTful API pattern for data endpoints (`/api/search/`, `/api/timeline/`, etc.)

**View Layer:**
- Separation of concerns: page views render templates, API views return JSON
- File-based data storage using JSON files in `dashboard/data/`
- No database models currently defined (models.py is empty)

**URL Routing:**
- Two-level routing: project-level URLs include app-level URLs
- Clean URL structure with dedicated paths for pages and API endpoints

### Data Storage Solutions

**Current Implementation:**
- JSON file-based storage in `dashboard/data/` directory
- Four data files: `entities.json`, `timeline.json`, `predictions.json`, `alerts.json`
- Data loaded synchronously from filesystem on each API request

**Database Configuration:**
- SQLite configured as default database (Django default)
- No models defined yet, indicating potential for migration to database-backed storage
- Database setup ready for future entity persistence and historical data tracking

**Data Model Concepts** (from JSON structure):
- **Entities:** name, type (Student/Staff/Asset), source, timestamp, confidence score
- **Timeline Events:** time, event description, icon representation
- **Predictions:** entity, predicted_location, confidence, explanation
- **Alerts:** entity, type, last_seen timestamp, status

### Authentication and Authorization

**Current State:**
- Django authentication middleware enabled in settings
- Django admin interface available at `/admin/`
- No custom authentication implemented
- No access control on pages or API endpoints (all publicly accessible)

**Security Considerations:**
- DEBUG mode enabled (development setting)
- ALLOWED_HOSTS set to wildcard `['*']` (not production-safe)
- Secret key exposed in settings file (should be environment variable)
- CSRF protection enabled via middleware

### External Dependencies

**Python Dependencies:**
- Django 5.2.7 (web framework)
- Python standard library (json, os modules for file operations)

**JavaScript Dependencies:**
- @tailwindcss/cli v4.1.14 (development dependency)
- tailwindcss v4.1.14 (development dependency)

**Build Tools:**
- npm scripts for CSS compilation (`build:css`, `watch:css`)
- Tailwind CLI for processing input.css to static output

**Third-Party Services:**
- None currently integrated
- System designed for potential integration with:
  - Wi-Fi access point logs
  - Card access systems
  - Library management systems
  - Device tracking systems
  - CCTV or security camera feeds

**Static Assets:**
- CSS served from `campus_monitor/dashboard/static/dashboard/styles.css`
- JavaScript utilities in `script.js` (timestamp formatting, confidence scoring)
- Icons referenced via emoji characters in HTML

**Deployment Configuration:**
- WSGI application configured for traditional deployment
- ASGI application configured for async deployment options
- Static files configuration using Django's staticfiles app