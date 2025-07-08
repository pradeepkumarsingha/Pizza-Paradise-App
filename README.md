# 🍕 Pizza Paradise App

**Pizza Paradise** is a web-based pizza ordering system built with **Django** and styled using **Bootstrap**. The app allows users to browse featured pizzas, view details and prices, and place orders through a clean, responsive interface. It’s a perfect learning project for beginners exploring Django web development and template-based UI design.

---

## 📌 Features

- 🔍 Browse featured pizzas with images, names, and prices
- 📋 View pizza descriptions (with truncation for UI clarity)
- 🛒 Add to cart functionality using dynamic URLs
- 🧭 User-friendly navigation (Order Now, Menu)
- 💻 Responsive layout using Bootstrap and Font Awesome
- 🧩 Modular structure with Django templates

---

## 🚀 Technologies Used

- **Backend**: Python, Django
- **Frontend**: HTML5, CSS3, Bootstrap, Font Awesome
- **Database**: SQLite (default Django DB)
- **Templating**: Django Templating Engine

---

## 🗂️ Project Structure

pizza-paradise/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── templates/
│ └── home.html
├── static/
│ └── css, js, images...
├── pizza/ # Django app
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│ └── templates/
│ └── pizza/
└── pizza_paradise/ # Project config
├── settings.py
└── urls.py

---

## ⚙️ How to Run Locally

1. **Clone the repository**
```bash
git clone https://github.com/pradeepkumarsingha/Pizza-Paradise-App.git
cd Pizza-Paradise-App
python -m venv env
env\Scripts\activate   # On Windows
# or
source env/bin/activate   # On Mac/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
http://127.0.0.1:8000/
## 📷 Screenshots

### 🔸 Home Page (Hero Section + CTA)
![Home Page](screenshots/homepage.png)

### 🔸 Featured Pizzas Section
![Featured Pizzas](screenshots/featured_pizzas.png)

### 🔸 Why Choose Us Section
![Why Choose Us](screenshots/why_choose_us.png)
## 👨‍💻 Developer

**Pradeep Kumar Singha**  
🔗 [GitHub Profile](https://github.com/pradeepkumarsingha)  
✉️ [mr.pradeepkumarsingha@gmail.com](mailto:mr.pradeepkumarsingha@gmail.com)
