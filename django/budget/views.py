from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import AnggaranDaerah, Provinsi, KabupatenKota


def index(request):
    """Home page"""
    total_anggaran = AnggaranDaerah.objects.count()
    total_provinsi = Provinsi.objects.count()
    total_kabkota = KabupatenKota.objects.count()

    context = {
        'total_anggaran': total_anggaran,
        'total_provinsi': total_provinsi,
        'total_kabkota': total_kabkota,
    }

    return render(request, 'budget/index.html', context)


def dashboard(request):
    """Dashboard page with Superset integration using Embedded SDK"""
    # Dashboard ID dari Superset (UUID format untuk Superset 3.0+)
    superset_dashboard_id = 'bd3a437e-a613-4fe2-ac77-937ae03e5e94'

    context = {
        'dashboard_id': 1,  # ID untuk guest token endpoint (dari django_superset_integration)
        'superset_dashboard_id': superset_dashboard_id,  # ID dashboard di Superset
        'superset_domain': 'localhost:8088',  # Domain Superset
    }
    return render(request, 'budget/dashboard.html', context)


def superset_proxy(request, dashboard_id):
    """Proxy to Superset dashboard for iframe embedding"""
    # Redirect ke Superset dengan standalone mode
    superset_url = f"http://localhost:8088/superset/dashboard/{dashboard_id}/?standalone=true"
    return redirect(superset_url)
