# Reporte final

## Proyecto evaluado

El proyecto evaluado es Claustrum, una plataforma académica para estudiantes del Instituto Tecnológico de Costa Rica. El flujo seleccionado es la consulta de cursos/grupos y el guardado de horarios mediante Supabase REST API y funciones RPC.

## Alcance

Se probaron servicios de:

- Catálogo académico.
- Campus, carreras y planes.
- Periodos académicos.
- Cursos y grupos disponibles.
- Guardado de horarios.
- Consulta de horarios guardados.
- Eliminacion de horarios.
- Manejo de errores y autenticación.

## Adaptación del carrito

El laboratorio solicita un flujo similar a compra o carrito. En Claustrum, el equivalente es el horario guardado:

| Carrito de compras | Claustrum |
|---|---|
| Productos disponibles | Cursos y grupos disponibles |
| Agregar al carrito | Seleccionar grupos |
| Consultar carrito | Consultar horario guardado |
| Calcular total | Calcular cursos, créditos y horas |
| Checkout | Guardar horario |
| Eliminar carrito | Eliminar horario guardado |

## Datos de prueba

| Campo | Valor |
|---|---|
| Universidad | 1 |
| Campus | 3 |
| Carrera | 10 |
| Plan | 48 |
| Periodo | 101 |
| Usuario | Cuenta de pruebas configurada en variables de entorno |

## Herramientas

- Postman para ejecución manual y validación de requests.
- Supabase REST API para consumo de tablas, vistas y RPCs.
- Python con `requests` para automatizacion.
- Pytest para ejecución de pruebas.
- SQLite en memoria para persistencia temporal aislada.
- uv para gestión del entorno Python.

## Pruebas ejecutadas

| Area | Pruebas |
|---|---|
| Catálogo | Universidad, campus, carreras, planes y periodos |
| Horarios | Cursos disponibles, grupos, contrato y tiempo de respuesta |
| Persistencia | Guardar, consultar y eliminar horario |
| SQLite | Insertar selección temporal y calcular totales |
| Negativas | Sin autenticación, nombre vacío, grupo inexistente |
| Riesgo | Guardado parcial con grupos válidos e inválidos |

## Resultado automatizado

La suite Pytest se ejecutó correctamente contra Supabase usando la cuenta de pruebas.

```text
9 passed in 10.09s
```

La evidencia está en `evidencias/pytest/resultados.txt`.

La colección Postman se ejecutó automáticamente con Newman durante 3 iteraciones.

```text
iterations: 3
requests: 45
assertions: 135
failed: 0
average response time: 229ms
```

La evidencia está en `evidencias/newman/resultados-20260505-173726.txt`. La contraseña de la cuenta de pruebas no se guarda en el environment exportado ni en reportes JSON.

## Defectos y riesgos

| Severidad | Descripción | Evidencia | Recomendación |
|---|---|---|---|
| Media | El RPC `save_user_schedule` permite guardado parcial cuando el payload mezcla grupos válidos e inválidos. | Caso automatizado `test_partial_invalid_groups_are_saved_as_current_behavior`. | Rechazar toda la solicitud si algún grupo no existe o devolver detalle de grupos omitidos. |
| Baja | Un horario puede cargarse incompleto si alguno de sus grupos ya no está disponible en el filtro actual. | Revisión de flujo de carga en Claustrum. | Informar grupos faltantes al usuario. |

## Conclusiones

- Una prueba de API aislada valida un endpoint individual; una prueba de integración valida la continuidad entre catálogo, selección, persistencia y consulta.
- Probar solo la interfaz gráfica podría ocultar errores de contrato, RLS, permisos, persistencia parcial y manejo de payloads inválidos.
- Las validaciones más importantes fueron contrato JSON, reglas de negocio y persistencia, porque el flujo depende de IDs y relaciones entre tablas.
- Integrar servicios externos sin pruebas automatizadas aumenta el riesgo de cambios de contrato, fallos de autenticación y errores de datos no detectados.
- Para producción se recomienda agregar pruebas automatizadas en CI, datos semilla controlados y validaciones más estrictas en `save_user_schedule`.
