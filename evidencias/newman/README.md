# Evidencia Newman

Ejecutar la automatizacion completa con:

```bash
export CLAUSTRUM_PASS="<password-de-pruebas>"
scripts/run_postman.sh
```

El script ejecuta 3 iteraciones y genera evidencia CLI en `.txt`.

No se guarda reporte JSON porque Newman puede incluir valores resueltos de variables secretas en el archivo exportado.
