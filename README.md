# 🛒 Sistem E-Commerce Terdistribusi

Sebuah sistem e-commerce yang dirancang untuk demonstrasi integrasi basis data terdistribusi menggunakan **FastAPI**, **PostgreSQL Citus**, **MongoDB**, dan **Redis**. Proyek ini mensimulasikan manajemen produk, checkout, dan penyimpanan metadata produk dalam skenario skala nyata.

---

## 🔧 Teknologi yang Digunakan

| Komponen               | Fungsi                                |
| ---------------------- | ------------------------------------- |
| **FastAPI**            | Backend utama (CRUD, checkout)        |
| **PostgreSQL + Citus** | Data utama produk & orders (sharding) |
| **MongoDB**            | Metadata produk (deskripsi, gambar)   |
| **Redis**              | Manajemen stok real-time & sesi login |
| **Jinja2**             | Template HTML responsif               |
| **Docker Compose**     | Orkestrasi semua service              |

---

## 🧩 Fitur Utama

- ✅ Daftar produk dari database terdistribusi
- ✏️ Tambah, edit, hapus produk (admin)
- 🛒 Checkout dengan pengurangan stok real-time
- 🔐 Login sederhana (tanpa hashing kompleks)
- 🔄 Integrasi antar database dalam satu endpoint
- 🧪 Simulasi arsitektur data terdistribusi

---

---

## 🚀 Cara Menjalankan

```bash
[text] (git clone https://github.com/username/ecommerce_distributed_system.git)
cd ecommerce_distributed_system
docker-compose up --build

[text](http://localhost:8001)
```
