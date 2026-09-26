# memory-transfer-test

[Français](README.md) · [English](README.en.md) · [Español](README.es.md)

Vérifie qu'une migration de mémoire d'agent conserve les faits actifs, leurs portées et leurs provenances, sans ressusciter les souvenirs corrigés ou supprimés. Compare deux exports JSON normalisés et exécute des sondes de récupération par portée et terme.

## Démarrage

Python 3.11+, sans dépendance externe.

```bash
python3 memory_transfer.py examples/source.json examples/destination-ok.json examples/probes.json
python3 memory_transfer.py examples/source.json examples/destination-bug.json examples/probes.json
python3 -m unittest discover -s tests -v
```

La première commande passe. La seconde sort `2` : elle détecte un fait corrigé réapparu, un fait supprimé réapparu et une portée modifiée. `--output report.json` enregistre le rapport. Chaque enregistrement a `id`, `text`, `scope`, `provenance`, avec `status` et `supersedes` optionnels. Une sonde a `scope` et `term`.

## Périmètre

Le MVP compare des exports normalisés, pas les API des fournisseurs ni la qualité de recherche vectorielle. La récupération de sonde est une recherche de terme exact sensible à la portée. Écrivez un adaptateur d'export pour vos deux magasins, puis contrôlez le rapport avant de supprimer la source.

Signaux : [MemMachine](https://github.com/MemMachine/MemMachine) et [agent-memory-benchmark](https://github.com/AlekseiMarchenko/agent-memory-benchmark).

Licence MIT. Adaptateurs de magasins bienvenus.
