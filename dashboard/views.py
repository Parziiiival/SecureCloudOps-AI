from django.shortcuts import render  # type: ignore[reportMissingModuleSource]
from .models import SecurityFinding

def index(request):
    findings = SecurityFinding.objects.all().order_by('-detected_at')
    
    # Calculate severity counts for the top summary cards
    context = {
        'findings': findings,
        'total_count': findings.count(),
        'critical_count': findings.filter(severity='CRITICAL').count(),
        'high_count': findings.filter(severity='HIGH').count(),
        'medium_count': findings.filter(severity='MEDIUM').count(),
        'low_count': findings.filter(severity='LOW').count(),
    }
    return render(request, 'dashboard/index.html', context)