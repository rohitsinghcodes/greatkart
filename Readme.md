# 🛍️ GreatKart — Django E-Commerce Website

[![Stars](https://img.shields.io/github/stars/rohitsinghcodes/greatkart?style=social)](https://github.com/rohitsinghcodes/greatkart)

**GreatKart** is a **full‑stack Django e‑commerce application** for selling clothing and fashion items. It includes product categorization, shopping cart functionality, user authentication, and a dynamic store interface. :contentReference[oaicite:1]{index=1}

---

## 🚀 Features

✔ Product categories and listings  
✔ Search and browsing by category  
✔ Shopping cart with add/remove/increment functionality  
✔ User registration and login  
✔ User profile management  
✔ Dynamic store pages  
✔ Template‑based layout using Django’s templating engine  
✔ (Planned) Orders, order history, and admin dashboards

> ✨ Additional features like **orders, checkout, payment integration, invoice generation**, and **email notifications** are planned (you can add these and update this section).

---

## 🧠 Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Django (Python) |
| Frontend | Django Templates, HTML, CSS, JavaScript |
| Backend | Django, Django ORM |
| Database | SQLite (default) / PostgreSQL (optional) |
| Authentication | Django Auth |
| Cart | Session / DB‑based cart logic |
| Styling | CSS / Tailwind |

---

## 📁 Project Structure

```text
greatkart/
├── accounts/      # User authentication & profiles
├── carts/         # Shopping cart logic & session handling
├── category/      # Product category management
├── store/         # Product listings, details, & search
├── Orders/        # Checkout & order processing
├── greatkart/     # Core project configuration (settings/urls)
├── templates/     # Global HTML templates
├── static/        # CSS, JavaScript, and Image assets
├── manage.py      # Django management script
└── README.md
```

---

## 🛠️ Setup & Installation

Follow these steps to run GreatKart locally:

### 🔹 1. Clone the repository

```bash
git clone https://github.com/rohitsinghcodes/greatkart.git
cd greatkart


python -m venv env
# macOS / Linux
source env/bin/activate
# Windows
.\env\Scripts\activate
```
📦 Database Setup
```bash
# Apply migrations
python manage.py migrate

# Create a superuser (for admin access)
python manage.py createsuperuser
```
▶️ Running the App
```bash
python manage.py runserver
```

---

## 👤 Author

* **Rohit Singh** - [rohitsinghcodes](https://github.com/rohitsinghcodes)