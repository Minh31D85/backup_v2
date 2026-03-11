from django.urls import path
from .views import HealthView, BackupListView, BackupLatestView, BackupExportView, BackupImportView, BackupDeleteView, BackupGuiView

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),

    path("backups/", BackupListView.as_view(), name="backupList"),
    path("backups/latest/", BackupLatestView.as_view(), name="backupLatest"),
    path("backups/export/", BackupExportView.as_view(), name="backupExport"),
    path("backups/import/", BackupImportView.as_view(), name="backupImport"),
    path("backups/delete/", BackupDeleteView.as_view(), name="backupDelete"),
    path("backups/gui/", BackupGuiView.as_view(), name="backupGui")
]