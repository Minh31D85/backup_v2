from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthView, BackupListView, BackupLatestView, BackupExportView, BackupImportView, BackupDeleteView, BackupGuiView, PasswordViewSet

router = DefaultRouter()
router.register(r'password', PasswordViewSet, basename='password')

urlpatterns = [
    # Ping
    path('health/', HealthView.as_view(), name='health'),

    # Backup API
    path("api/backups/", BackupListView.as_view(), name="backupList"),
    path("api/backups/latest/", BackupLatestView.as_view(), name="backupLatest"),
    path("api/backups/export/", BackupExportView.as_view(), name="backupExport"),
    path("api/backups/import/", BackupImportView.as_view(), name="backupImport"),
    path("api/backups/delete/", BackupDeleteView.as_view(), name="backupDelete"),

    # GUI
    path("gui/", BackupGuiView.as_view(), name="backupGui"),

    # Password API
    path("api/", include(router.urls))
]