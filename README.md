# memory-transfer-test

## Nouvelle vérification : citations après migration

`python3 citation_migration.py demo --lang fr` montre en dix secondes une page qui cite encore `old-1` après transfert vers `new-1` (démo réussie : code 0). Pour vos exports normalisés : `python3 citation_migration.py check source.json destination.json remap.json --lang fr`. Les deux exports contiennent `records: [{id}]` et `pages: [{id, based_on: [id]}]`; `remap.json` associe ancien et nouvel ID. Le contrôle repère les cibles absentes, citations périmées et orphelines. Il ne contacte aucun magasin et dépend de la table de correspondance fournie.

**Projet voisin :** [Hindsight #5298](https://github.com/vectorize-io/hindsight/issues/5298) décrit précisément des citations `based_on` conservant l’ID source après un import fusionné. Ce CLI traite ce symptôme sur des exports ; aucune intégration Hindsight directe n’est incluse.

[Français](README.md) · [English](README.en.md) · [Español](README.es.md)

## Projets voisins et lacune visée

- [MemMachine](https://github.com/MemMachine/MemMachine) fournit une mémoire persistante pour agents. Un passage vers ou depuis ce type de magasin doit conserver les corrections, suppressions, portées et provenances.
- [Agent Memory Benchmark](https://github.com/AlekseiMarchenko/agent-memory-benchmark) teste déjà le rappel, les conflits et l'oubli sélectif chez les fournisseurs. Il y a **recouvrement** sur ces comportements. Notre MVP cible le cas différent d'une **migration source → destination**, en comparant deux exports du même état.
- **Notre angle :** vérifier des invariants de transfert avant bascule. Aucun adaptateur MemMachine ou fournisseur n'est encore inclus.

Vérifie qu'une migration de mémoire d'agent conserve les faits actifs, leurs portées et leurs provenances, sans ressusciter les souvenirs corrigés ou supprimés. Compare deux exports JSON normalisés et exécute des sondes de récupération par portée et terme.

## Démarrage

Python 3.11+, sans dépendance externe.

```bash
python3 memory_transfer.py examples/source.json examples/destination-ok.json examples/probes.json
python3 memory_transfer.py examples/source.json examples/destination-bug.json examples/probes.json
python3 -m unittest discover -s tests -v
```

La première commande passe. La seconde sort `2` : elle détecte un fait corrigé réapparu, un fait supprimé réapparu et une portée modifiée. `--output report.json` enregistre le rapport. Chaque enregistrement a `id`, `text`, `scope`, `provenance`, avec `status` et `supersedes` optionnels. Une sonde a `scope` et `term`.

## Exemple : frontière de portée

`python3 -m examples.scope_boundary` compare une migration correcte à une copie où le même souvenir change de portée. La seconde échoue aussi aux sondes de récupération par équipe. Les exports sont synthétiques ; aucun magasin réel n’est interrogé.

## Périmètre

Le MVP compare des exports normalisés, pas les API des fournisseurs ni la qualité de recherche vectorielle. La récupération de sonde est une recherche de terme exact sensible à la portée. Écrivez un adaptateur d'export pour vos deux magasins, puis contrôlez le rapport avant de supprimer la source.


Licence MIT. Adaptateurs de magasins bienvenus.
