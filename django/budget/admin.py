from django.contrib import admin
from .models import (
    Provinsi, KabupatenKota, ProgramKegiatan,
    JenisAnggaran, AnggaranDaerah, RealisasiBulanan
)

# Import django-superset-integration models
try:
    from django_superset_integration.models import SupersetInstance, SupersetDashboard

    # Unregister default admin if exists
    try:
        admin.site.unregister(SupersetInstance)
        admin.site.unregister(SupersetDashboard)
    except:
        pass
except ImportError:
    SupersetInstance = None
    SupersetDashboard = None


@admin.register(Provinsi)
class ProvinsiAdmin(admin.ModelAdmin):
    list_display = ['kode_provinsi', 'nama_provinsi']
    search_fields = ['nama_provinsi', 'kode_provinsi']


@admin.register(KabupatenKota)
class KabupatenKotaAdmin(admin.ModelAdmin):
    list_display = ['kode_kabkota', 'nama_kabkota', 'jenis', 'provinsi']
    list_filter = ['jenis', 'provinsi']
    search_fields = ['nama_kabkota', 'kode_kabkota']


@admin.register(ProgramKegiatan)
class ProgramKegiatanAdmin(admin.ModelAdmin):
    list_display = ['kode_program', 'nama_program']
    search_fields = ['nama_program', 'kode_program']


@admin.register(JenisAnggaran)
class JenisAnggaranAdmin(admin.ModelAdmin):
    list_display = ['kode_jenis', 'nama_jenis', 'kategori']
    list_filter = ['kategori']
    search_fields = ['nama_jenis', 'kode_jenis']


class RealisasiBulananInline(admin.TabularInline):
    model = RealisasiBulanan
    extra = 1


@admin.register(AnggaranDaerah)
class AnggaranDaerahAdmin(admin.ModelAdmin):
    list_display = [
        'kabupaten_kota', 'program', 'tahun_anggaran',
        'pagu_anggaran', 'realisasi_anggaran', 'persentase_realisasi', 'status'
    ]
    list_filter = ['tahun_anggaran', 'status', 'kabupaten_kota__provinsi', 'jenis_anggaran__kategori']
    search_fields = ['kabupaten_kota__nama_kabkota', 'program__nama_program']
    readonly_fields = ['persentase_realisasi', 'sisa_anggaran', 'created_at', 'updated_at']
    inlines = [RealisasiBulananInline]

    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('kabupaten_kota', 'program', 'jenis_anggaran', 'tahun_anggaran', 'status')
        }),
        ('Anggaran', {
            'fields': ('pagu_anggaran', 'realisasi_anggaran', 'sisa_anggaran', 'persentase_realisasi')
        }),
        ('Periode', {
            'fields': ('tanggal_mulai', 'tanggal_selesai')
        }),
        ('Keterangan', {
            'fields': ('keterangan',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RealisasiBulanan)
class RealisasiBulananAdmin(admin.ModelAdmin):
    list_display = ['anggaran', 'bulan', 'tahun', 'jumlah_realisasi']
    list_filter = ['tahun', 'bulan']
    search_fields = ['anggaran__kabupaten_kota__nama_kabkota', 'anggaran__program__nama_program']


# Custom Admin for Superset Integration (English labels)
if SupersetInstance and SupersetDashboard:

    @admin.register(SupersetInstance)
    class SupersetInstanceAdmin(admin.ModelAdmin):
        list_display = ['address', 'username']
        search_fields = ['address', 'username']

        fieldsets = (
            ('Superset Instance Configuration', {
                'fields': ('address', 'username', 'password'),
                'description': 'Configure connection to your Superset instance. '
                              'Address should not include http:// or https://.'
            }),
        )

        def get_form(self, request, obj=None, **kwargs):
            form = super().get_form(request, obj, **kwargs)
            # Override field labels
            if 'address' in form.base_fields:
                form.base_fields['address'].label = 'Superset Instance URL'
                form.base_fields['address'].help_text = 'Example: superset:8088 or localhost:8088'
            if 'username' in form.base_fields:
                form.base_fields['username'].label = 'Username'
                form.base_fields['username'].help_text = 'Superset user (default: superset_api or admin)'
            if 'password' in form.base_fields:
                form.base_fields['password'].label = 'Password'
                form.base_fields['password'].widget.attrs['type'] = 'password'
                form.base_fields['password'].help_text = 'Password will be encrypted'
            return form

    @admin.register(SupersetDashboard)
    class SupersetDashboardAdmin(admin.ModelAdmin):
        list_display = ['name', 'integration_id', 'domain', 'superset_link']
        list_filter = ['domain']
        search_fields = ['name', 'integration_id']

        fieldsets = (
            ('Dashboard Information', {
                'fields': ('name', 'integration_id', 'domain'),
            }),
            ('Additional Info', {
                'fields': ('superset_link', 'comment'),
                'classes': ('collapse',)
            }),
        )

        def get_form(self, request, obj=None, **kwargs):
            form = super().get_form(request, obj, **kwargs)
            # Override field labels
            if 'integration_id' in form.base_fields:
                form.base_fields['integration_id'].label = 'Dashboard ID'
                form.base_fields['integration_id'].help_text = 'Dashboard ID from Superset URL (e.g., 1, 2, 3...)'
            if 'name' in form.base_fields:
                form.base_fields['name'].label = 'Dashboard Name'
                form.base_fields['name'].help_text = 'Descriptive name for this dashboard'
            if 'domain' in form.base_fields:
                form.base_fields['domain'].label = 'Superset Instance'
                form.base_fields['domain'].help_text = 'Select the Superset instance where this dashboard exists'
            if 'comment' in form.base_fields:
                form.base_fields['comment'].label = 'Comment'
                form.base_fields['comment'].help_text = 'Optional notes about this dashboard'
            if 'superset_link' in form.base_fields:
                form.base_fields['superset_link'].label = 'Superset Dashboard Link'
                form.base_fields['superset_link'].help_text = 'Direct link to dashboard in Superset (optional)'
            return form
