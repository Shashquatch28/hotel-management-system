# Hotel Management System (Django Project)

![HotelSystem Home Page](https://i.imgur.com/e0d63e.jpg)

This is a full-stack web application for a Hotel Management System, built with Python and the Django framework.

The primary challenge of this project was to integrate a modern web application with a **pre-existing, legacy MySQL database**. The project demonstrates a "bottom-up" development approach, where the application logic and Django models were built to conform to an existing database schema, rather than the other way around.

The final application features a complete "Midnight & Gold" dark theme, full user authentication, hotel browsing/search, and a comprehensive **CRUD** (Create, Read, Update, Delete) system for managing bookings, reviews, and user profiles.

## Key Features

* **Full User Authentication:** Secure user registration, login, logout, and password change functionality.
* **Custom User Model:** Uses the legacy `Customer` table for authentication, demonstrating a complete schema override and migration.
* **Hotel Browsing:** Search, filter, and browse all hotels, displayed in a responsive card grid.
* **Dynamic Hotel Details:** A two-column detail page showing hotel info, facilities, offers, and image galleries.
* **Complete Booking System (CRUD):**
    * **Create:** Book a room with full date validation (checks for past dates, invalid ranges, and double-bookings).
    * **Read:** View all active bookings on a dedicated "My Bookings" page.
    * **Update:** Edit the check-in/check-out dates of an existing booking.
    * **Delete:** Cancel an active booking.
* **Data Synchronization:** Automatically creates and updates `Payment` records in sync with booking actions (create, edit, cancel).
* **User Profile Management (CRUD):** Users can edit their profile info (name, location, DOB) and manage multiple phone numbers (create/delete).
* **Review System (CRUD):** Logged-in users can submit ratings (1-5) and comments for hotels, which are then displayed on the detail page.
* **Dynamic User Feedback:** Animated, auto-disappearing "flash" messages for success and error handling.
* **Full Admin Panel:** Uses the built-in Django admin to manage all 11 database tables.

## Tech Stack

* **Backend:** Python, Django
* **Database:** MySQL (connected via `mysqlclient`)
* **Frontend:** HTML5, CSS3 (with CSS Grid & Flexbox)
* **Core Libraries:** `dj-database-url`, `python-dotenv`

## 🚀 Local Setup & Installation

To run this project locally, you must have Python, Git, and a MySQL server installed.

### 1. Set Up the Database

Before running the application, you must set up the database in your local MySQL server.

1.  Create the database:
    ```sql
    CREATE DATABASE hotel_management_system;
    ```
2.  **Critically important:** You must run all the SQL scripts found in your project's documentation (`report.md` file) to first **create the tables** (`CREATE TABLE...`) and then **modify them** (`ALTER TABLE...`) to be compatible with Django's auth system.

### 2. Set Up the Project

1.  Clone the repository:
    ```bash
    git clone [https://github.com/Shashquatch28/hotel-management-system.git](https://github.com/Shashquatch28/hotel-management-system.git)
    cd hotel-management-system
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On Mac/Linux
    source venv/bin/activate
    ```
3.  Install all dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If you are running locally without deployment, you can remove `gunicorn` and `whitenoise` from `requirements.txt`)*

### 3. Configure Environment Variables

This project uses a `.env` file for local development to keep passwords secure.

1.  Create a file named `.env` in the root of the project (the same folder as `manage.py`).
2.  Add your database URL and a secret key to this file. (Replace `your_user` and `your_password` with your MySQL credentials).
    ```
    LOCAL_DATABASE_URL=mysql://your_user:your_password@127.0.0.1:3306/hotel_management_system
    SECRET_KEY=django-insecure-your-own-local-secret-key
    ```
    *(Alternatively, you can hardcode these values in `config/settings.py` as we discussed.)*

### 4. Run the Application

1.  Run the Django migrations (this creates Django's *internal* tables like `auth_group`):
    ```bash
    python manage.py migrate
    ```
2.  Create your admin superuser:
    ```bash
    python manage.py createsuperuser
    ```
3.  Start the development server:
    ```bash
    python manage.py runserver
    ```
4.  Open your browser and go to: **`http://127.0.0.1:8000/`**

## Usage

1.  Go to `http://127.0.0.1:8000/` to see the home page.
2.  Click "Register" to create a new customer account.
3.  Log in with your new account.
4.  Browse "All Hotels," search for a hotel, and click one to see details.
5.  Book a room, then check "My Bookings" to manage it.
6.  Go to "My Profile" to add a phone number or edit your details.

To access the staff backend, go to `http://127.0.0.1:8000/admin/` and log in with the superuser account you created.

## Author

* **Shashwat Kumar**
