# Despliegue de MEMORA AI desde GitHub

Este repositorio ya incluye un Blueprint de Render en `render.yaml`. El servicio se construye desde `main`, ejecuta migraciones Alembic antes de iniciar FastAPI y genera automáticamente `MEMORA_API_TOKEN`.

## 1. Crear PostgreSQL en Neon

1. Inicia sesión en Neon y crea un proyecto PostgreSQL.
2. Selecciona una región cercana a los usuarios de Ecuador si está disponible.
3. Copia la cadena de conexión PostgreSQL con SSL habilitado.
4. No publiques esa cadena en GitHub ni la envíes por chat.

Render necesita la variable `MEMORA_DATABASE_URL`. Si Neon entrega una URL que empieza con `postgresql://`, conserva el resto de sus parámetros SSL. Si el driver de la URL no coincide con el driver instalado por el backend, revisa `backend/requirements.txt` y la configuración SQLAlchemy antes del primer despliegue.

## 2. Crear el servicio desde el Blueprint

1. En Render, elige **New → Blueprint**.
2. Conecta la cuenta de GitHub y selecciona `LuisCorrea2007/BlueClass`.
3. Render detectará `render.yaml` y mostrará el servicio `memora-ai-api`.
4. Antes de confirmar, revisa que el plan y las variables estén correctos.
5. En el paso de configuración, pega la URL de Neon únicamente en el campo secreto `MEMORA_DATABASE_URL`.
6. Confirma la creación. Render generará `MEMORA_API_TOKEN` y desplegará automáticamente cada actualización de `main`.

## 3. Validación después del despliegue

- Abre `https://<dominio-render>/api/health` y confirma respuesta saludable.
- Comprueba que la API rechaza peticiones protegidas sin bearer token.
- Verifica conexión a PostgreSQL y que las migraciones se hayan aplicado.
- Configura el token en MEMORA AI Sync y en el panel web. Nunca lo guardes en el repositorio.

## Consideraciones del plan gratuito

Los servicios gratuitos pueden suspenderse por inactividad, tener límites de CPU/RAM y no ofrecer garantías de disponibilidad. No deben tratarse como infraestructura de producción crítica. Revisa las condiciones y límites vigentes de Render y Neon antes de almacenar datos importantes.

## Recuperación y seguridad

- Mantén copias de seguridad independientes de PostgreSQL.
- Rota el token si se expone.
- No habilites CORS con comodines para un panel autenticado.
- No publiques la base de datos directamente en Internet.
- Antes de almacenar datos personales o sensibles, añade autenticación por usuario, autorización por tenant y auditoría; el token global actual no sustituye esos controles.
