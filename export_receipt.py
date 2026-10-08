#!/usr/bin/env python3
"""Compare a source memory-unit snapshot with a Hindsight bank export ZIP."""

from __future__ import annotations

import argparse
import io
import json
import sys
import zipfile
from pathlib import Path

TEXT = {
    "en": {"title": "Memory export receipt", "ok": "All captured observations are present in the archive", "missing": "Observations are absent from the archive", "unexpected": "The archive contains observations absent from the source snapshot", "orphaned_status": "The archive is complete, but some source observations cite missing units", "inconclusive": "Observation IDs are unavailable for a reliable comparison", "orphaned": "Observations with missing source units", "count": "Source / exported / missing", "invalid": "Invalid source snapshot or bank archive", "note": "This compares one source snapshot and one archive; changes between captures can affect the result."},
    "fr": {"title": "Reçu d’export mémoire", "ok": "Toutes les observations capturées sont présentes dans l’archive", "missing": "Des observations sont absentes de l’archive", "unexpected": "L’archive contient des observations absentes de l’instantané source", "orphaned_status": "L’archive est complète, mais des observations sources citent des unités absentes", "inconclusive": "Les ID d’observations manquent pour une comparaison fiable", "orphaned": "Observations dont des unités sources manquent", "count": "Source / exportées / absentes", "invalid": "Instantané source ou archive de banque invalide", "note": "Ce contrôle compare un instantané et une archive ; des changements entre les captures peuvent modifier le résultat."},
    "es": {"title": "Comprobante de exportación de memoria", "ok": "Todas las observaciones capturadas están en el archivo", "missing": "Faltan observaciones en el archivo", "unexpected": "El archivo contiene observaciones ausentes de la instantánea de origen", "orphaned_status": "El archivo está completo, pero algunas observaciones de origen citan unidades ausentes", "inconclusive": "Faltan ID de observación para una comparación fiable", "orphaned": "Observaciones con unidades de origen ausentes", "count": "Origen / exportadas / ausentes", "invalid": "Instantánea de origen o archivo de banco no válido", "note": "Esta comprobación compara una instantánea y un archivo; los cambios entre capturas pueden alterar el resultado."},
}
MAX_JSON_ENTRY = 25_000_000


def source_snapshot(value: dict):
    if not isinstance(value, dict) or not isinstance(value.get("memory_units"), list):
        raise ValueError("source shape")
    units = value["memory_units"]
    identifiers = set()
    observations = {}
    for row in units:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            raise ValueError("unit shape")
        identifier = row["id"]
        if identifier in identifiers:
            raise ValueError("duplicate source ID")
        identifiers.add(identifier)
        if row.get("fact_type") == "observation":
            sources = row.get("source_memory_ids", [])
            if not isinstance(sources, list) or not all(isinstance(s, str) for s in sources):
                raise ValueError("source IDs shape")
            observations[identifier] = sources
    bank = value.get("bank_id")
    if bank is not None and not isinstance(bank, str):
        raise ValueError("bank shape")
    return identifiers, observations, bank


def archive_json(archive: zipfile.ZipFile, name: str, required: bool = True):
    entries = [item for item in archive.infolist() if item.filename == name]
    if not entries:
        if required:
            raise ValueError("archive entry missing")
        return None
    if len(entries) != 1 or entries[0].file_size > MAX_JSON_ENTRY:
        raise ValueError("archive entry invalid")
    return json.loads(archive.read(entries[0]))


def read_archive(path: Path):
    with zipfile.ZipFile(path) as archive:
        manifest = archive_json(archive, "manifest.json")
        observations = archive_json(archive, "observations.json", required=False)
    if not isinstance(manifest, dict) or manifest.get("archive_type") != "bank":
        raise ValueError("whole-bank archive required")
    if observations is None:
        observations = []
    if not isinstance(observations, list) or not isinstance(manifest.get("observation_count"), int):
        raise ValueError("archive observation shape")
    if manifest["observation_count"] != len(observations):
        raise ValueError("archive observation count")
    return manifest, observations


def audit(source: dict, manifest: dict, exported: list) -> dict:
    identifiers, source_observations, bank = source_snapshot(source)
    if bank is not None and bank != manifest.get("source_bank_id"):
        raise ValueError("bank mismatch")
    if not isinstance(exported, list) or manifest.get("observation_count") != len(exported):
        raise ValueError("archive count mismatch")
    exported_ids = []
    for row in exported:
        if not isinstance(row, dict):
            raise ValueError("observation shape")
        identifier = row.get("source_id")
        if not isinstance(identifier, str) or not identifier:
            return {"status": "inconclusive", "source_count": len(source_observations),
                    "exported_count": len(exported), "missing_ids": [], "orphaned_source_ids": [],
                    "note_code": "archive_source_ids_unavailable"}
        exported_ids.append(identifier)
    if len(exported_ids) != len(set(exported_ids)):
        raise ValueError("duplicate exported ID")
    missing = sorted(set(source_observations) - set(exported_ids))
    unexpected = sorted(set(exported_ids) - set(source_observations))
    orphaned = sorted(identifier for identifier, sources in source_observations.items()
                      if any(source_id not in identifiers for source_id in sources))
    return {"status": "missing" if missing else "unexpected" if unexpected else "orphaned" if orphaned else "ok",
            "source_count": len(source_observations), "exported_count": len(exported),
            "missing_ids": missing, "unexpected_export_ids": unexpected,
            "orphaned_source_ids": orphaned,
            "missing_and_orphaned_ids": sorted(set(missing) & set(orphaned)),
            "note_code": "source_snapshot_and_bank_archive_only"}


def demo() -> dict:
    """Exercise the real archive reader using a synthetic in-memory bank ZIP."""
    source = {"bank_id": "demo-bank", "memory_units": [
        {"id": "fact-1", "fact_type": "world"},
        {"id": "obs-1", "fact_type": "observation", "source_memory_ids": ["fact-1"]},
        {"id": "obs-2", "fact_type": "observation", "source_memory_ids": ["deleted-fact"]},
    ]}
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("manifest.json", json.dumps({"archive_type": "bank", "source_bank_id": "demo-bank", "observation_count": 1}))
        archive.writestr("observations.json", json.dumps([{"source_id": "obs-1", "text": "synthetic"}]))
    buffer.seek(0)
    with zipfile.ZipFile(buffer) as archive:
        manifest = archive_json(archive, "manifest.json")
        exported = archive_json(archive, "observations.json")
    return audit(source, manifest, exported)


def render(report: dict, lang: str) -> str:
    words = TEXT[lang]
    return "\n".join([
        words["title"], words[{"ok": "ok", "missing": "missing", "unexpected": "unexpected", "orphaned": "orphaned_status", "inconclusive": "inconclusive"}[report["status"]]],
        f"{words['count']}: {report['source_count']} / {report['exported_count']} / {len(report['missing_ids'])}",
        f"{words['orphaned']}: {len(report['orphaned_source_ids'])}", words["note"]])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("demo", "check"))
    parser.add_argument("--source", type=Path)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--lang", choices=TEXT, default="en")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            report = demo()
        else:
            if args.source is None or args.archive is None:
                raise ValueError("missing arguments")
            if args.source.stat().st_size > MAX_JSON_ENTRY:
                raise ValueError("source file too large")
            source = json.loads(args.source.read_text(encoding="utf-8"))
            manifest, exported = read_archive(args.archive)
            report = audit(source, manifest, exported)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError, zipfile.BadZipFile):
        print(TEXT[args.lang]["invalid"], file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report, args.lang))
    if args.command == "demo":
        return 0 if report["missing_ids"] == ["obs-2"] and report["orphaned_source_ids"] == ["obs-2"] else 1
    return {"ok": 0, "missing": 2, "unexpected": 2, "orphaned": 2, "inconclusive": 3}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
