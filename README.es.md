# memory-transfer-test

[Français](README.md) · [English](README.en.md) · [Español](README.es.md)

## Proyectos relacionados y carencia abordada

- [MemMachine](https://github.com/MemMachine/MemMachine) ofrece memoria persistente para agentes. Una migración hacia o desde ese tipo de almacén debe conservar correcciones, eliminaciones, ámbitos y procedencias.
- [Agent Memory Benchmark](https://github.com/AlekseiMarchenko/agent-memory-benchmark) ya prueba recuperación, conflictos y olvido selectivo entre proveedores. Hay **solapamiento** en esos comportamientos. Nuestro MVP aborda el caso distinto de **migración origen → destino**, comparando dos exportaciones del mismo estado.
- **Nuestro enfoque:** verificar invariantes de transferencia antes del cambio. Aún no se incluye un adaptador para MemMachine ni otros proveedores.

Comprueba que una migración de memoria de agente conserve los hechos activos, sus ámbitos y procedencias, sin resucitar recuerdos corregidos o eliminados. Compara dos exportaciones JSON normalizadas y ejecuta pruebas de recuperación por ámbito y término.

## Inicio rápido

Python 3.11+, sin dependencias externas.

```bash
python3 memory_transfer.py examples/source.json examples/destination-ok.json examples/probes.json
python3 memory_transfer.py examples/source.json examples/destination-bug.json examples/probes.json
python3 -m unittest discover -s tests -v
```

La primera orden pasa. La segunda sale con código `2`: detecta un hecho corregido reaparecido, uno eliminado reaparecido y un ámbito cambiado. `--output report.json` guarda el informe. Cada registro tiene `id`, `text`, `scope`, `provenance`, con `status` y `supersedes` opcionales. Una prueba tiene `scope` y `term`.

## Ejemplo: límite de alcance

`python3 -m examples.scope_boundary` compara una migración correcta con una copia en la que el mismo recuerdo cambia de alcance. La segunda también falla en las sondas de recuperación por equipo. Las exportaciones son sintéticas; no se consulta ningún almacén real.

## Alcance

El MVP compara exportaciones normalizadas, no API de proveedores ni calidad de búsqueda vectorial. La recuperación utiliza una búsqueda de términos exactos limitada por ámbito. Escribe adaptadores de exportación para los dos almacenes y revisa el informe antes de borrar el origen.


Licencia MIT. Se aceptan adaptadores para almacenes.
