# SYANDE-Meryl

A comprehensive inventory and sales management system built with FastAPI, designed for retail businesses to manage products, sales, users, and operations efficiently.

## Features

### 🏪 Core Functionality
- **Point of Sale (POS)**: Streamlined sales interface for quick transactions
- **Inventory Management**: Complete product lifecycle management
- **User Management**: Role-based access control with customizable permissions
- **Sales Tracking**: Detailed sales analytics and reporting
- **Returns Management**: Handle customer returns and exchanges

### 📦 Inventory Management
- Product catalog with detailed specifications
- Brand and category organization
- Size and variant management
- Stock level monitoring
- Image upload and management

### 👥 User Management
- User registration and authentication
- Role-based permissions system
- Profile management with image uploads
- Session management

### 💰 Sales & Analytics
- Sales transaction recording
- Customer order tracking
- Returns processing
- Dashboard analytics

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Templates**: Jinja2
- **Email**: Resend API, Google APIs
- **Image Processing**: Pillow
- **Authentication**: Session-based with bcrypt

## Prerequisites

- Python 3.8+
- MySQL Server

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Terriakidesu/SYANDE-Meryl.git
   cd SYANDE-Meryl
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database:**
   - Create a MySQL database
   - Configure database connection in `secrets.env`

5. **Configure environment:**
   - Copy and update `secrets.env` with your configuration
   - Update `properties.json` if needed for custom paths

## Configuration

### Environment Variables
The application loads secrets from environment variables. Create a `.env` file (or `secrets.env` as specified in `properties.json`) with the following variables:

```env
# Database Configuration
DB_HOSTNAME=localhost
DB_DATABASE=your_database_name
DB_USERNAME=your_username
DB_PASSWORD=your_password

# Session Secret
SESSION_SECRET_KEY=your-secret-key-here

# Email Configuration (Resend)
RESEND_API_KEY=your-resend-api-key

# Gmail Configuration (for email sending)
GMAIL_CLIENT_ID=your-gmail-client-id
GMAIL_CLIENT_SECRET=your-gmail-client-secret
GMAIL_REFRESH_TOKEN=your-gmail-refresh-token
```

### Database Setup
The application connects to a MySQL database using the following connection URL format:
```
mysql://username:password@hostname/database_name
```

**Requirements:**
- MySQL Server 5.7+ or MariaDB 10.0+
- A database user with appropriate permissions
- The database must be created before running the application

**Note:** Database schema and migrations are not included in this repository. You will need to create the necessary tables and initial data manually based on the models in `src/models/`.

## Running the Application

1. **Start the development server:**
   ```bash
   python main.py
   ```

2. **Access the application:**
   - Open your browser and navigate to `http://localhost:8080`
   - Default login credentials (if set up): Check your database

## Project Structure

```
SYANDE-Meryl/
├── assets/
│   └── public/
│       ├── static/          # CSS, JS, images
│       ├── templates/       # HTML templates
│       │   ├── components/  # Reusable components
│       │   ├── manage/      # Management pages
│       │   ├── pos/         # Point of sale
│       │   ├── settings/    # Settings pages
│       │   └── exceptions/  # Error pages
│       ├── profiles/        # User profile images
│       └── products/        # Product images
├── src/
│   ├── routes/              # API and page routes
│   │   ├── api/            # REST API endpoints
│   │   ├── manage.py       # Management routes
│   │   ├── pos.py          # POS routes
│   │   └── settings.py     # Settings routes
│   ├── models/             # Database models
│   ├── helpers/            # Utility functions
│   ├── Settings/           # Configuration management
│   └── utils/              # Helper utilities
├── logs/                   # Application logs
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── properties.json         # Application configuration
├── secrets.env            # Environment secrets (not in repo)
└── README.md              # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/logout` - User logout
- `POST /api/auth/request_otp` - Request OTP for email verification
- `POST /api/auth/verify_otp` - Verify OTP
- `POST /api/auth/verify_email` - Verify email availability

### Inventory Management
- `GET /api/inventory/brands` - List brands with pagination and search
- `GET /api/inventory/brands/suggestions` - Get brand suggestions for autocomplete
- `POST /api/inventory/brands/add` - Add new brand
- `POST /api/inventory/brands/update` - Update brand
- `DELETE /api/inventory/brands/delete/{brand_id}` - Delete brand
- `GET /api/inventory/brands/{brand_id}` - Get specific brand
- `GET /api/inventory/categories` - List categories
- `GET /api/inventory/sizes` - List sizes
- `GET /api/inventory/shoes` - List shoes
- `GET /api/inventory/variants` - List variants

### User Management
- `GET /api/users` - List users
- `POST /api/users/add` - Add user
- `POST /api/users/update` - Update user

### Sales
- `GET /api/sales` - List sales
- `GET /api/sales/returns` - List returns

**Note:** This is not an exhaustive list. The API includes additional endpoints for CRUD operations on all inventory entities, user management, and sales processing.

## Development

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes

### Database Migrations
The application doesn't include automatic migrations. Database schema changes should be handled manually or through your preferred migration tool.

### Logging
Application logs are stored in the `logs/` directory with rotation based on file size.

### Static Files
- CSS and JS files are served from `assets/public/static/`
- Images are stored in `assets/public/` subdirectories
- Templates use Jinja2 syntax

## Deployment

1. **Production Environment:**
   - Set `debug: false` in `properties.json`
   - Use a production WSGI server (e.g., Gunicorn)
   - Configure proper SSL/TLS
   - Set secure session cookies

2. **Environment Variables:**
   - Ensure all secrets are properly configured
   - Use strong, random keys for sessions

3. **Database:**
   - Use connection pooling for production
   - Regular backups
   - Monitor performance


## Changelog

### Version 1.0.0
- Initial release
- Basic inventory management
- User authentication
- POS functionality
- Sales tracking
- Returns management
