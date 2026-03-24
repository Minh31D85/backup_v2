import json

from django.shortcuts import render
from django.conf import settings
from django.utils.text import slugify

from datetime import datetime, timezone
from pathlib import Path

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from .auth import BackupAuth
from .models import PasswordItem
from .serializers import PasswordItemSerializer


def _list_apps() -> list[str]:
    root = Path(settings.BACKUP_ROOT)
    if not root.exists():
        return []
    
    return sorted(
        d.name
        for d in root.iterdir()
        if d.is_dir() and any(d.glob("*.json"))
    )


def _app_dir(app: str) -> Path:
    app_slug = slugify(app)
    if not app_slug:
        raise ValueError('Invalid app name')
    
    backup_root = Path(settings.BACKUP_ROOT)
    if not backup_root.exists():
        raise RuntimeError("BACKUP_ROOT does not exist")
    
    app_dir = backup_root / app_slug
    app_dir.mkdir(parents=True, exist_ok=True)

    return app_dir


def _list_backup_files(app: str) -> list[Path]:
    backup_dir = _app_dir(app)
    return sorted(backup_dir.glob("*.json"))


def _latest_backup_files(app: str) -> Path | None:
    files = _list_backup_files(app)
    if not files:
        return None
    
    return max(files, key=lambda f: f.stat().st_mtime)


def _cleanup_old_backups(app: str, keep: int = 5) -> int:
    files = _list_backup_files(app)
    if len(files) <= keep:
        return 0
    
    files_sorted = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)

    deleted = 0
    for f in files_sorted[keep:]:
        try:
            f.unlink()
            deleted += 1
        except Exception: 
            pass
    return deleted



class HealthView(APIView):
    
    def get(self, request):
        return Response({'status': 'ok'})
    

class BackupListView(APIView):
    authentication_classes = [BackupAuth]
    permission_classes = [AllowAny]

    def get(self, request):
        app = request.query_params.get("app")
        if not app:
            return Response({"message": "Missing query param: app"}, status=status.HTTP_400_BAD_REQUEST)

        files = _list_backup_files(app)
        items = []
        for f in files:
            stat = f.stat()
            items.append({
                "filename": f.name,
                "path": str(f.relative_to(settings.BACKUP_ROOT)),
                "bytes": stat.st_size,
                "modifiedAt": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            })
        
        return Response({
            "app": slugify(app),
            "count": len(items),
            "items": items
        })
    

class BackupLatestView(APIView):
    authentication_classes = [BackupAuth]
    permission_classes = [AllowAny]

    def get(self, request):
        app = request.query_params.get("app")
        if not app:
            return Response({"app": slugify(app), "latest": None}, status=status.HTTP_400_BAD_REQUEST)
        
        file = _latest_backup_files(app)
        if not file:
            return Response({"app": slugify(app), "latest": None}, status=status.HTTP_200_OK)
        
        stat = file.stat()
        return Response({
            "app": slugify(app),
            "latest": {
                "filename": file.name,
                "path": str(file.relative_to(settings.BACKUP_ROOT)),
                "bytes": stat.st_size,
                "modifiedAt": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            }
        })
    

class BackupExportView(APIView):
    authentication_classes = [BackupAuth]
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        app = data.get("app")
        schema_Version = data.get("schemaVersion")
        payload = data.get("payload")

        if not app:
            return Response({"message": "Missing field: app"}, status=status.HTTP_400_BAD_REQUEST)
        
        if schema_Version is None:
            return Response({"message": "Missing field: schemaVision"}, status=status.HTTP_400_BAD_REQUEST)
        
        if payload is None:
            return Response({"message": "Missing field: payload"}, status=status.HTTP_400_BAD_REQUEST)
        
        app_slug = slugify(app)
        export_time = datetime.now(timezone.utc)
        export_at = export_time.isoformat()

        backup_obj = {
            "app": app_slug,
            "schemaVersion": schema_Version,
            "exportAt": export_at,
            "payload": payload
        }

        filename = export_time.strftime("%Y%m%dT%H%M%SZ") + ".json"
        target_dir = _app_dir(app_slug)
        target_file = target_dir / filename

        target_file.write_text(json.dumps(backup_obj, ensure_ascii=False, indent=2), encoding="utf-8")
        deleted_count = _cleanup_old_backups(app_slug, keep=5)
        stat = target_file.stat()

        return Response({
            "message": "exported",
            "deletedOldBackups": deleted_count,
            "file": {
                "filename": filename,
                "path": str(target_file.relative_to(settings.BACKUP_ROOT)),
                "bytes": stat.st_size,
                "modifiedAt": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            }
        }, status=status.HTTP_201_CREATED)
    

class BackupImportView(APIView):
    authentication_classes = [BackupAuth]
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        app = data.get("app")
        rel_path = data.get("path")

        if not app:
            return Response({"message": "Missing field: app"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not rel_path:
            return Response({"message": "Missing field: path"}, status=status.HTTP_400_BAD_REQUEST)
        
        app_slug = slugify(app)
        root = Path(settings.BACKUP_ROOT).resolve()
        file_path = (root / rel_path).resolve()

        if not str(file_path).startswith(str(root)):
            return Response({"message": "File not found", "path": rel_path}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            raw = file_path.read_text(encoding="utf-8")
            obj = json.loads(raw)
        except Exception:
            return Response({"message": "Invalid JSON file"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        if "exportAt" not in obj and "exportedAt" in obj:
            obj["exportAt"] = obj ["exportedAt"]
        
        for k in ["app", "schemaVersion", "exportAt", "payload"]:
            if k not in obj:
                return Response({"message": f"Missing key in backup file: {k}"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
        if slugify(str(obj.get("app"))) != app_slug:
            return Response({"message": "App mismatch", "expected": app_slug, "found": obj.get("app")}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        return Response(obj, status=status.HTTP_200_OK)
    

class BackupDeleteView(APIView):

    def post(self, request):
        rel_path = request.data.get("path")

        if not rel_path:
            return Response({"message": "Missing field: path"}, status=status.HTTP_400_BAD_REQUEST)
        
        root = Path(settings.BACKUP_ROOT).resolve()
        file_path = (root / rel_path).resolve()

        if not file_path.exists():
            return Response({"message": "File not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not str(file_path).startswith(str(root)):
            return Response({"message": "Invalid path"}, status=status.HTTP_400_BAD_REQUEST)
        
        if file_path.suffix != ".json":
            return Response({"message": "Invalid file type"}, status=status.HTTP_400_BAD_REQUEST)
        
        file_path.unlink()

        return Response({"message": "delete", "path": rel_path}, status=status.HTTP_200_OK )
    


class BackupGuiView(APIView):
    def get(self, request):
        apps = _list_apps()
        app = request.GET.get("app")

        if not app and apps:
            app = apps[0]

        items = []

        if app:
            files = _list_backup_files(app)
            for file_path in files:
                stat = file_path.stat()
                try:
                    relative_path = file_path.relative_to(settings.BACKUP_ROOT)
                except Exception:
                    continue

                items.append({
                    "filename": file_path.name,
                    "path": str(relative_path),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime)
                })
        
        return render(request, "backup_gui.html", {
            "apps": apps,
            "active_app": app,
            "items": items
        })
    

class PasswordViewSet(viewsets.ModelViewSet):
    serializer_class = PasswordItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user

        return PasswordItem.objects.filter(
            group__application__user=user
        )
