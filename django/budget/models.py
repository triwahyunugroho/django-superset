from django.db import models


class Provinsi(models.Model):
    kode_provinsi = models.CharField(max_length=2, unique=True)
    nama_provinsi = models.CharField(max_length=100)

    class Meta:
        db_table = 'provinsi'
        verbose_name_plural = 'Provinsi'

    def __str__(self):
        return self.nama_provinsi


class KabupatenKota(models.Model):
    JENIS_CHOICES = [
        ('KABUPATEN', 'Kabupaten'),
        ('KOTA', 'Kota'),
    ]

    provinsi = models.ForeignKey(Provinsi, on_delete=models.CASCADE, related_name='kabupaten_kota')
    kode_kabkota = models.CharField(max_length=4, unique=True)
    nama_kabkota = models.CharField(max_length=100)
    jenis = models.CharField(max_length=10, choices=JENIS_CHOICES)

    class Meta:
        db_table = 'kabupaten_kota'
        verbose_name_plural = 'Kabupaten/Kota'

    def __str__(self):
        return f"{self.jenis} {self.nama_kabkota}"


class ProgramKegiatan(models.Model):
    kode_program = models.CharField(max_length=20, unique=True)
    nama_program = models.CharField(max_length=255)
    deskripsi = models.TextField(blank=True)

    class Meta:
        db_table = 'program_kegiatan'
        verbose_name_plural = 'Program Kegiatan'

    def __str__(self):
        return self.nama_program


class JenisAnggaran(models.Model):
    KATEGORI_CHOICES = [
        ('BELANJA_PEGAWAI', 'Belanja Pegawai'),
        ('BELANJA_BARANG_JASA', 'Belanja Barang dan Jasa'),
        ('BELANJA_MODAL', 'Belanja Modal'),
        ('BELANJA_HIBAH', 'Belanja Hibah'),
        ('BELANJA_BANTUAN_SOSIAL', 'Belanja Bantuan Sosial'),
    ]

    kode_jenis = models.CharField(max_length=20, unique=True)
    nama_jenis = models.CharField(max_length=100)
    kategori = models.CharField(max_length=30, choices=KATEGORI_CHOICES)

    class Meta:
        db_table = 'jenis_anggaran'
        verbose_name_plural = 'Jenis Anggaran'

    def __str__(self):
        return self.nama_jenis


class AnggaranDaerah(models.Model):
    STATUS_CHOICES = [
        ('RENCANA', 'Rencana'),
        ('DISETUJUI', 'Disetujui'),
        ('DIREALISASI', 'Direalisasi'),
        ('SELESAI', 'Selesai'),
    ]

    kabupaten_kota = models.ForeignKey(KabupatenKota, on_delete=models.CASCADE, related_name='anggaran')
    program = models.ForeignKey(ProgramKegiatan, on_delete=models.CASCADE, related_name='anggaran')
    jenis_anggaran = models.ForeignKey(JenisAnggaran, on_delete=models.CASCADE, related_name='anggaran')

    tahun_anggaran = models.IntegerField()
    pagu_anggaran = models.DecimalField(max_digits=15, decimal_places=2)
    realisasi_anggaran = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sisa_anggaran = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    persentase_realisasi = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RENCANA')

    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField()

    keterangan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'anggaran_daerah'
        verbose_name_plural = 'Anggaran Daerah'
        ordering = ['-tahun_anggaran', '-pagu_anggaran']

    def __str__(self):
        return f"{self.kabupaten_kota} - {self.program} ({self.tahun_anggaran})"

    def save(self, *args, **kwargs):
        # Hitung sisa anggaran
        self.sisa_anggaran = self.pagu_anggaran - self.realisasi_anggaran

        # Hitung persentase realisasi
        if self.pagu_anggaran > 0:
            self.persentase_realisasi = (self.realisasi_anggaran / self.pagu_anggaran) * 100

        super().save(*args, **kwargs)


class RealisasiBulanan(models.Model):
    BULAN_CHOICES = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'),
        (4, 'April'), (5, 'Mei'), (6, 'Juni'),
        (7, 'Juli'), (8, 'Agustus'), (9, 'September'),
        (10, 'Oktober'), (11, 'November'), (12, 'Desember'),
    ]

    anggaran = models.ForeignKey(AnggaranDaerah, on_delete=models.CASCADE, related_name='realisasi_bulanan')
    bulan = models.IntegerField(choices=BULAN_CHOICES)
    tahun = models.IntegerField()
    jumlah_realisasi = models.DecimalField(max_digits=15, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'realisasi_bulanan'
        verbose_name_plural = 'Realisasi Bulanan'
        unique_together = ['anggaran', 'bulan', 'tahun']
        ordering = ['tahun', 'bulan']

    def __str__(self):
        return f"{self.anggaran} - {self.get_bulan_display()} {self.tahun}"
