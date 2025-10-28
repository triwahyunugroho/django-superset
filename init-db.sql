-- Create separate database for Django
CREATE DATABASE django_db;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE superset TO superset;
GRANT ALL PRIVILEGES ON DATABASE django_db TO superset;

-- Connect to superset database to create tables and populate data
\c superset;

-- =====================================================
-- TABLES FOR GOVERNMENT BUDGET DATA
-- =====================================================

-- Table: OPD (Organisasi Perangkat Daerah / Government Agencies)
CREATE TABLE IF NOT EXISTS opd (
    id SERIAL PRIMARY KEY,
    kode_opd VARCHAR(20) UNIQUE NOT NULL,
    nama_opd VARCHAR(255) NOT NULL,
    kepala_opd VARCHAR(100),
    alamat TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Program
CREATE TABLE IF NOT EXISTS program (
    id SERIAL PRIMARY KEY,
    opd_id INTEGER REFERENCES opd(id),
    kode_program VARCHAR(50) UNIQUE NOT NULL,
    nama_program VARCHAR(255) NOT NULL,
    deskripsi TEXT,
    tahun_mulai INTEGER,
    tahun_selesai INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Kegiatan (Activities under Program)
CREATE TABLE IF NOT EXISTS kegiatan (
    id SERIAL PRIMARY KEY,
    program_id INTEGER REFERENCES program(id),
    kode_kegiatan VARCHAR(50) UNIQUE NOT NULL,
    nama_kegiatan VARCHAR(255) NOT NULL,
    deskripsi TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Kategori Belanja
CREATE TABLE IF NOT EXISTS kategori_belanja (
    id SERIAL PRIMARY KEY,
    kode_kategori VARCHAR(20) UNIQUE NOT NULL,
    nama_kategori VARCHAR(100) NOT NULL,
    jenis VARCHAR(50) -- Operasi, Modal, Transfer, dll
);

-- Table: Rencana Anggaran
CREATE TABLE IF NOT EXISTS rencana_anggaran (
    id SERIAL PRIMARY KEY,
    kegiatan_id INTEGER REFERENCES kegiatan(id),
    kategori_belanja_id INTEGER REFERENCES kategori_belanja(id),
    tahun INTEGER NOT NULL,
    triwulan INTEGER CHECK (triwulan BETWEEN 1 AND 4),
    bulan INTEGER CHECK (bulan BETWEEN 1 AND 12),
    nilai_anggaran DECIMAL(18, 2) NOT NULL,
    sumber_dana VARCHAR(100), -- APBD, DAK, DAU, dll
    keterangan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Realisasi Anggaran
CREATE TABLE IF NOT EXISTS realisasi_anggaran (
    id SERIAL PRIMARY KEY,
    rencana_anggaran_id INTEGER REFERENCES rencana_anggaran(id),
    kegiatan_id INTEGER REFERENCES kegiatan(id),
    kategori_belanja_id INTEGER REFERENCES kategori_belanja(id),
    tahun INTEGER NOT NULL,
    triwulan INTEGER CHECK (triwulan BETWEEN 1 AND 4),
    bulan INTEGER CHECK (bulan BETWEEN 1 AND 12),
    tanggal_realisasi DATE,
    nilai_realisasi DECIMAL(18, 2) NOT NULL,
    nilai_sisa DECIMAL(18, 2),
    persentase_realisasi DECIMAL(5, 2),
    keterangan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- POPULATE DUMMY DATA
-- =====================================================

-- Insert OPD (Government Agencies)
INSERT INTO opd (kode_opd, nama_opd, kepala_opd, alamat) VALUES
('OPD-001', 'Dinas Pendidikan', 'Dr. Ahmad Suryanto, M.Pd', 'Jl. Pendidikan No. 1'),
('OPD-002', 'Dinas Kesehatan', 'dr. Siti Nurhaliza, Sp.PK', 'Jl. Kesehatan No. 5'),
('OPD-003', 'Dinas Pekerjaan Umum dan Penataan Ruang', 'Ir. Budi Santoso, M.T', 'Jl. Pembangunan No. 10'),
('OPD-004', 'Dinas Sosial', 'Dra. Ratna Sari, M.Si', 'Jl. Sosial No. 3'),
('OPD-005', 'Dinas Pertanian dan Pangan', 'Ir. Hadi Wijaya, M.P', 'Jl. Pertanian No. 7'),
('OPD-006', 'Dinas Perhubungan', 'Drs. Eko Prasetyo, M.T', 'Jl. Lalu Lintas No. 15'),
('OPD-007', 'Dinas Pariwisata dan Kebudayaan', 'Dra. Maya Kusuma, M.M', 'Jl. Wisata No. 20'),
('OPD-008', 'Badan Pengelolaan Keuangan dan Aset Daerah', 'Drs. Bambang Hartono, M.Ak', 'Jl. Keuangan No. 2');

-- Insert Programs
INSERT INTO program (opd_id, kode_program, nama_program, deskripsi, tahun_mulai, tahun_selesai) VALUES
-- Dinas Pendidikan
(1, 'PROG-001', 'Program Peningkatan Kualitas Pendidikan Dasar', 'Peningkatan mutu pendidikan SD dan SMP', 2024, 2026),
(1, 'PROG-002', 'Program Pembangunan dan Rehabilitasi Sekolah', 'Pembangunan dan renovasi gedung sekolah', 2024, 2025),
(1, 'PROG-003', 'Program Beasiswa Pendidikan', 'Pemberian beasiswa untuk siswa kurang mampu', 2024, 2024),

-- Dinas Kesehatan
(2, 'PROG-004', 'Program Peningkatan Pelayanan Kesehatan', 'Peningkatan kualitas layanan puskesmas', 2024, 2026),
(2, 'PROG-005', 'Program Imunisasi dan Gizi', 'Program imunisasi dan perbaikan gizi masyarakat', 2024, 2024),
(2, 'PROG-006', 'Program Pembangunan Fasilitas Kesehatan', 'Pembangunan puskesmas dan posyandu', 2024, 2025),

-- Dinas PU
(3, 'PROG-007', 'Program Pembangunan Jalan dan Jembatan', 'Pembangunan infrastruktur jalan kabupaten', 2024, 2026),
(3, 'PROG-008', 'Program Penataan Ruang Kota', 'Penataan dan revitalisasi ruang publik', 2024, 2025),

-- Dinas Sosial
(4, 'PROG-009', 'Program Bantuan Sosial', 'Bantuan untuk masyarakat kurang mampu', 2024, 2024),
(4, 'PROG-010', 'Program Pemberdayaan UMKM', 'Pemberdayaan usaha mikro kecil menengah', 2024, 2025),

-- Dinas Pertanian
(5, 'PROG-011', 'Program Peningkatan Produksi Pertanian', 'Peningkatan hasil panen dan produktivitas', 2024, 2025),
(5, 'PROG-012', 'Program Ketahanan Pangan', 'Menjaga stabilitas harga dan ketersediaan pangan', 2024, 2024);

-- Insert Kegiatan (Activities)
INSERT INTO kegiatan (program_id, kode_kegiatan, nama_kegiatan, deskripsi) VALUES
-- Program Pendidikan Dasar
(1, 'KEG-001', 'Pelatihan Guru SD dan SMP', 'Pelatihan peningkatan kompetensi guru'),
(1, 'KEG-002', 'Pengadaan Buku dan Alat Peraga', 'Pengadaan buku pelajaran dan alat peraga'),
(1, 'KEG-003', 'Supervisi dan Monitoring Sekolah', 'Monitoring kualitas pembelajaran'),

-- Program Pembangunan Sekolah
(2, 'KEG-004', 'Pembangunan Ruang Kelas Baru', 'Pembangunan 20 ruang kelas baru'),
(2, 'KEG-005', 'Rehabilitasi Gedung Sekolah', 'Renovasi 15 gedung sekolah rusak'),

-- Program Beasiswa
(3, 'KEG-006', 'Beasiswa Siswa Miskin', 'Beasiswa untuk 500 siswa kurang mampu'),

-- Program Pelayanan Kesehatan
(4, 'KEG-007', 'Peningkatan Pelayanan Puskesmas', 'Upgrade fasilitas dan SDM puskesmas'),
(4, 'KEG-008', 'Pengadaan Obat dan Alat Kesehatan', 'Pengadaan obat-obatan esensial'),

-- Program Imunisasi
(5, 'KEG-009', 'Imunisasi Dasar Lengkap', 'Program imunisasi untuk balita'),
(5, 'KEG-010', 'Program Gizi Buruk', 'Penanganan kasus gizi buruk'),

-- Program Pembangunan Kesehatan
(6, 'KEG-011', 'Pembangunan Puskesmas Baru', 'Pembangunan 2 puskesmas baru'),
(6, 'KEG-012', 'Renovasi Posyandu', 'Renovasi 30 posyandu'),

-- Program Jalan dan Jembatan
(7, 'KEG-013', 'Pembangunan Jalan Aspal', 'Pengaspalan 50 km jalan kabupaten'),
(7, 'KEG-014', 'Pembangunan Jembatan', 'Pembangunan 5 jembatan baru'),
(7, 'KEG-015', 'Pemeliharaan Jalan', 'Pemeliharaan rutin jalan kabupaten'),

-- Program Penataan Ruang
(8, 'KEG-016', 'Revitalisasi Taman Kota', 'Penataan 10 taman kota'),
(8, 'KEG-017', 'Pembangunan RTH', 'Pembangunan ruang terbuka hijau'),

-- Program Bantuan Sosial
(9, 'KEG-018', 'Bantuan Langsung Tunai', 'BLT untuk 2000 KK'),
(9, 'KEG-019', 'Bantuan Sembako', 'Bantuan sembako untuk warga miskin'),

-- Program UMKM
(10, 'KEG-020', 'Pelatihan Kewirausahaan', 'Pelatihan untuk pelaku UMKM'),
(10, 'KEG-021', 'Bantuan Modal UMKM', 'Bantuan modal usaha'),

-- Program Pertanian
(11, 'KEG-022', 'Bantuan Bibit dan Pupuk', 'Bantuan sarana produksi pertanian'),
(11, 'KEG-023', 'Alsintan untuk Petani', 'Bantuan alat dan mesin pertanian'),

-- Program Ketahanan Pangan
(12, 'KEG-024', 'Operasi Pasar Murah', 'Stabilisasi harga bahan pokok'),
(12, 'KEG-025', 'Cadangan Beras Daerah', 'Pengadaan cadangan beras');

-- Insert Kategori Belanja
INSERT INTO kategori_belanja (kode_kategori, nama_kategori, jenis) VALUES
('BL-51', 'Belanja Pegawai', 'Operasi'),
('BL-52', 'Belanja Barang dan Jasa', 'Operasi'),
('BL-53', 'Belanja Modal', 'Modal'),
('BL-54', 'Belanja Bantuan Sosial', 'Transfer'),
('BL-55', 'Belanja Hibah', 'Transfer'),
('BL-56', 'Belanja Perjalanan Dinas', 'Operasi'),
('BL-57', 'Belanja Pemeliharaan', 'Operasi');

-- Insert Rencana Anggaran (Budget Plan for 2024)
-- Tahun 2024 - Triwulan 1-4, Bulan 1-12
INSERT INTO rencana_anggaran (kegiatan_id, kategori_belanja_id, tahun, triwulan, bulan, nilai_anggaran, sumber_dana, keterangan) VALUES
-- KEG-001: Pelatihan Guru (Q1-Q4)
(1, 2, 2024, 1, 1, 150000000, 'APBD', 'Pelatihan Batch 1'),
(1, 2, 2024, 2, 4, 150000000, 'APBD', 'Pelatihan Batch 2'),
(1, 2, 2024, 3, 7, 150000000, 'APBD', 'Pelatihan Batch 3'),
(1, 2, 2024, 4, 10, 150000000, 'APBD', 'Pelatihan Batch 4'),

-- KEG-002: Pengadaan Buku
(2, 3, 2024, 1, 2, 500000000, 'APBD', 'Pengadaan buku semester 1'),
(2, 3, 2024, 3, 7, 500000000, 'APBD', 'Pengadaan buku semester 2'),

-- KEG-003: Supervisi Sekolah
(3, 2, 2024, 1, 1, 50000000, 'APBD', 'Supervisi Triwulan 1'),
(3, 2, 2024, 2, 4, 50000000, 'APBD', 'Supervisi Triwulan 2'),
(3, 2, 2024, 3, 7, 50000000, 'APBD', 'Supervisi Triwulan 3'),
(3, 2, 2024, 4, 10, 50000000, 'APBD', 'Supervisi Triwulan 4'),

-- KEG-004: Pembangunan Ruang Kelas (Q1-Q4)
(4, 3, 2024, 1, 1, 2000000000, 'DAK', 'Pembangunan fase 1'),
(4, 3, 2024, 2, 4, 2500000000, 'DAK', 'Pembangunan fase 2'),
(4, 3, 2024, 3, 7, 2500000000, 'DAK', 'Pembangunan fase 3'),
(4, 3, 2024, 4, 10, 2000000000, 'DAK', 'Finishing'),

-- KEG-005: Rehabilitasi Gedung
(5, 3, 2024, 1, 2, 800000000, 'APBD', 'Rehabilitasi batch 1'),
(5, 3, 2024, 3, 8, 800000000, 'APBD', 'Rehabilitasi batch 2'),

-- KEG-006: Beasiswa (setiap bulan)
(6, 4, 2024, 1, 1, 100000000, 'APBD', 'Beasiswa Januari'),
(6, 4, 2024, 1, 2, 100000000, 'APBD', 'Beasiswa Februari'),
(6, 4, 2024, 1, 3, 100000000, 'APBD', 'Beasiswa Maret'),
(6, 4, 2024, 2, 4, 100000000, 'APBD', 'Beasiswa April'),
(6, 4, 2024, 2, 5, 100000000, 'APBD', 'Beasiswa Mei'),
(6, 4, 2024, 2, 6, 100000000, 'APBD', 'Beasiswa Juni'),
(6, 4, 2024, 3, 7, 100000000, 'APBD', 'Beasiswa Juli'),
(6, 4, 2024, 3, 8, 100000000, 'APBD', 'Beasiswa Agustus'),
(6, 4, 2024, 3, 9, 100000000, 'APBD', 'Beasiswa September'),
(6, 4, 2024, 4, 10, 100000000, 'APBD', 'Beasiswa Oktober'),
(6, 4, 2024, 4, 11, 100000000, 'APBD', 'Beasiswa November'),
(6, 4, 2024, 4, 12, 100000000, 'APBD', 'Beasiswa Desember'),

-- KEG-007: Pelayanan Puskesmas
(7, 2, 2024, 1, 1, 300000000, 'APBD', 'Operasional Q1'),
(7, 2, 2024, 2, 4, 300000000, 'APBD', 'Operasional Q2'),
(7, 2, 2024, 3, 7, 300000000, 'APBD', 'Operasional Q3'),
(7, 2, 2024, 4, 10, 300000000, 'APBD', 'Operasional Q4'),

-- KEG-008: Pengadaan Obat
(8, 2, 2024, 1, 2, 400000000, 'DAU', 'Pengadaan obat Q1'),
(8, 2, 2024, 2, 5, 400000000, 'DAU', 'Pengadaan obat Q2'),
(8, 2, 2024, 3, 8, 400000000, 'DAU', 'Pengadaan obat Q3'),
(8, 2, 2024, 4, 11, 400000000, 'DAU', 'Pengadaan obat Q4'),

-- KEG-009: Imunisasi
(9, 2, 2024, 1, 1, 200000000, 'APBD', 'Imunisasi Q1'),
(9, 2, 2024, 2, 4, 200000000, 'APBD', 'Imunisasi Q2'),
(9, 2, 2024, 3, 7, 200000000, 'APBD', 'Imunisasi Q3'),
(9, 2, 2024, 4, 10, 200000000, 'APBD', 'Imunisasi Q4'),

-- KEG-010: Program Gizi
(10, 4, 2024, 1, 1, 150000000, 'APBD', 'Program gizi Q1'),
(10, 4, 2024, 2, 4, 150000000, 'APBD', 'Program gizi Q2'),
(10, 4, 2024, 3, 7, 150000000, 'APBD', 'Program gizi Q3'),
(10, 4, 2024, 4, 10, 150000000, 'APBD', 'Program gizi Q4'),

-- KEG-011: Pembangunan Puskesmas
(11, 3, 2024, 1, 2, 3000000000, 'DAK', 'Pembangunan puskesmas 1'),
(11, 3, 2024, 3, 7, 3000000000, 'DAK', 'Pembangunan puskesmas 2'),

-- KEG-012: Renovasi Posyandu
(12, 3, 2024, 1, 3, 300000000, 'APBD', 'Renovasi batch 1'),
(12, 3, 2024, 3, 9, 300000000, 'APBD', 'Renovasi batch 2'),

-- KEG-013: Pembangunan Jalan (continuous)
(13, 3, 2024, 1, 1, 5000000000, 'DAK', 'Pengaspalan segment 1'),
(13, 3, 2024, 2, 4, 7000000000, 'DAK', 'Pengaspalan segment 2'),
(13, 3, 2024, 3, 7, 7000000000, 'DAK', 'Pengaspalan segment 3'),
(13, 3, 2024, 4, 10, 5000000000, 'DAK', 'Pengaspalan segment 4'),

-- KEG-014: Pembangunan Jembatan
(14, 3, 2024, 1, 2, 4000000000, 'DAK', 'Jembatan 1 dan 2'),
(14, 3, 2024, 3, 8, 4000000000, 'DAK', 'Jembatan 3, 4, dan 5'),

-- KEG-015: Pemeliharaan Jalan
(15, 7, 2024, 1, 1, 500000000, 'APBD', 'Pemeliharaan Q1'),
(15, 7, 2024, 2, 4, 500000000, 'APBD', 'Pemeliharaan Q2'),
(15, 7, 2024, 3, 7, 500000000, 'APBD', 'Pemeliharaan Q3'),
(15, 7, 2024, 4, 10, 500000000, 'APBD', 'Pemeliharaan Q4'),

-- KEG-016: Revitalisasi Taman
(16, 3, 2024, 1, 3, 1000000000, 'APBD', 'Revitalisasi taman batch 1'),
(16, 3, 2024, 3, 9, 1000000000, 'APBD', 'Revitalisasi taman batch 2'),

-- KEG-017: Pembangunan RTH
(17, 3, 2024, 2, 4, 1500000000, 'APBD', 'Pembangunan RTH fase 1'),
(17, 3, 2024, 4, 10, 1500000000, 'APBD', 'Pembangunan RTH fase 2'),

-- KEG-018: BLT
(18, 4, 2024, 1, 1, 600000000, 'APBD', 'BLT batch 1'),
(18, 4, 2024, 2, 4, 600000000, 'APBD', 'BLT batch 2'),
(18, 4, 2024, 3, 7, 600000000, 'APBD', 'BLT batch 3'),
(18, 4, 2024, 4, 10, 600000000, 'APBD', 'BLT batch 4'),

-- KEG-019: Bantuan Sembako
(19, 4, 2024, 1, 2, 400000000, 'APBD', 'Sembako Q1'),
(19, 4, 2024, 3, 8, 400000000, 'APBD', 'Sembako Q3'),

-- KEG-020: Pelatihan UMKM
(20, 2, 2024, 1, 2, 200000000, 'APBD', 'Pelatihan batch 1'),
(20, 2, 2024, 3, 8, 200000000, 'APBD', 'Pelatihan batch 2'),

-- KEG-021: Bantuan Modal UMKM
(21, 5, 2024, 1, 3, 1000000000, 'APBD', 'Bantuan modal tahap 1'),
(21, 5, 2024, 3, 9, 1000000000, 'APBD', 'Bantuan modal tahap 2'),

-- KEG-022: Bantuan Bibit Pupuk
(22, 2, 2024, 1, 1, 800000000, 'APBD', 'Masa tanam 1'),
(22, 2, 2024, 3, 7, 800000000, 'APBD', 'Masa tanam 2'),

-- KEG-023: Alsintan
(23, 3, 2024, 1, 2, 2000000000, 'APBD', 'Pengadaan alsintan batch 1'),
(23, 3, 2024, 3, 8, 2000000000, 'APBD', 'Pengadaan alsintan batch 2'),

-- KEG-024: Operasi Pasar
(24, 2, 2024, 1, 1, 300000000, 'APBD', 'Op pasar Q1'),
(24, 2, 2024, 2, 4, 300000000, 'APBD', 'Op pasar Q2'),
(24, 2, 2024, 3, 7, 300000000, 'APBD', 'Op pasar Q3'),
(24, 2, 2024, 4, 10, 300000000, 'APBD', 'Op pasar Q4'),

-- KEG-025: Cadangan Beras
(25, 2, 2024, 1, 3, 500000000, 'APBD', 'Pengadaan cadangan beras Q1'),
(25, 2, 2024, 3, 9, 500000000, 'APBD', 'Pengadaan cadangan beras Q3');

-- Insert Realisasi Anggaran (Budget Realization - with varying percentages)
-- Realizing budgets with realistic scenarios (some fully realized, some partial, some delayed)
INSERT INTO realisasi_anggaran (rencana_anggaran_id, kegiatan_id, kategori_belanja_id, tahun, triwulan, bulan, tanggal_realisasi, nilai_realisasi, nilai_sisa, persentase_realisasi, keterangan) VALUES
-- KEG-001: Pelatihan Guru - Q1 fully realized
(1, 1, 2, 2024, 1, 1, '2024-01-25', 148000000, 2000000, 98.67, 'Pelatihan selesai dengan baik'),
(2, 1, 2, 2024, 2, 4, '2024-04-20', 145000000, 5000000, 96.67, 'Beberapa peserta tidak hadir'),
(3, 1, 2, 2024, 3, 7, '2024-07-15', 150000000, 0, 100.00, 'Target tercapai'),
(4, 1, 2, 2024, 4, 10, '2024-10-18', 140000000, 10000000, 93.33, 'Sedang berlangsung'),

-- KEG-002: Pengadaan Buku - Q1 full, Q3 partial
(5, 2, 3, 2024, 1, 2, '2024-02-28', 500000000, 0, 100.00, 'Buku terdistribusi ke semua sekolah'),
(6, 2, 3, 2024, 3, 7, '2024-07-30', 450000000, 50000000, 90.00, 'Pengadaan dalam proses'),

-- KEG-003: Supervisi - All quarters
(7, 3, 2, 2024, 1, 1, '2024-01-31', 50000000, 0, 100.00, 'Supervisi selesai'),
(8, 3, 2, 2024, 2, 4, '2024-04-30', 48000000, 2000000, 96.00, 'Supervisi selesai'),
(9, 3, 2, 2024, 3, 7, '2024-07-31', 50000000, 0, 100.00, 'Supervisi selesai'),
(10, 3, 2, 2024, 4, 10, '2024-10-25', 45000000, 5000000, 90.00, 'Sedang berjalan'),

-- KEG-004: Pembangunan Ruang Kelas - Slow progress (infrastructure delay)
(11, 4, 3, 2024, 1, 1, '2024-01-30', 1800000000, 200000000, 90.00, 'Pengadaan material'),
(12, 4, 3, 2024, 2, 4, '2024-04-28', 2200000000, 300000000, 88.00, 'Pembangunan terhambat cuaca'),
(13, 4, 3, 2024, 3, 7, '2024-07-29', 2300000000, 200000000, 92.00, 'Progress catching up'),
(14, 4, 3, 2024, 4, 10, '2024-10-20', 1500000000, 500000000, 75.00, 'Finishing tertunda'),

-- KEG-005: Rehabilitasi Gedung
(15, 5, 3, 2024, 1, 2, '2024-02-29', 780000000, 20000000, 97.50, 'Rehabilitasi selesai'),
(16, 5, 3, 2024, 3, 8, '2024-08-25', 750000000, 50000000, 93.75, 'Sedang dalam pengerjaan'),

-- KEG-006: Beasiswa - Monthly payments (all realized)
(17, 6, 4, 2024, 1, 1, '2024-01-10', 100000000, 0, 100.00, 'Transfer ke rekening siswa'),
(18, 6, 4, 2024, 1, 2, '2024-02-10', 100000000, 0, 100.00, 'Transfer ke rekening siswa'),
(19, 6, 4, 2024, 1, 3, '2024-03-10', 100000000, 0, 100.00, 'Transfer ke rekening siswa'),
(20, 6, 4, 2024, 2, 4, '2024-04-10', 100000000, 0, 100.00, 'Transfer ke rekening siswa'),
(21, 6, 4, 2024, 2, 5, '2024-05-10', 100000000, 0, 100.00, 'Transfer ke rekening siswa'),
(22, 6, 4, 2024, 2, 6, '2024-06-10', 100000000, 0, 100.00, 'Transfer ke rekening siswa'),
(23, 6, 4, 2024, 3, 7, '2024-07-10', 100000000, 0, 100.00, 'Transfer ke rekening siswa'),
(24, 6, 4, 2024, 3, 8, '2024-08-10', 100000000, 0, 100.00, 'Transfer ke rekening siswa'),
(25, 6, 4, 2024, 3, 9, '2024-09-10', 100000000, 0, 100.00, 'Transfer ke rekening siswa'),
(26, 6, 4, 2024, 4, 10, '2024-10-10', 100000000, 0, 100.00, 'Transfer ke rekening siswa'),

-- KEG-007: Pelayanan Puskesmas
(29, 7, 2, 2024, 1, 1, '2024-01-31', 295000000, 5000000, 98.33, 'Operasional lancar'),
(30, 7, 2, 2024, 2, 4, '2024-04-30', 300000000, 0, 100.00, 'Operasional lancar'),
(31, 7, 2, 2024, 3, 7, '2024-07-31', 298000000, 2000000, 99.33, 'Operasional lancar'),
(32, 7, 2, 2024, 4, 10, '2024-10-25', 280000000, 20000000, 93.33, 'Sedang berjalan'),

-- KEG-008: Pengadaan Obat
(33, 8, 2, 2024, 1, 2, '2024-02-25', 400000000, 0, 100.00, 'Obat terdistribusi'),
(34, 8, 2, 2024, 2, 5, '2024-05-28', 390000000, 10000000, 97.50, 'Pengadaan selesai'),
(35, 8, 2, 2024, 3, 8, '2024-08-30', 395000000, 5000000, 98.75, 'Pengadaan selesai'),
(36, 8, 2, 2024, 4, 11, '2024-10-28', 350000000, 50000000, 87.50, 'Proses pengadaan'),

-- KEG-009: Imunisasi
(37, 9, 2, 2024, 1, 1, '2024-01-31', 200000000, 0, 100.00, 'Target cakupan tercapai'),
(38, 9, 2, 2024, 2, 4, '2024-04-30', 195000000, 5000000, 97.50, 'Cakupan baik'),
(39, 9, 2, 2024, 3, 7, '2024-07-31', 198000000, 2000000, 99.00, 'Cakupan baik'),
(40, 9, 2, 2024, 4, 10, '2024-10-20', 180000000, 20000000, 90.00, 'Sedang berjalan'),

-- KEG-010: Program Gizi
(41, 10, 4, 2024, 1, 1, '2024-01-31', 148000000, 2000000, 98.67, 'Program berjalan baik'),
(42, 10, 4, 2024, 2, 4, '2024-04-30', 150000000, 0, 100.00, 'Target tercapai'),
(43, 10, 4, 2024, 3, 7, '2024-07-31', 145000000, 5000000, 96.67, 'Program berjalan'),
(44, 10, 4, 2024, 4, 10, '2024-10-22', 140000000, 10000000, 93.33, 'Sedang berjalan'),

-- KEG-011: Pembangunan Puskesmas - Major project with delays
(45, 11, 3, 2024, 1, 2, '2024-02-29', 2500000000, 500000000, 83.33, 'Proses lelang dan pembebasan lahan'),
(46, 11, 3, 2024, 3, 7, '2024-07-30', 2700000000, 300000000, 90.00, 'Konstruksi berjalan'),

-- KEG-012: Renovasi Posyandu
(47, 12, 3, 2024, 1, 3, '2024-03-28', 290000000, 10000000, 96.67, 'Renovasi selesai'),
(48, 12, 3, 2024, 3, 9, '2024-09-25', 280000000, 20000000, 93.33, 'Sedang pengerjaan'),

-- KEG-013: Pembangunan Jalan - Large infrastructure
(49, 13, 3, 2024, 1, 1, '2024-01-31', 4800000000, 200000000, 96.00, 'Pengaspalan segment 1'),
(50, 13, 3, 2024, 2, 4, '2024-04-30', 6500000000, 500000000, 92.86, 'Pengaspalan segment 2'),
(51, 13, 3, 2024, 3, 7, '2024-07-30', 6800000000, 200000000, 97.14, 'Pengaspalan segment 3'),
(52, 13, 3, 2024, 4, 10, '2024-10-25', 4500000000, 500000000, 90.00, 'Sedang pengerjaan'),

-- KEG-014: Pembangunan Jembatan
(53, 14, 3, 2024, 1, 2, '2024-02-28', 3800000000, 200000000, 95.00, 'Jembatan 1 dan 2 selesai'),
(54, 14, 3, 2024, 3, 8, '2024-08-30', 3600000000, 400000000, 90.00, 'Jembatan 3,4,5 dalam progress'),

-- KEG-015: Pemeliharaan Jalan
(55, 15, 7, 2024, 1, 1, '2024-01-31', 495000000, 5000000, 99.00, 'Pemeliharaan rutin'),
(56, 15, 7, 2024, 2, 4, '2024-04-30', 500000000, 0, 100.00, 'Pemeliharaan selesai'),
(57, 15, 7, 2024, 3, 7, '2024-07-31', 498000000, 2000000, 99.60, 'Pemeliharaan selesai'),
(58, 15, 7, 2024, 4, 10, '2024-10-28', 480000000, 20000000, 96.00, 'Sedang berjalan'),

-- KEG-016: Revitalisasi Taman
(59, 16, 3, 2024, 1, 3, '2024-03-30', 980000000, 20000000, 98.00, 'Revitalisasi batch 1 selesai'),
(60, 16, 3, 2024, 3, 9, '2024-09-28', 950000000, 50000000, 95.00, 'Batch 2 dalam pengerjaan'),

-- KEG-017: Pembangunan RTH
(61, 17, 3, 2024, 2, 4, '2024-04-30', 1450000000, 50000000, 96.67, 'RTH fase 1 selesai'),
(62, 17, 3, 2024, 4, 10, '2024-10-26', 1400000000, 100000000, 93.33, 'RTH fase 2 dalam progress'),

-- KEG-018: BLT - All quarters realized
(63, 18, 4, 2024, 1, 1, '2024-01-15', 600000000, 0, 100.00, 'BLT tersalurkan semua'),
(64, 18, 4, 2024, 2, 4, '2024-04-15', 600000000, 0, 100.00, 'BLT tersalurkan semua'),
(65, 18, 4, 2024, 3, 7, '2024-07-15', 600000000, 0, 100.00, 'BLT tersalurkan semua'),
(66, 18, 4, 2024, 4, 10, '2024-10-15', 600000000, 0, 100.00, 'BLT tersalurkan semua'),

-- KEG-019: Bantuan Sembako
(67, 19, 4, 2024, 1, 2, '2024-02-20', 398000000, 2000000, 99.50, 'Sembako terdistribusi'),
(68, 19, 4, 2024, 3, 8, '2024-08-20', 395000000, 5000000, 98.75, 'Sembako terdistribusi'),

-- KEG-020: Pelatihan UMKM
(69, 20, 2, 2024, 1, 2, '2024-02-28', 195000000, 5000000, 97.50, 'Pelatihan batch 1 selesai'),
(70, 20, 2, 2024, 3, 8, '2024-08-30', 198000000, 2000000, 99.00, 'Pelatihan batch 2 selesai'),

-- KEG-021: Bantuan Modal UMKM
(71, 21, 5, 2024, 1, 3, '2024-03-25', 1000000000, 0, 100.00, 'Modal tersalurkan ke 100 UMKM'),
(72, 21, 5, 2024, 3, 9, '2024-09-25', 980000000, 20000000, 98.00, 'Modal tersalurkan'),

-- KEG-022: Bantuan Bibit Pupuk
(73, 22, 2, 2024, 1, 1, '2024-01-31', 800000000, 0, 100.00, 'Distribusi masa tanam 1 selesai'),
(74, 22, 2, 2024, 3, 7, '2024-07-31', 790000000, 10000000, 98.75, 'Distribusi masa tanam 2'),

-- KEG-023: Alsintan
(75, 23, 3, 2024, 1, 2, '2024-02-28', 1950000000, 50000000, 97.50, 'Alsintan batch 1 terdistribusi'),
(76, 23, 3, 2024, 3, 8, '2024-08-30', 1980000000, 20000000, 99.00, 'Alsintan batch 2 terdistribusi'),

-- KEG-024: Operasi Pasar
(77, 24, 2, 2024, 1, 1, '2024-01-31', 295000000, 5000000, 98.33, 'Operasi pasar berjalan lancar'),
(78, 24, 2, 2024, 2, 4, '2024-04-30', 300000000, 0, 100.00, 'Operasi pasar selesai'),
(79, 24, 2, 2024, 3, 7, '2024-07-31', 298000000, 2000000, 99.33, 'Operasi pasar selesai'),
(80, 24, 2, 2024, 4, 10, '2024-10-25', 290000000, 10000000, 96.67, 'Sedang berjalan'),

-- KEG-025: Cadangan Beras
(81, 25, 2, 2024, 1, 3, '2024-03-28', 500000000, 0, 100.00, 'Cadangan beras terpenuhi'),
(82, 25, 2, 2024, 3, 9, '2024-09-28', 495000000, 5000000, 99.00, 'Cadangan beras terpenuhi');

-- Create indexes for better query performance
CREATE INDEX idx_rencana_tahun_triwulan ON rencana_anggaran(tahun, triwulan);
CREATE INDEX idx_rencana_kegiatan ON rencana_anggaran(kegiatan_id);
CREATE INDEX idx_realisasi_tahun_triwulan ON realisasi_anggaran(tahun, triwulan);
CREATE INDEX idx_realisasi_kegiatan ON realisasi_anggaran(kegiatan_id);
CREATE INDEX idx_kegiatan_program ON kegiatan(program_id);
CREATE INDEX idx_program_opd ON program(opd_id);

-- Create view for easy reporting
CREATE OR REPLACE VIEW v_summary_anggaran AS
SELECT
    o.nama_opd,
    p.nama_program,
    k.nama_kegiatan,
    kb.nama_kategori,
    ra.tahun,
    ra.triwulan,
    ra.bulan,
    ra.nilai_anggaran,
    COALESCE(rea.nilai_realisasi, 0) as nilai_realisasi,
    COALESCE(rea.persentase_realisasi, 0) as persentase_realisasi,
    ra.sumber_dana,
    rea.tanggal_realisasi
FROM rencana_anggaran ra
LEFT JOIN kegiatan k ON ra.kegiatan_id = k.id
LEFT JOIN program p ON k.program_id = p.id
LEFT JOIN opd o ON p.opd_id = o.id
LEFT JOIN kategori_belanja kb ON ra.kategori_belanja_id = kb.id
LEFT JOIN realisasi_anggaran rea ON ra.id = rea.rencana_anggaran_id
ORDER BY o.nama_opd, p.nama_program, k.nama_kegiatan, ra.tahun, ra.triwulan, ra.bulan;

-- Grant permissions to superset user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO superset;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO superset;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO superset;
