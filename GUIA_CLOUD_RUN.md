# 🚀 Guía de Despliegue en Google Cloud Run

Este documento te guía paso a paso para desplegar tu aplicación FastAPI en Google Cloud Run usando Cloud Build.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener:

1. **Google Cloud SDK** instalado en tu máquina
   ```bash
   # En Windows (PowerShell)
   # Descarga desde: https://cloud.google.com/sdk/docs/install
   ```

2. **Proyecto activo en Google Cloud**
   ```bash
   gcloud projects list
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Git configurado** para usar Cloud Build con GitHub

---

## 🔧 Pasos de Configuración en GCP

### Paso 1: Crear Artifact Registry

```bash
# Crear un repositorio en Artifact Registry
gcloud artifacts repositories create ai360 \
    --repository-format=docker \
    --location=us-central1 \
    --description="Repository for AI360 backend"
```

### Paso 2: Configurar Permisos

```bash
# Otorgar permisos a Cloud Build para acceder a Artifact Registry
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member=serviceAccount:YOUR_PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
    --role=roles/artifactregistry.writer

# Otorgar permisos para desplegar a Cloud Run
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member=serviceAccount:YOUR_PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
    --role=roles/run.admin
```

### Paso 3: Conectar GitHub con Cloud Build

1. Ve a https://console.cloud.google.com/cloud-build/triggers
2. Haz clic en **"Create Trigger"**
3. Selecciona **GitHub** como fuente
4. Conecta tu repositorio
5. Configura:
   - **Build configuration**: `Cloud Build configuration file (yaml)`
   - **Location**: `Repository`
   - **Cloud Build configuration file location**: `cloudbuild.yaml`

---

## 📝 Configurar Variables de Sustitución

En tu `cloudbuild.yaml`, personaliza estas variables en la sección `substitutions`:

```yaml
substitutions:
  _REGION: 'us-central1'              # Tu región preferida
  _ARTIFACT_REGISTRY: 'ai360'         # Nombre de tu repositorio
  _IMAGE_NAME: 'ai360-backend'        # Nombre de la imagen
  _SERVICE_NAME: 'ai360-backend'      # Nombre del servicio Cloud Run
```

### Regiones Disponibles:
- `us-central1` (Iowa - USA)
- `europe-west1` (Bélgica)
- `asia-northeast1` (Tokyo - Japón)

---

## 🚀 Desplegar Manualmente (Sin GitHub)

Si quieres probar sin GitHub, ejecuta:

```bash
# 1. Compila la imagen localmente
docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ai360/ai360-backend:latest .

# 2. Sube a Artifact Registry
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ai360/ai360-backend:latest

# 3. Despliega en Cloud Run
gcloud run deploy ai360-backend \
    --image=us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ai360/ai360-backend:latest \
    --region=us-central1 \
    --platform=managed \
    --allow-unauthenticated \
    --port=8000 \
    --memory=512Mi \
    --cpu=1 \
    --timeout=3600
```

---

## ✅ Verificar Despliegue

```bash
# Ver servicios en Cloud Run
gcloud run services list

# Ver logs en tiempo real
gcloud run services logs read ai360-backend --region=us-central1 --limit=50 --follow

# Probar el endpoint
curl https://ai360-backend-xxxxxxx.run.app/docs
```

---

## 🔐 Variables de Entorno en Cloud Run

Si necesitas añadir variables de entorno (ej: para Google Cloud Storage):

```bash
gcloud run services update ai360-backend \
    --region=us-central1 \
    --set-env-vars=GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/gcs-key.json
```

---

## 📊 Monitorear el Despliegue

En Google Cloud Console:
1. Ve a **Cloud Run** → **Services**
2. Haz clic en tu servicio
3. Visualiza:
   - **Métricas**: CPU, Memoria, Requests
   - **Logs**: Errores y accesos
   - **Revisiones**: Historial de deployments

---

## 🐛 Solucionar Problemas

### Error: "Permission denied" durante build

```bash
# Verifica que Cloud Build tenga permisos
gcloud projects get-iam-policy YOUR_PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:*@cloudbuild.gserviceaccount.com"
```

### Error: "Image not found" durante deploy

- Verifica que Artifact Registry exista
- Confirma que Cloud Build subió la imagen ejecutando:
  ```bash
  gcloud artifacts docker images list us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ai360
  ```

### Error de puerto en Cloud Run

Cloud Run siempre requiere que la aplicación escuche en la variable `PORT` (default 8000).
Nuestro Dockerfile ya lo maneja con: `${PORT:-8000}`

---

## 💡 Optimizaciones Recomendadas

1. **Aumentar memoria si es necesario**:
   ```bash
   gcloud run services update ai360-backend \
       --memory=1Gi \
       --cpu=2
   ```

2. **Auto-scaling**:
   ```bash
   gcloud run services update ai360-backend \
       --min-instances=1 \
       --max-instances=10
   ```

3. **Timeouts largos para procesos**:
   Ya configurado en `cloudbuild.yaml`: `timeout=3600` (1 hora)

---

## 📚 Referencias Útiles

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Configuration](https://cloud.google.com/build/docs/build-config)
- [FastAPI on Cloud Run](https://cloud.google.com/python/docs/reference/functions/latest/services)
- [Artifact Registry Guide](https://cloud.google.com/artifact-registry/docs)

---

## ✨ Checklist Final

- [ ] Google Cloud SDK instalado y configurado
- [ ] Proyecto GCP creado y activo
- [ ] Artifact Registry creado
- [ ] Permisos configurados
- [ ] GitHub conectado con Cloud Build
- [ ] `Dockerfile` en la raíz del repositorio
- [ ] `cloudbuild.yaml` en la raíz del repositorio
- [ ] Variables de sustitución personalizadas
- [ ] Push realizado a GitHub
- [ ] Build completado exitosamente
- [ ] Servicio activo en Cloud Run

¡Listo! Tu aplicación debe estar disponible en `https://ai360-backend-xxxxxxx.run.app` 🎉
