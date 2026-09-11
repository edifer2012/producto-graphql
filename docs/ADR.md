# Registro de decisiones arquitectónicas

Estado de las decisiones: adoptadas en la implementación inicial; publicación y prueba completa de infraestructura pendientes.

## ADR-001 · Backend modular y tres contenedores

**Contexto.** Se requiere un CRUD de producto con separación de responsabilidades y despliegue reproducible.

**Decisión.** Un backend modular, un servidor web con cliente estático y PostgreSQL independiente. Los tres forman una sola solución desplegada por Compose.

**Consecuencias.** Se pueden construir y actualizar las imágenes por separado. No se introduce complejidad de transacciones distribuidas. Se mantiene un solo punto de fallo por servicio: no hay alta disponibilidad.

## ADR-002 · FastAPI y Strawberry como adaptadores de entrada

**Contexto.** El trabajo anterior organiza persistencia y casos de uso con servicio y repositorio.

**Decisión.** Mantener esa estructura y publicar el CRUD mediante tipos, queries y mutations de Strawberry, registrado con `GraphQLRouter`.

**Consecuencias.** El servicio puede ser invocado desde otro adaptador sin HTTP interno. No hay router REST de productos en este proyecto; añadirlo posteriormente no exige duplicar reglas. Se documenta la dependencia del servicio con SQLAlchemy y no se describe la solución como hexagonal pura.

## ADR-003 · Sesión por resolver en el thread pool

**Contexto.** SQLAlchemy síncrono requiere cuidado con el event loop y con las sesiones compartidas entre hilos.

**Decisión.** Mantener una fábrica de sesiones en contexto. Abrir y cerrar una sesión por resolver dentro de `run_in_threadpool`, incluyendo la conversión a tipos de respuesta.

**Consecuencias.** Las queries concurrentes no comparten una `Session`. Cada mutation tiene su transacción; la atomicidad no abarca todo un documento GraphQL. El tamaño de pool y de thread pool debe dimensionarse si aumenta la carga.

## ADR-004 · Valores monetarios y concurrencia

**Contexto.** Los precios necesitan precisión decimal y la interfaz puede ser usada desde varias pestañas.

**Decisión.** Precio `Decimal`/`NUMERIC(12,2)`/string JSON. Actualización y eliminación exigen `version`, respaldada por `version_id_col` de SQLAlchemy.

**Consecuencias.** Se detectan modificaciones obsoletas y se evita redondeo binario. El consumidor debe conservar la versión. No hay detección de duplicados ni idempotencia en creación; las mutations no se reintentan automáticamente.

## ADR-005 · Cliente ligero y mismo origen

**Contexto.** El alcance es un solo CRUD y se exige una aplicación web moderna en un tercer contenedor.

**Decisión.** Cliente de una página con HTML semántico, CSS adaptable y JavaScript modular. Nginx entrega los archivos y reenvía `/graphql`.

**Consecuencias.** No hay instalación npm ni bundler obligatorios para desplegar, y se reduce la superficie de dependencias. El cliente separa transporte, operaciones, validación y UI. No ofrece tipado estático TypeScript ni caché normalizada Apollo; si la aplicación crece, se revisará esta decisión. El navegador no conoce la red privada Docker.

## ADR-006 · Migraciones y dependencias bloqueadas

**Contexto.** El esquema y las bibliotecas deben poder evolucionar de forma revisable.

**Decisión.** Alembic versiona los cambios SQL. Docker instala lockfiles con hashes. Las migraciones se ejecutan al iniciar la única réplica de API de esta configuración.

**Consecuencias.** Los cambios de modelo requieren migración. Si se escala a varias réplicas, las migraciones deben ejecutarse una sola vez en un job controlado. Los tags de imagen siguen siendo mutables: fijar digest es una tarea explícita antes de producción.
