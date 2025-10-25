from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import random

from budget.models import (
    Provinsi, KabupatenKota, ProgramKegiatan,
    JenisAnggaran, AnggaranDaerah, RealisasiBulanan
)


class Command(BaseCommand):
    help = 'Load dummy data untuk anggaran pemerintah daerah'

    def handle(self, *args, **options):
        self.stdout.write('Memulai loading dummy data...')

        # Clear existing data
        self.stdout.write('Menghapus data lama...')
        RealisasiBulanan.objects.all().delete()
        AnggaranDaerah.objects.all().delete()
        JenisAnggaran.objects.all().delete()
        ProgramKegiatan.objects.all().delete()
        KabupatenKota.objects.all().delete()
        Provinsi.objects.all().delete()

        # Create Provinsi
        self.stdout.write('Membuat data provinsi...')
        provinsi_data = [
            ('31', 'DKI Jakarta'),
            ('32', 'Jawa Barat'),
            ('33', 'Jawa Tengah'),
            ('34', 'DI Yogyakarta'),
            ('35', 'Jawa Timur'),
            ('51', 'Bali'),
            ('73', 'Sulawesi Selatan'),
        ]

        provinsi_objects = {}
        for kode, nama in provinsi_data:
            prov = Provinsi.objects.create(kode_provinsi=kode, nama_provinsi=nama)
            provinsi_objects[kode] = prov
            self.stdout.write(f'  - {nama}')

        # Create Kabupaten/Kota
        self.stdout.write('Membuat data kabupaten/kota...')
        kabkota_data = [
            ('3101', 'Jakarta Pusat', 'KOTA', '31'),
            ('3102', 'Jakarta Utara', 'KOTA', '31'),
            ('3103', 'Jakarta Barat', 'KOTA', '31'),
            ('3201', 'Bogor', 'KABUPATEN', '32'),
            ('3202', 'Sukabumi', 'KABUPATEN', '32'),
            ('3273', 'Bandung', 'KOTA', '32'),
            ('3301', 'Cilacap', 'KABUPATEN', '33'),
            ('3302', 'Banyumas', 'KABUPATEN', '33'),
            ('3371', 'Semarang', 'KOTA', '33'),
            ('3401', 'Kulon Progo', 'KABUPATEN', '34'),
            ('3471', 'Yogyakarta', 'KOTA', '34'),
            ('3501', 'Pacitan', 'KABUPATEN', '35'),
            ('3578', 'Surabaya', 'KOTA', '35'),
            ('5101', 'Jembrana', 'KABUPATEN', '51'),
            ('5171', 'Denpasar', 'KOTA', '51'),
            ('7301', 'Kepulauan Selayar', 'KABUPATEN', '73'),
            ('7371', 'Makassar', 'KOTA', '73'),
        ]

        kabkota_objects = []
        for kode, nama, jenis, kode_prov in kabkota_data:
            kabkota = KabupatenKota.objects.create(
                kode_kabkota=kode,
                nama_kabkota=nama,
                jenis=jenis,
                provinsi=provinsi_objects[kode_prov]
            )
            kabkota_objects.append(kabkota)
            self.stdout.write(f'  - {jenis} {nama}')

        # Create Program Kegiatan
        self.stdout.write('Membuat data program kegiatan...')
        program_data = [
            ('1.01.01', 'Program Pelayanan Administrasi Perkantoran', 'Program untuk meningkatkan pelayanan administrasi perkantoran'),
            ('1.02.01', 'Program Peningkatan Sarana dan Prasarana Aparatur', 'Program peningkatan sarana dan prasarana'),
            ('1.03.01', 'Program Peningkatan Kapasitas Sumber Daya Aparatur', 'Program pelatihan dan pengembangan SDM'),
            ('2.01.01', 'Program Pendidikan Anak Usia Dini', 'Program PAUD dan TK'),
            ('2.02.01', 'Program Wajib Belajar Pendidikan Dasar 9 Tahun', 'Program pendidikan SD dan SMP'),
            ('2.03.01', 'Program Pendidikan Menengah', 'Program pendidikan SMA/SMK'),
            ('3.01.01', 'Program Obat dan Perbekalan Kesehatan', 'Program pengadaan obat dan alat kesehatan'),
            ('3.02.01', 'Program Upaya Kesehatan Masyarakat', 'Program puskesmas dan posyandu'),
            ('3.03.01', 'Program Peningkatan Pelayanan Kesehatan', 'Program rumah sakit dan klinik'),
            ('4.01.01', 'Program Pembangunan Jalan dan Jembatan', 'Program infrastruktur jalan'),
            ('4.02.01', 'Program Rehabilitasi dan Pemeliharaan Jalan', 'Program pemeliharaan jalan'),
            ('5.01.01', 'Program Pemberdayaan Masyarakat dan Desa', 'Program pemberdayaan masyarakat'),
            ('5.02.01', 'Program Pengembangan Ekonomi Lokal', 'Program UMKM dan ekonomi kreatif'),
        ]

        program_objects = []
        for kode, nama, desk in program_data:
            prog = ProgramKegiatan.objects.create(
                kode_program=kode,
                nama_program=nama,
                deskripsi=desk
            )
            program_objects.append(prog)
            self.stdout.write(f'  - {nama}')

        # Create Jenis Anggaran
        self.stdout.write('Membuat data jenis anggaran...')
        jenis_data = [
            ('5.1.1', 'Belanja Gaji dan Tunjangan', 'BELANJA_PEGAWAI'),
            ('5.1.2', 'Belanja Tambahan Penghasilan PNS', 'BELANJA_PEGAWAI'),
            ('5.2.1', 'Belanja Bahan Pakai Habis', 'BELANJA_BARANG_JASA'),
            ('5.2.2', 'Belanja Jasa', 'BELANJA_BARANG_JASA'),
            ('5.2.3', 'Belanja Pemeliharaan', 'BELANJA_BARANG_JASA'),
            ('5.2.4', 'Belanja Perjalanan Dinas', 'BELANJA_BARANG_JASA'),
            ('5.3.1', 'Belanja Tanah', 'BELANJA_MODAL'),
            ('5.3.2', 'Belanja Peralatan dan Mesin', 'BELANJA_MODAL'),
            ('5.3.3', 'Belanja Gedung dan Bangunan', 'BELANJA_MODAL'),
            ('5.3.4', 'Belanja Jalan, Irigasi dan Jaringan', 'BELANJA_MODAL'),
            ('5.4.1', 'Belanja Hibah kepada Pemerintah', 'BELANJA_HIBAH'),
            ('5.5.1', 'Belanja Bantuan Sosial kepada Masyarakat', 'BELANJA_BANTUAN_SOSIAL'),
        ]

        jenis_objects = []
        for kode, nama, kategori in jenis_data:
            jenis = JenisAnggaran.objects.create(
                kode_jenis=kode,
                nama_jenis=nama,
                kategori=kategori
            )
            jenis_objects.append(jenis)
            self.stdout.write(f'  - {nama}')

        # Create Anggaran Daerah
        self.stdout.write('Membuat data anggaran daerah...')
        tahun_list = [2023, 2024, 2025]
        status_list = ['RENCANA', 'DISETUJUI', 'DIREALISASI', 'SELESAI']

        anggaran_objects = []
        for tahun in tahun_list:
            for kabkota in kabkota_objects:
                # Setiap kabupaten/kota punya beberapa program
                num_programs = random.randint(5, 8)
                selected_programs = random.sample(program_objects, num_programs)

                for program in selected_programs:
                    # Setiap program punya beberapa jenis anggaran
                    num_jenis = random.randint(2, 4)
                    selected_jenis = random.sample(jenis_objects, num_jenis)

                    for jenis in selected_jenis:
                        pagu = Decimal(random.randint(100_000_000, 10_000_000_000))

                        # Tentukan status berdasarkan tahun
                        if tahun == 2023:
                            status = 'SELESAI'
                            realisasi_persen = random.uniform(85, 98)
                        elif tahun == 2024:
                            status = random.choice(['DIREALISASI', 'SELESAI'])
                            realisasi_persen = random.uniform(70, 95)
                        else:  # 2025
                            status = random.choice(['RENCANA', 'DISETUJUI', 'DIREALISASI'])
                            if status == 'RENCANA':
                                realisasi_persen = 0
                            elif status == 'DISETUJUI':
                                realisasi_persen = random.uniform(0, 20)
                            else:
                                realisasi_persen = random.uniform(20, 60)

                        realisasi = pagu * Decimal(realisasi_persen / 100)

                        # Tanggal
                        tanggal_mulai = date(tahun, 1, 1)
                        tanggal_selesai = date(tahun, 12, 31)

                        anggaran = AnggaranDaerah.objects.create(
                            kabupaten_kota=kabkota,
                            program=program,
                            jenis_anggaran=jenis,
                            tahun_anggaran=tahun,
                            pagu_anggaran=pagu,
                            realisasi_anggaran=realisasi,
                            status=status,
                            tanggal_mulai=tanggal_mulai,
                            tanggal_selesai=tanggal_selesai,
                            keterangan=f'Anggaran {program.nama_program} untuk {kabkota.nama_kabkota} tahun {tahun}'
                        )
                        anggaran_objects.append(anggaran)

        self.stdout.write(f'  - Dibuat {len(anggaran_objects)} data anggaran')

        # Create Realisasi Bulanan
        self.stdout.write('Membuat data realisasi bulanan...')
        realisasi_count = 0
        for anggaran in anggaran_objects:
            if anggaran.status in ['DIREALISASI', 'SELESAI']:
                # Tentukan sampai bulan berapa
                if anggaran.tahun_anggaran == 2023 or anggaran.status == 'SELESAI':
                    max_bulan = 12
                elif anggaran.tahun_anggaran == 2024:
                    max_bulan = 12
                else:  # 2025 dan masih direalisasi
                    max_bulan = 10  # Oktober 2025

                total_realisasi = anggaran.realisasi_anggaran
                remaining = total_realisasi

                for bulan in range(1, max_bulan + 1):
                    if bulan < max_bulan:
                        # Distribusi acak tapi wajar
                        if remaining > 0:
                            max_realisasi_bulan = remaining * Decimal(0.3)  # Max 30% sisa per bulan
                            realisasi_bulan = Decimal(random.uniform(
                                float(total_realisasi * Decimal(0.03)),  # Min 3% dari total
                                float(max_realisasi_bulan)
                            ))
                        else:
                            realisasi_bulan = Decimal(0)
                    else:
                        # Bulan terakhir, gunakan sisa
                        realisasi_bulan = remaining

                    RealisasiBulanan.objects.create(
                        anggaran=anggaran,
                        bulan=bulan,
                        tahun=anggaran.tahun_anggaran,
                        jumlah_realisasi=realisasi_bulan
                    )
                    remaining -= realisasi_bulan
                    realisasi_count += 1

        self.stdout.write(f'  - Dibuat {realisasi_count} data realisasi bulanan')

        # Summary
        self.stdout.write(self.style.SUCCESS('\nSummary:'))
        self.stdout.write(f'  - Provinsi: {Provinsi.objects.count()}')
        self.stdout.write(f'  - Kabupaten/Kota: {KabupatenKota.objects.count()}')
        self.stdout.write(f'  - Program Kegiatan: {ProgramKegiatan.objects.count()}')
        self.stdout.write(f'  - Jenis Anggaran: {JenisAnggaran.objects.count()}')
        self.stdout.write(f'  - Anggaran Daerah: {AnggaranDaerah.objects.count()}')
        self.stdout.write(f'  - Realisasi Bulanan: {RealisasiBulanan.objects.count()}')

        self.stdout.write(self.style.SUCCESS('\nDummy data berhasil dimuat!'))
