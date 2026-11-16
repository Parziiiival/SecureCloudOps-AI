from django.urls import path  # type: ignore[reportMissingModulesSource]
from . import views

urlpatterns = [
    path("", views.index, name="dashboard_index"),
    path("explain/<int:finding_id>/", views.explain_finding, name="explain_finding"),
]