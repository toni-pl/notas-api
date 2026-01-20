# Notas API

API REST con interfaz web para gestionar notas personales. Desarrollada con Flask y MariaDB, desplegada con Docker Compose.

## Descripción

Aplicación web que permite crear, listar y eliminar notas. Incluye:

- **API REST** con 3 endpoints (crear, listar, borrar)
- **Interfaz web** moderna e interactiva
- **Base de datos** MariaDB con persistencia
- **Logs** en formato JSON
- **Configuración** mediante variables de entorno

## Arquitectura
```
┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │
│   Flask App     │◄───────►│    MariaDB      │
│   (Puerto 5000) │         │   (Puerto 3306) │
│                 │         │                 │
└─────────────────┘         └─────────────────┘
        │                           │
        │                           │
   notas-network              datos-mariadb
   (red interna)                (volumen)
```

## Requisitos

- Docker (v20.10 o superior)
- Docker Compose (v2.0 o superior)

## Instalación y ejecución

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd notas-api
```

### 2. Levantar la aplicación
```bash
docker compose up --build
```

### 3. Acceder a la aplicación

Abre el navegador en: **http://localhost:5000**

### 4. Parar la aplicación
```bash
docker compose down
```

Para parar y eliminar los volúmenes (borra los datos):
```bash
docker compose down -v
```

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Interfaz web |
| GET | `/notas` | Lista todas las notas |
| POST | `/notas` | Crea una nueva nota |
| DELETE | `/notas/<id>` | Elimina una nota por ID |
| GET | `/health` | Estado de la aplicación |

### Ejemplos con curl

**Crear una nota:**
```bash
curl -X POST http://localhost:5000/notas \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Mi nota", "contenido": "Contenido de ejemplo"}'
```

**Listar notas:**
```bash
curl http://localhost:5000/notas
```

**Borrar una nota:**
```bash
curl -X DELETE http://localhost:5000/notas/1
```

## Configuración

La aplicación se configura mediante variables de entorno:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DB_HOST` | Host de la base de datos | `localhost` |
| `DB_PORT` | Puerto de la base de datos | `3306` |
| `DB_USER` | Usuario de la base de datos | `root` |
| `DB_PASSWORD` | Contraseña de la base de datos | `secret` |
| `DB_NAME` | Nombre de la base de datos | `notasdb` |

Estas variables deben configurarse en un fichero `.env` (no versionado) o exportarse en el entorno.
En el repositorio hay un `.env.example` con placeholders.

Para crear el fichero `.env` a partir del ejemplo:
```bash
cp .env.example .env
```

## Estructura del proyecto
```
notas-api/
├── app.py                 # Aplicación Flask
├── requirements.txt       # Dependencias Python
├── Dockerfile            # Construcción de imagen (Multistage)
├── docker-compose.yml    # Orquestación de servicios
├── .gitignore           # Archivos ignorados por Git
└── README.md            # Este archivo
```

## Dockerfile (Multistage)

El Dockerfile utiliza construcción en múltiples etapas:

1. **Fase builder**: Instala dependencias en imagen completa
2. **Fase final**: Copia solo lo necesario a imagen slim

Esto reduce el tamaño de la imagen final (~80MB vs ~500MB).

## Logs

Los logs se emiten por STDOUT en formato JSON:
```json
{"timestamp": "2026-01-19 15:07:34", "level": "INFO", "message": "Nota creada con ID: 1"}
```

Para ver los logs:
```bash
docker logs notas-app
```

Para ver los logs de la base de datos:
```bash
docker logs notas-db
```

## Verificación del funcionamiento

1. **Aplicación corriendo:**
```bash
   curl http://localhost:5000/health
   # Respuesta: {"status": "ok"}
```

2. **Persistencia de datos:**
   - Crear una nota
   - Parar con `docker compose down`
   - Volver a levantar con `docker compose up`
   - La nota debe seguir ahí

3. **Logs funcionando:**
```bash
   docker logs notas-app | grep "level"
```

## Autor

Antonio Prado Lorenzo - KeepCoding DevOps Bootcamp (Módulo Docker)
