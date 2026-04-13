import json
import os
from pathlib import Path
# from google.cloud import storage
from typing import List, Dict, Any

class StorageService:
    """
    Servicio para manejar el almacenamiento en Google Cloud Storage (GCS).
    En desarrollo, usa archivos locales en la carpeta 'registros/'.
    """

    def __init__(self, bucket_name: str = "guru_ai360"):
        """
        Inicializa el cliente de almacenamiento.

        Args:
            bucket_name (str): Nombre del bucket en GCS (no se usa en desarrollo).
        """
        self.bucket_name = bucket_name
        # self.storage_client = storage.Client()
        # self.bucket = self.storage_client.bucket(bucket_name)
        
        # Crear carpeta de registros si no existe (para desarrollo local)
        self.registros_dir = Path("registros")
        self.registros_dir.mkdir(exist_ok=True)

    def cargar_datos(self, blob_path: str) -> List[Dict[str, Any]]:
        """
        Carga datos desde un archivo JSON.
        
        En desarrollo: lee archivos locales desde carpeta 'registros/'.
        En producción: leerá desde GCS.

        Args:
            blob_path (str): Ruta del blob en el bucket (ejemplo: "registros/usuarios.json").

        Returns:
            List[Dict[str, Any]]: Lista de datos cargados.
        """
        # Implementación local para desarrollo
        file_path = Path(blob_path)
        
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except (json.JSONDecodeError, IOError):
                return []
        
        return []
        
        # Descomentar para usar GCS en producción:
        # blob = self.bucket.blob(blob_path)
        # if not blob.exists():
        #     return []
        # return json.loads(blob.download_as_text())

    def guardar_datos(self, blob_path: str, data: List[Dict[str, Any]]) -> None:
        """
        Guarda datos en un archivo JSON.
        
        En desarrollo: escribe archivos locales en carpeta 'registros/'.
        En producción: escribirá en GCS.

        Args:
            blob_path (str): Ruta del blob en el bucket (ejemplo: "registros/usuarios.json").
            data (List[Dict[str, Any]]): Datos a guardar.
        """
        # Implementación local para desarrollo
        file_path = Path(blob_path)
        
        # Crear directorio si no existe
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error al guardar datos: {e}")
        
        # Descomentar para usar GCS en producción:
        # blob = self.bucket.blob(blob_path)
        # blob.upload_from_string(
        #     json.dumps(data, ensure_ascii=False, indent=2),
        #     content_type="application/json"
        # )