# Operación y mantenimiento

## Arranque y diagnóstico

```bash
docker compose config --quiet
docker compose up -d --build --wait
docker compose ps
docker compose logs --tail=100 api
```

Requisitos de salud:

| Comprobación | Qué demuestra | Qué no demuestra |
| --- | --- | --- |
| PostgreSQL `pg_isready` | Servidor acepta conexiones | Contraseña de aplicación, migraciones o integridad de datos |
| API `/health/live` | Proceso atiende HTTP | Acceso a PostgreSQL |
| API `/health/ready` | Conexión y `SELECT 1` | Existencia/compatibilidad de todas las tablas |
| Nginx `/healthz` | Servidor web atiende | Que API o DB estén disponibles |
| Smoke CRUD | Recorrido completo sobre un registro temporal | Carga, HA, seguridad completa o recuperación ante desastres |

La API usa `pool_pre_ping`. Un proceso puede seguir vivo aunque la DB esté caída. `restart: unless-stopped` reinicia por terminación del proceso, no simplemente por un estado `unhealthy`.

## Migraciones

En desarrollo, desde `backend` con dependencias instaladas y acceso a la base de desarrollo:

```bash
alembic revision --autogenerate -m "describir cambio de esquema"
```

Revisar manualmente el archivo generado, especialmente alteraciones destructivas, valores por defecto, índices, restricciones y compatibilidad con datos existentes. No convertir `--autogenerate` en aprobación automática.

Con la nueva imagen preparada:

```bash
docker compose run --rm --no-deps --entrypoint alembic api upgrade head
docker compose up -d --build api
```

Para un despliegue con varias réplicas se debe cambiar el entrypoint: migrar una vez antes del rollout. Nunca permitir que varias réplicas compitan por aplicar migraciones. No aplicar `downgrade` sobre datos reales sin revisar impacto y disponer de backup verificado.

## Backup

Desde la raíz del repositorio, con la DB en ejecución:

```bash
mkdir -p backups
backup_path="backups/productos-$(date -u +%Y%m%dT%H%M%SZ).dump"
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$backup_path"
test -s "$backup_path"
```

El dump contiene datos del catálogo y nombres de propietarios; no contiene la definición de contraseñas de los roles. Protegerlo, copiarlo fuera del host y establecer retención. `test -s` solo verifica que hay bytes: no valida que una restauración sea exitosa.

## Prueba de restauración

Usar una base nueva aislada; los siguientes comandos no apuntan a la base productiva. Sustituir `RUTA_DEL_BACKUP` por un backup confirmado.

```bash
docker compose exec db createdb -U postgres productos_restore_test
docker compose exec -T db pg_restore --exit-on-error --no-owner --no-acl \
  -U postgres -d productos_restore_test < RUTA_DEL_BACKUP
docker compose exec db psql -U postgres -d productos_restore_test \
  -c 'SELECT count(*) FROM productos;'
```

Si la base de restauración ya existe, detenerse y elegir otra base vacía; no sobrescribirla. Después de validar conteos, una muestra de registros y reglas de integridad, registrar la duración y el resultado. No se incluye un comando de eliminación automática de la base restaurada.

RPO y RTO no están garantizados por este Compose. Deben definirse y medirse, junto con la frecuencia de backup y el procedimiento de recuperación de roles.

## Fallos frecuentes

| Síntoma | Revisión |
| --- | --- |
| Puerto 8080 ocupado | Cambiar `WEB_PORT` en `.env` |
| GraphiQL no abre | Verificar `GRAPHQL_IDE`, conectividad de sus recursos y utilizar cliente/curl |
| HTTP 400 al hacer GET | Las queries se envían por POST con documento GraphQL |
| HTTP 200 con `errors` | Leer `extensions.code`; no considerar éxito solo por HTTP |
| `CONFLICT` | Refrescar y revisar la versión, no forzar sobrescritura |
| API no inicia | Logs de migración, credenciales y permisos del esquema |
| Cambié la clave en `.env` y falla | `.env` no cambia roles de un volumen existente; rotar el rol en PostgreSQL |
| `NOT_FOUND` al editar | El registro pudo eliminarse desde otra pestaña |
| El navegador no resuelve `api` | El navegador debe llamar a `/graphql`, no al hostname Docker |
| Código no cambia en Compose base | Reconstruir; utilizar override de desarrollo para montaje y recarga |
| HTTP 429 | Límite por IP; esperar y revisar ráfagas, no quitarlo sin evaluar carga |
| Timeout guardando | Puede existir commit; consultar estado antes de repetir la mutation |

## Preparación para producción

Lista pendiente, no una declaración de capacidades ya implementadas:

- [ ] Autenticación OIDC/JWT y autorización por rol en operaciones y datos.
- [ ] TLS en Nginx o ingress externo; cookies y CSRF si se usa autenticación basada en cookies.
- [ ] GraphiQL deshabilitado y política de introspección definida; ocultarlo no reemplaza autorización.
- [ ] Secretos administrados y rotación de credenciales sin recrear el volumen.
- [ ] Separación de credenciales de migración y de ejecución (runtime sin DDL).
- [ ] Imágenes por digest y revisión de vulnerabilidades/SBOM/licencias.
- [ ] Escaneo de secretos y protección de rama con revisiones obligatorias.
- [ ] Métricas, alertas y trazabilidad distribuida si aparecen servicios adicionales.
- [ ] Auditoría funcional de cambios con actor, antes/después y retención.
- [ ] Backup fuera del host, restauración probada y RPO/RTO medidos.
- [ ] Pruebas de carga, timeout SQL y límites por costo ajustados a requisitos.
- [ ] Idempotencia de escrituras si hay colas, reenvíos o clientes no confiables.
- [ ] Revisión de accesibilidad en navegador, teclado, móvil y ampliación al 200%.
- [ ] Disponibilidad y escalamiento definidos con métricas, no por cantidad de contenedores.
