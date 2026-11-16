import os
import time
import requests
from django.http import JsonResponse  # type: ignore[reportMissingModulesSource]
from django.shortcuts import get_object_or_404, render  # type: ignore[reportMissingModulesSource]
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


def _call_gemini_model(model_name, headers, payload):
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent"
    return requests.post(url, headers=headers, json=payload, timeout=(10, 60))


def _get_fallback_models(api_key):
    try:
        resp = requests.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            headers={"x-goog-api-key": api_key},
            timeout=15,
        )
        resp.raise_for_status()
        models = resp.json().get("models", [])
        return [
            m["name"]
            for m in models
            if "generateContent" in m.get("supportedGenerationMethods", [])
            and "gemini" in m.get("name", "").lower()
            and "2.5" not in m.get("name", "")
            and m.get("name") != "models/gemini-3.8-flash"
        ]
    except requests.RequestException:
        return []


def explain_finding(request, finding_id):
    finding = get_object_or_404(SecurityFinding, id=finding_id)
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return JsonResponse(
            {"error": "GEMINI_API_KEY is missing from your .env file."},
            status=500,
        )

    description = getattr(finding, "description", "")
    prompt = (
        "You are a senior DevSecOps engineer. In under 150 words, provide: "
        "(1) a 2-sentence explanation of the security risk, and "
        "(2) 3 concrete step-by-step remediation instructions.\n\n"
        f"Title: {finding.title}\n"
        f"Scanner Tool: {finding.tool}\n"
        f"Severity: {finding.severity}\n"
        f"Affected Component: {finding.component}\n"
        f"Details: {description}"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    models_to_try = ["models/gemini-3.8-flash", "models/gemini-3.8-flash"]
    last_error = "Unable to reach Gemini API."

    for idx, model_name in enumerate(models_to_try):
        if idx == 1:
            time.sleep(2)
            for fallback in _get_fallback_models(api_key):
                if fallback not in models_to_try:
                    models_to_try.append(fallback)

        try:
            response = _call_gemini_model(model_name, headers, payload)
            if response.status_code in (404, 429, 503):
                last_error = response.text
                continue

            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates") or []
            parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
            advice = parts[0].get("text") if parts else None

            if advice:
                return JsonResponse({"title": finding.title, "advice": advice})

            last_error = f"Empty response from {model_name}: {data}"
        except requests.RequestException as exc:
            last_error = exc.response.text if exc.response is not None else str(exc)

    print("Gemini API error:", last_error)
    return JsonResponse({"error": f"Gemini API error: {last_error}"}, status=502)