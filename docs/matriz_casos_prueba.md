# Matriz de casos de prueba

Flujo evaluado: integración de servicios API para consulta de catálogo académico y guardado de horarios en Claustrum mediante Supabase REST API y RPC.

| ID | Caso | Endpoint/acción | Datos de entrada | Pasos | Resultado esperado | Validación | Métrica |
|---|---|---|---|---|---|---|---|
| TC-01 | Consultar universidad | `GET /rest/v1/v_universities` | `university_id=1` | Enviar request con `select=id,name,short_name` e id filtrado | Respuesta 200 con universidad ITCR | Estado HTTP, lista no vacía, campos `id`, `name`, `short_name` | Tiempo de respuesta |
| TC-02 | Consultar campus por universidad | `POST /rest/v1/rpc/get_campuses_for_university` | `p_university_id=1` | Ejecutar RPC de campus | Respuesta 200 y contiene campus 3 | Estado HTTP, contrato, regla de negocio | Cobertura de flujo |
| TC-03 | Consultar carreras por campus | `POST /rest/v1/rpc/get_academic_units_for_campus` | `p_campus_id=3` | Ejecutar RPC de unidades académicas | Respuesta 200 y contiene carrera 10 | Estado HTTP, contrato, datos esperados | Cobertura de flujo |
| TC-04 | Consultar planes por carrera | `POST /rest/v1/rpc/get_study_plans_for_academic_unit` | `p_academic_unit_id=10` | Ejecutar RPC de planes | Respuesta 200 y contiene plan 48 | Estado HTTP, contrato, datos esperados | Cobertura de flujo |
| TC-05 | Consultar períodos académicos | `POST /rest/v1/rpc/get_active_academic_terms` | `{}` | Ejecutar RPC de períodos | Respuesta 200 y contiene período 101 | Estado HTTP, lista no vacía, contrato | Cobertura de flujo |
| TC-06 | Consultar cursos y grupos disponibles | `POST /rest/v1/rpc/get_schedule_courses` | `campus=3`, `career=10`, `plan=48`, `term=101` | Ejecutar RPC de horarios | Respuesta 200 con cursos y grupos | Estado HTTP, contrato estricto, tiempo menor a 5000 ms | Tiempo promedio, validaciones por endpoint |
| TC-07 | Persistir selección temporal en SQLite | SQLite en memoria | Cursos/grupos de TC-06 | Insertar dos grupos seleccionados en tabla temporal | Registros insertados y totales calculados | Persistencia falsa, cantidad, créditos, horas | Total de cursos, créditos y horas |
| TC-08 | Guardar horario válido | `POST /rest/v1/rpc/save_user_schedule` | Token válido, nombre, term 101, grupos válidos | Ejecutar RPC autenticado | Respuesta 200 con `saved_schedule.id` | Estado HTTP, contrato, persistencia | Casos aprobados |
| TC-09 | Consultar horario guardado | `GET /rest/v1/saved_schedule` | `saved_schedule_id` | Consultar horario creado | Respuesta 200 con el horario del usuario | Estado HTTP, RLS, persistencia | Cobertura de endpoints |
| TC-10 | Consultar grupos del horario guardado | `POST /rest/v1/rpc/get_user_saved_schedule_group_lookups` | `saved_schedule_id` | Ejecutar RPC autenticado | Respuesta 200 con grupos guardados | Contrato `course_code`, `campus_id`, `group_code` | Validaciones por endpoint |
| TC-11 | Eliminar horario guardado | `DELETE /rest/v1/saved_schedule` | `saved_schedule_id` | Eliminar horario creado | Respuesta 200/204 y posterior consulta vacía | Estado HTTP, persistencia, cascada | Defectos encontrados |
| TC-12 | Guardar horario sin autenticación | `POST /rest/v1/rpc/save_user_schedule` | Sin access token | Ejecutar RPC con rol anon | Request rechazado | Estado HTTP 401/403/404, RLS | Tasa de error controlado |
| TC-13 | Guardar horario con nombre vacío | `POST /rest/v1/rpc/save_user_schedule` | Nombre en blanco | Ejecutar RPC autenticado | Respuesta 400 con error de nombre | Manejo de errores, regla de negocio | Defectos encontrados |
| TC-14 | Guardar horario con grupo inexistente | `POST /rest/v1/rpc/save_user_schedule` | Grupo `NOEXISTE999-ZZ` | Ejecutar RPC autenticado | Respuesta 400 con error de grupos válidos | Manejo de errores, regla de negocio | Defectos encontrados |
| TC-15 | Guardado parcial con grupo válido e inválido | `POST /rest/v1/rpc/save_user_schedule` | Un grupo válido y uno inválido | Ejecutar RPC autenticado y consultar items | Se guarda solo el grupo válido | Comportamiento observado, riesgo documentado | Hallazgo funcional |
