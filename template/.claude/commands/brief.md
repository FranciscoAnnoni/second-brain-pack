Generá el brief del dia. Sin introduccion, sin fluff, directo al formato.

## Paso 0 — Sincronizar repo

Antes de leer cualquier archivo, corré un `git pull` para traer cambios de otros dispositivos.
Si falla (sin red, conflicto, etc.), continuá igual sin interrumpir el brief.

## Paso 1 — Leer fuentes

Leer en paralelo:
1. `pendientes.md` — fuente de verdad de tareas abiertas
2. El daily log mas reciente en `daily/` — para saber que se hizo en la ultima sesion

Para encontrar el daily mas reciente: listá los archivos en `daily/` y abrí el de fecha mas alta
que NO sea una reflexion automatica (ignorar los que empiezan con `reflection-`).

No leer otros archivos. No leer todos los dailys. Solo el mas reciente.

## Paso 2 — Armar el brief

El formato es ESTRICTAMENTE este, sin excepciones:

```
**[ ULTIMA SESION ]**
- que se hizo (del daily log, concreto, sin repetir todo el archivo)
- maximo 4-5 items, los mas importantes

**[ INMEDIATO ]**
- solo items con urgencia real o deadline de hoy
- si no hay ninguno, omitir esta seccion

**[ CATEGORIA ]**
- items de pendientes.md para esa categoria
```

Reglas de formato:
- Titulos SIEMPRE con corchetes: `**[ NOMBRE ]**`
- Un item por linea con `-`
- Sin sub-bullets, sin tablas, sin `---`, sin `##`
- Sin introduccion antes del primer bloque
- Solo mostrar categorias que tienen items activos
- Los items vienen de `pendientes.md` — no inventar, no agregar de memoria

## Paso 3 — Cerrar

Despues del ultimo bloque, una sola linea:

`Algo que falta tachar o agregar?`

## Comportamiento de mantenimiento

Cada vez que en la conversacion surja una tarea nueva, proyecto nuevo, o algo que queda pendiente:
- Agregarlo a `pendientes.md` en la categoria correcta (crearla si no existe)

Cada vez que se complete o cierre algo:
- Borrarlo de `pendientes.md`
- El registro del cierre queda en el daily log
