# MEMORA AI — despliegue con Docker

## Arquitectura

- FastAPI + Uvicorn para API y dashboard estático.
- PostgreSQL 16 para persistencia.
- SQLAlchemy 2 y Alembic para esquema versionado.
- Docker Compose para API y base de datos en red privada.
- Contenedor API con usuario no privilegiado; PostgreSQL sin puerto publicado al host.
- Healthchecks para API y PostgreSQL.

## Arranque

1. Instala Docker Engine y Docker Compose v2.
2. Copia `.env.example` a `.env`.
3. Genera dos secretos fuertes e independientes, por ejemplo con `openssl rand -hex 32`.
4. Completa `POSTGRES_PASSWORD` y `MEMORA_API_TOKEN` en `.env`.
5. Ejecuta `docker compose up -d --build`.
6. Comprueba `curl http://127.0.0.1:8000/api/health`.
7. Publica el servicio detrás de un proxy HTTPS (Caddy, Traefik o balanceador gestionado). No expongas la API directamente a Internet sin TLS.

La API escucha solo en loopback del host. El proxy inverso debe ejecutarse en el mismo host y reenviar a `127.0.0.1:8000`. Configura `MEMORA_ALLOWED_ORIGINS` solo si el dashboard se sirve desde otro origen.

## Migraciones y persistencia

El contenedor ejecuta `alembic upgrade head` antes de iniciar Uvicorn. Las migraciones viven en `backend/migrations`. Crea migraciones nuevas y revisadas; no edites migraciones ya aplicadas.

Los datos viven en el volumen Docker `memora_pgdata`. Programa backups externos cifrados con `pg_dump` y ensaya restauraciones. Un volumen no sustituye un backup. No ejecutes `docker compose down -v` en producción.

## Límites que impiden certificar producción multiusuario

Esta versión conserva un token bearer compartido. Todavía no implementa cuentas, OAuth/OIDC, separación de datos por usuario/organización, rotación automatizada de credenciales, auditoría completa, límites de abuso, restauración automatizada ni resolución de conflictos multi-dispositivo. La recuperación es léxica, no vectorial/semántica. El grafo es una visualización de relaciones de datos, no una red neuronal entrenada. Antes de ofrecer el servicio a terceros, implementar identidad/tenancy y realizar revisión de seguridad y pruebas de carga.
