# ADR 0001: separar borradores de tareas comprometidas

- **Estado:** aceptada
- **Fecha:** 2026-08-12

## Contexto

Las personas suelen formular trabajo de manera progresiva. Una solicitud puede
llegar sin responsable, fecha, criterio de aceptación o evidencia esperada. Crear
una tarea operativa en ese momento produce compromisos ambiguos, recordatorios
injustificados y estados difíciles de auditar.

El esquema actual permite algunos de esos campos incompletos. La especificación
funcional ya distingue propuestas progresivas de efectos confirmados.

## Decisión

Una solicitud incompleta se representa como **borrador**. El borrador:

- puede completarse en varios turnos;
- pertenece al actor y contexto correctos;
- no produce efectos operativos;
- puede modificarse, vencer o cancelarse;
- no aparece como tarea comprometida ni activa recordatorios.

Sólo puede convertirse en **tarea comprometida** cuando contiene:

1. objetivo al que contribuye;
2. responsable;
3. fecha objetivo;
4. criterio de aceptación;
5. política de evidencia.

La conversión requiere una vista previa, confirmación explícita, revalidación del
estado vigente, ejecución única y auditoría. Confirmar un borrador obsoleto o ajeno
no crea una tarea.

## Consecuencias

- La captura conversacional puede seguir siendo flexible sin debilitar el dominio.
- Las tareas operativas dejan de representar pedidos incompletos.
- Recordatorios, aprobaciones y reportes pueden apoyarse en compromisos completos.
- Se necesita un ciclo de vida propio para borradores y pruebas de vencimiento,
  modificación, cancelación, concurrencia e idempotencia.
- La migración de datos existentes deberá identificar tareas incompletas antes de
  endurecer restricciones; su estrategia se decidirá al implementar.

## Fuera de alcance

- Diseñar una UI administrativa completa.
- Crear un motor genérico de workflows.
- Permitir que el modelo complete campos faltantes por inferencia.
- Definir aquí taxonomías personalizadas de estados o evidencias.
- Resolver la política de autoridad, privacidad o escalamiento específica del piloto.
