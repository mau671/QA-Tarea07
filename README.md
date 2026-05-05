# QA tarea 07

Laboratorio de pruebas de integración para Claustrum usando Supabase REST API, Postman, Pytest, Requests y SQLite en memoria.

## Flujo evaluado

El flujo probado es la consulta de catálogo académico y el guardado de horarios. Este flujo funciona como equivalente a un carrito:

| Carrito | Claustrum |
|---|---|
| Productos disponibles | Cursos y grupos disponibles |
| Agregar al carrito | Seleccionar grupos |
| Consultar carrito | Consultar horario guardado |
| Calcular total | Calcular cursos, créditos y horas |
| Checkout | Guardar horario |
| Eliminar carrito | Eliminar horario guardado |

## Estructura

```text
.
├── docs/
│   ├── matriz_casos_prueba.md
│   ├── metricas_resultados.md
│   └── reporte_final.md
├── evidencias/
│   ├── newman/
│   └── pytest/
├── postman/
│   ├── Integracion_Claustrum_Horarios.postman_collection.json
│   └── QA_API_LAB.postman_environment.json
├── scripts/
│   └── run_postman.sh
├── tests/
│   └── test_api_integration.py
├── .env.example
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md
```

## Artefactos entregables

| Artefacto | Ubicación | Descripción |
|---|---|---|
| Matriz de casos de prueba | `docs/matriz_casos_prueba.md` | Contiene los casos diseñados antes de la ejecución, con objetivo, endpoint, datos de entrada, pasos, resultado esperado, validación y métrica asociada. |
| Métricas y resultados | `docs/metricas_resultados.md` | Resume métricas obligatorias: porcentaje de aprobación, tiempo de respuesta, cobertura, validaciones por endpoint, tasa de error y defectos encontrados. |
| Reporte final | `docs/reporte_final.md` | Documenta el proyecto evaluado, alcance, adaptación del carrito, datos de prueba, herramientas, resultados, hallazgos y conclusiones. |
| Colección de Postman | `postman/Integracion_Claustrum_Horarios.postman_collection.json` | Colección exportada con requests, variables dinámicas, scripts y aserciones del flujo de integración. |
| Environment de Postman | `postman/QA_API_LAB.postman_environment.json` | Environment exportado sin contraseña real. La variable `claustrum_pass` debe configurarse localmente. |
| Pruebas automatizadas | `tests/test_api_integration.py` | Suite Pytest con consumo de Supabase REST API, validación de contrato, pruebas negativas y SQLite en memoria. |
| Evidencia Pytest | `evidencias/pytest/resultados.txt` | Salida de ejecución de Pytest. |
| Evidencia Newman | `evidencias/newman/resultados-20260505-173726.txt` | Reporte de consola generado con Newman, runner oficial de línea de comandos de Postman. |
| Script de Newman | `scripts/run_postman.sh` | Automatiza 3 iteraciones de la colección Postman y guarda evidencia de ejecución. |

## Requisitos

- Python 3.13 o superior
- uv
- Postman opcional para ejecutar la colección manualmente
- Newman, runner oficial de línea de comandos de Postman, para ejecutar la colección desde consola y generar evidencia

## Instalación

```bash
uv sync
```

## Variables de entorno

Crear un archivo local `.env` a partir de `.env.example` o exportar las variables antes de ejecutar Pytest.

```bash
export SUPABASE_URL="https://jxzkhfclcdpcgtkpyxyk.supabase.co"
export SUPABASE_PUBLISHABLE_KEY="sb_publishable_t7JXv-4WbCOOsO4kruTOog_9fJ6fboa"
export CLAUSTRUM_EMAIL="pruebas@maugp.com"
export CLAUSTRUM_PASS="<password-de-pruebas>"
```

La contraseña no se incluye en archivos versionados. En Postman debe configurarse como Current Value de `claustrum_pass`.

## Datos de prueba

```text
university=1
campus=3
career=10
plan=48
term=101
```

## Ejecutar Pytest

Pytest ejecuta las pruebas automatizadas en Python contra Supabase REST API y usa SQLite en memoria para validar persistencia temporal del flujo.

```bash
uv run pytest -v
```

Guardar evidencia:

```bash
uv run pytest -v | tee evidencias/pytest/resultados.txt
```

## Ejecutar Postman

La colección de Postman contiene las pruebas de integración del flujo completo: autenticación, catálogo académico, consulta de cursos, guardado de horario, consulta, eliminación y pruebas negativas.

Importar en Postman:

- `postman/Integracion_Claustrum_Horarios.postman_collection.json`
- `postman/QA_API_LAB.postman_environment.json`

Antes de ejecutar:

- Seleccionar environment `QA_API_LAB`.
- Colocar la contraseña de pruebas como Current Value de `claustrum_pass`.
- Ejecutar la colección completa desde Collection Runner.
- Usar al menos 3 iteraciones.

## Ejecutar Newman

Newman es la herramienta oficial de línea de comandos de Postman. Se usa para automatizar la ejecución de la colección sin abrir la interfaz gráfica y para generar el reporte/evidencia de ejecución solicitado por el laboratorio.

Ejecutar la colección con Newman:

```bash
export CLAUSTRUM_PASS="<password-de-pruebas>"
scripts/run_postman.sh
```

El script ejecuta la colección 3 veces y guarda la evidencia en `evidencias/newman/` con este formato de nombre:

- `resultados-YYYYMMDD-HHMMSS.txt`

No se genera reporte JSON porque Newman incluye valores resueltos de variables de entorno y podría exponer la contraseña de pruebas.

## Evidencias incluidas

Este repositorio ya incluye evidencia generada:

- `evidencias/pytest/resultados.txt`: ejecución de Pytest.
- `evidencias/newman/resultados-20260505-173726.txt`: ejecución de Newman con 3 iteraciones.

Resultado actual de Pytest:

```text
9 passed in 10.09s
```

Resultado actual de Newman:

```text
iterations: 3
requests: 45
assertions: 135
failed: 0
```

## Dependencias principales

- requests: consumo de Supabase REST API.
- pytest: automatización de pruebas de integración.
- sqlite3: persistencia temporal en memoria incluida en Python.
