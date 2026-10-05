# La prueba chica del Motor

Código descartable de la Etapa 2 del Motor: prueba el diseño del ADR 0018 en el circuito del
recordatorio. El plan, las tareas y la evidencia están en `odd/tasks/prueba-chica-del-motor.md`.

**En la Etapa 3 esta carpeta se borra entera.** El motor de conversación definitivo se escribe
de nuevo en `src/leda`, con su propia prueba de frontera.

## Qué hay

- `turno.py`: un turno. Lee el estado de la persona, sus tareas y sus últimos turnos; le pide
  a la IA las jugadas; maneja cada una; le pide a la IA la respuesta desde los hechos; la encola
  y deja todo en el registro de turnos. Si la IA no responde, un reintento y después el único
  texto fijo, con un incidente para el administrador.
- `ia.py`: lo que el motor le pide a la IA y una IA guionada para las pruebas.
- `tiempo.py`: el reloj del motor. Los momentos los pone el motor, nunca la base.
- `test_frontera.py`: qué puede importar esta carpeta de `src/leda` y qué nunca debe alcanzar.

## Cómo se corren sus pruebas

Desde la raíz de la carpeta del Motor:

```
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider prueba_chica
```

La suite de siempre (`pytest` sin ruta) no las corre: sólo mira `tests/`. Usan una base
efímera en el servidor de `LEDA_TEST_DB_URL` (`.env.test`), que se crea y se borra en cada
corrida, y nunca leen el `.env` de la carpeta ni tocan `leda`, `leda_flujo` o `leda_motor`.
Sin esa variable, las pruebas que piden la base se saltean.
