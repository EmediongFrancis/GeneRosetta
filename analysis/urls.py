from django.urls import path
from .views import AnalyzeView
from .views import ProjectStatusView

urlpatterns = [
    path('analyze/', AnalyzeView.as_view(), name='analyze'),
    path('status/<uuid:project_id>/', ProjectStatusView.as_view(), name='status'),
]