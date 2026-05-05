# Métricas y resultados

## Métricas definidas

| Métrica | Cálculo | Criterio | Resultado esperado |
|---|---|---|---|
| Porcentaje de casos aprobados | Casos aprobados / total de casos x 100 | Mayor o igual a 85% | 100% en Pytest: 9/9 casos aprobados |
| Tiempo de respuesta | Milisegundos por endpoint crítico | Menor a 5000 ms | Validado en Postman y Pytest |
| Cobertura de endpoints | Endpoints probados / endpoints del flujo | Mayor o igual a 80% | Catálogo, horarios, guardado, consulta y eliminación |
| Validaciones por endpoint | Assertions por request | Mínimo 3 en endpoints importantes | Estado HTTP, contrato y regla de negocio |
| Tasa de error controlado | Errores esperados / pruebas negativas | 100% de negativos controlados | Sin auth, nombre vacío y grupo inexistente |
| Defectos encontrados | Hallazgos funcionales o técnicos | Registrar severidad | Guardado parcial documentado como riesgo |

## Flujo evaluado

El flujo representa un carrito académico:

- Catálogo: cursos y grupos disponibles.
- Selección: grupos elegidos por el estudiante.
- Carrito: horario temporal seleccionado.
- Persistencia: horario guardado en Supabase.
- Total: cantidad de cursos, créditos y horas semanales.
- Checkout equivalente: guardar horario.

## Resultados Pytest

Ejecucion realizada:

```text
9 passed in 10.09s
```

Evidencia guardada en `evidencias/pytest/resultados.txt`.

La evidencia debe generarse con:

```bash
uv run pytest -v | tee evidencias/pytest/resultados.txt
```

Casos automatizados en `tests/test_api_integration.py`:

- Contrato del catálogo académico.
- Contrato y tiempo de respuesta de cursos/grupos.
- Inserción temporal en SQLite.
- Cálculo de totales de cursos, créditos y horas.
- Guardado de horario autenticado.
- Consulta de grupos guardados.
- Eliminacion de horario.
- Negativos de autenticación, nombre vacío y grupo inexistente.
- Documentación del comportamiento de guardado parcial.

## Resultados Postman

La colección `postman/Integracion_Claustrum_Horarios.postman_collection.json` valida:

- Login con Supabase Auth.
- Consulta de catálogo.
- Consulta de cursos disponibles.
- Guardado, consulta y eliminación de horario.
- Pruebas negativas.

Se ejecutaron 3 iteraciones con Newman y la evidencia quedó en `evidencias/newman/resultados-20260505-173726.txt`.

Resultado Newman:

```text
iterations: 3
requests: 45
assertions: 135
failed: 0
average response time: 229ms
```

No se conserva reporte JSON porque expone valores resueltos de variables secretas.

## Hallazgos

| Severidad | Hallazgo | Impacto | Recomendación |
|---|---|---|---|
| Media | Si se envía un grupo válido y otro inválido, `save_user_schedule` guarda el válido e ignora el inválido. | El usuario podría creer que guardó todo el horario cuando solo se persistió una parte. | Validar que todos los grupos solicitados existan antes de insertar, o devolver advertencia con rechazados. |
| Baja | La carga de horarios depende de que los grupos sigan disponibles en el filtro actual. | Un horario antiguo podría cargarse incompleto si cambian los datos activos. | Mostrar mensaje con cantidad de grupos recuperados contra cantidad esperada. |
