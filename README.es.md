# memory-transfer-test

## Nuevo: comprobante de exportación de Hindsight

**« Algunas observaciones recuperables desaparecieron de mi exportación de memoria. »** [Hindsight #5419](https://github.com/vectorize-io/hindsight/issues/5419) describe observaciones con fuentes borradas que se omiten en `export-bank`. `export_receipt.py` compara los ID de una instantánea de origen con los campos `source_id` de `observations.json` en un archivo de banco Hindsight. También señala observaciones cuyos `source_memory_ids` faltan. No modifica ningún banco.

```sh
python3 export_receipt.py demo --lang es
psql -v ON_ERROR_STOP=1 -v bank_id=mi-banco -Atf examples/export-receipt/source-snapshot.sql > source.json
hindsight-admin export-bank --bank mi-banco --output banco.zip
python3 export_receipt.py check --source source.json --archive banco.zip --lang es
```

La demo sintética muestra dos observaciones de origen: una exportada y otra ausente con una fuente huérfana. La comprobación real lee un archivo **del banco completo** y una instantánea JSON del mismo banco; exporte justo después de la captura, preferiblemente sin escrituras simultáneas. El SQL de solo lectura supone que `memory_units` está disponible en su `search_path`. Mantenga la instantánea y el archivo en local porque contienen datos del banco. Código 0: coincide; 2: observación ausente o fuente huérfana; 3: comparación imposible sin ID; 1: entrada no válida. El comprobante no demuestra la causa de la omisión ni la calidad de una importación posterior.

**Proyectos relacionados:** [Hindsight #5419](https://github.com/vectorize-io/hindsight/issues/5419) motiva la comparación; [Hindsight](https://github.com/vectorize-io/hindsight) define el formato del archivo. Esta herramienta independiente lee los ZIP de `export-bank`, sin afiliación ni integración con una instancia activa.

## Nueva comprobación: citas tras una migración

`python3 citation_migration.py demo --lang es` muestra en diez segundos una página que aún cita `old-1` tras migrar a `new-1` (la demo correcta sale con código 0). Para exportaciones normalizadas: `python3 citation_migration.py check source.json destination.json remap.json --lang es`. Ambas exportaciones contienen `records: [{id}]` y `pages: [{id, based_on: [id]}]`; `remap.json` relaciona ID antiguos y nuevos. Detecta destinos ausentes, citas obsoletas y huérfanas. No consulta ningún almacén y depende del mapa proporcionado.

**Proyecto relacionado:** [Hindsight #5298](https://github.com/vectorize-io/hindsight/issues/5298) describe citas `based_on` que conservan el ID de origen tras una importación fusionada. Este CLI comprueba el síntoma en exportaciones; no incluye adaptador directo para Hindsight.

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
