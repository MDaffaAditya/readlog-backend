# 📚 ReadLog Backend API

ReadLog adalah **REST API berbasis Django** untuk **tracking, review, dan manajemen konten bacaan** seperti **komik dan novel**, mirip konsep **MyAnimeList / Letterboxd**, dengan sistem **role-based permission**, **JWT authentication**, dan **progress tracking**.

---

## 🚀 Tech Stack

* **Python**
* **Django**
* **Django REST Framework**
* **JWT Authentication (HttpOnly Cookie)**
* **dj-rest-auth & django-allauth**
* **drf-spectacular (Swagger & Redoc)**
* **django-environ**
* **django-cors-headers**

---

## 📦 Fitur Utama

### 🔐 Authentication & Authorization

* JWT Authentication berbasis **HttpOnly Cookie**
* Access token & refresh token
* Custom User Model (`member.User`)
* Role-based permission:

  * **Admin**: full CRUD
  * **User**: terbatas sesuai resource

### 📘 Content Management

* Comic
* Novel
* Genre
* Relasi genre ke konten

### ⭐ Review & Library

* Review dengan rating
* Tracking progress membaca
* User Library (koleksi pribadi)
* Validasi agar user **tidak bisa mengedit milik user lain**

### 📊 API Documentation

* Swagger UI
* Redoc
* OpenAPI Schema

---

## 🗂 Struktur Aplikasi

```text
backend/
├── member/        # Custom user & authentication
├── contents/      # Comic, Novel, Genre
├── reviews/       # Review & rating
├── library/       # User library & progress
├── interactions/ # Interaksi user (favorite, dsb)
├── backend/       # Core project settings
```

---

## ⚙️ Environment Variables

Project ini menggunakan **`.env` file** untuk konfigurasi environment.

Buat file `.env` di root project:

```env
# Core
DEBUG=
SECRET_KEY=
ALLOWED_HOSTS=

# Database
DATABASE_URL=

# Static & Media
STATIC_DIR=
MEDIA_DIR=

# API & Docs
IMAGE_VERSION=
SWAGGER_CONNECT_SOCKET=

# App Config
MAXIMUM_FILTER_DAYS=
```

> ⚠️ **Jangan pernah commit file `.env` ke repository publik**

---

## 🛠 Instalasi & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/username/readlog-backend.git
cd readlog-backend
```

### 2️⃣ Buat Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Setup Environment

Buat file `.env` dan isi sesuai konfigurasi kamu.

### 5️⃣ Migrasi Database

```bash
python manage.py migrate
```

### 6️⃣ Buat Superuser

```bash
python manage.py createsuperuser
```

### 7️⃣ Jalankan Server

```bash
python manage.py runserver
```

Server akan berjalan di:

```
http://127.0.0.1:8000
```

---

## 🔑 Authentication Detail

* **Auth Type**: JWT (Cookie-based)
* **Access Token Cookie**: `access`
* **Refresh Token Cookie**: `refresh`

### Token Lifetime

* Access Token: **24 jam**
* Refresh Token: **1 hari**

---

## 🧾 API Documentation

Setelah server berjalan:

* **Swagger UI**

  ```
  /api/schema/swagger-ui/
  ```

* **Redoc**

  ```
  /api/schema/redoc/
  ```

---

## 🛡 Permission Rules (Ringkasan)

| Resource              | User               | Admin     |
| --------------------- | ------------------ | --------- |
| Comic / Novel / Genre | Read only          | Full CRUD |
| Review                | CRUD milik sendiri | Full      |
| User Library          | CRUD milik sendiri | Full      |

---

## 🌐 CORS & Frontend Support

Frontend yang diizinkan:

* `http://localhost:3000`

Support untuk:

* Nuxt JS

---

## 📌 Catatan Penting

* Menggunakan **HttpOnly Cookie** → lebih aman dari XSS
* Siap untuk production dengan penyesuaian:

  * `DEBUG=False`
  * `SECURE_COOKIE=True`
  * Proper ALLOWED_HOSTS

---

## 📄 License

Project ini bersifat **open-source** dan bebas digunakan untuk pembelajaran dan pengembangan lebih lanjut.

---

## ✨ Author

**ReadLog Backend**
Dibangun menggunakan Django & Django REST Framework

