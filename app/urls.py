from django.urls import path
from .views import HealthView, BackupListView, BackupLatestView, BackupExportView, BackupImportView, BackupDeleteView, BackupGuiView

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),

    path("api/backups/", BackupListView.as_view(), name="backupList"),
    path("api/backups/latest/", BackupLatestView.as_view(), name="backupLatest"),
    path("api/backups/export/", BackupExportView.as_view(), name="backupExport"),
    path("api/backups/import/", BackupImportView.as_view(), name="backupImport"),
    path("api/backups/delete/", BackupDeleteView.as_view(), name="backupDelete"),
    path("gui/", BackupGuiView.as_view(), name="backupGui")
]