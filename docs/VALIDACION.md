# Evidencia de validación de la entrega

Resultados obtenidos en el entorno de preparación. No se sustituyen por ellos las validaciones pendientes de Docker o PostgreSQL.

| Comprobación | Resultado |
| --- | --- |
| Resolución e instalación de dependencias Python con hashes | Completada |
| Construcción del esquema Strawberry por importación | Correcta; 2 queries y 3 mutations |
| Pruebas backend rápidas | 20 aprobadas |
| Pruebas PostgreSQL | 2 omitidas porque no hay servidor de pruebas disponible |
| Cobertura backend medida | 97%; excluye `app/main.py` |
| Ruff y formato Python | Aprobados |
| Pruebas del cliente ejecutadas con Node | 7 aprobadas |
| Sintaxis de los cuatro módulos JavaScript | Correcta |
| Referencias estáticas de IDs de interfaz y assets | Correctas; no reemplaza prueba en navegador |
| Sintaxis YAML y scripts shell | Correcta |
| Migración y comparación Alembic en SQLite temporal | Correctas; sin diferencias de modelo pendientes |
| Arranque completo de Docker Compose | No ejecutado; Docker no está disponible en este entorno |
| Verificación de la configuración mediante Docker y de Nginx en runtime | Pendiente; prevista en CI |
| Aplicación de migración contra PostgreSQL | Pendiente; prevista en CI |
| Interacción visual/end-to-end en navegador | No ejecutada |
| Carga, seguridad ofensiva, backups y restauración | No ejecutadas |
| Creación/publicación remota en GitHub | Pendiente de acceso autorizado a la cuenta |

Los tests rápidos usan SQLite temporal y pruebas HTTP con TestClient. Hay avisos de deprecación en dependencias del cliente de pruebas (Starlette/HTTPX y AnyIO); no son fallos de los tests, pero deben revisarse al actualizar los lockfiles. No se han silenciado para ocultarlos.

Los tests frontend cubren normalización decimal, validación, variables GraphQL, errores en HTTP 200, límite HTTP 429 y respuesta vacía. No equivalen a comprobar visualmente formularios ni todos los navegadores.

La CI incluida añade un servicio PostgreSQL de pruebas y un job que construye y arranca la solución real. Sus resultados solo se podrán afirmar tras ejecutarla en el repositorio.
