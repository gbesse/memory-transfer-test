# memory-transfer-test

[Français](README.md) · [English](README.en.md) · [Español](README.es.md)

Comprueba que una migración de memoria de agente conserve los hechos activos, sus ámbitos y procedencias, sin resucitar recuerdos corregidos o eliminados. Compara dos exportaciones JSON normalizadas y ejecuta pruebas de recuperación por ámbito y término.

## Inicio rápido

Python 3.11+, sin dependencias externas.

```bash
python3 memory_transfer.py examples/source.json examples/destination-ok.json examples/probes.json
python3 memory_transfer.py examples/source.json examples/destination-bug.json examples/probes.json
python3 -m unittest discover -s tests -v
```

La primera orden pasa. La segunda sale con código `2`: detecta un hecho corregido reaparecido, uno eliminado reaparecido y un ámbito cambiado. `--output report.json` guarda el informe. Cada registro tiene `id`, `text`, `scope`, `provenance`, con `status` y `supersedes` opcionales. Una prueba tiene `scope` y `term`.

## Alcance

El MVP compara exportaciones normalizadas, no API de proveedores ni calidad de búsqueda vectorial. La recuperación utiliza una búsqueda de términos exactos limitada por ámbito. Escribe adaptadores de exportación para los dos almacenes y revisa el informe antes de borrar el origen.

Señales: [MemMachine](https://github.com/MemMachine/MemMachine) y [agent-memory-benchmark](https://github.com/AlekseiMarchenko/agent-memory-benchmark).

Licencia MIT. Se aceptan adaptadores para almacenes.
