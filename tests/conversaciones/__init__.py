"""Las conversaciones de prueba y su corredor.

Cada conversación tiene su fuente en Markdown (`NN-*.md`, el formato está en `README.md`) y, al
lado, su YAML con lo que se comprueba solo. El corredor (`correr.py`, `corredor.py` y lo que
usan) las corre por el código de verdad contra una IA guionada, una grabada o una real, y deja
el informe de cada ronda en `resultados/`. Vino de la prueba chica en la E3-8, para que la
regresión sobreviviera a su borrado (2026-10-07).
"""
