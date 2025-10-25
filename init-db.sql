-- Script untuk inisialisasi database PostgreSQL
-- Database akan dibuat otomatis oleh docker-entrypoint

-- Buat extension jika diperlukan
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Selesai - Django akan membuat tabel melalui migrasi
