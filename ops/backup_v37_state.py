#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, timezone
import tempfile
import subprocess
import hashlib
import json
import shutil
import tarfile
import time
import sys


ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = Path.home() / "trading_project" / "quantum_backups"
STATE_DIR = ROOT / "paper_trading_30d"

STATE_FILES = [
    "positions.json",
    "trades.json",
    "portfolio.json",
]

CODE_FILES = [
    "autonomous_trading_bot_improved.py",
    "position_risk_manager.py",
    "snapshot_manager.py",
    "telegram_notifier.py",
]

OPS_FILES = [
    "ops/bot_control.sh",
    "ops/bot_watchdog.sh",
]


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def git_value(*args):
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def acquire_consistent_state():
    journal = STATE_DIR / "transaction_pending.json"

    for attempt in range(1, 11):
        if journal.exists():
            print(
                f"⏳ Tentativo {attempt}: "
                "transaction_pending presente"
            )
            time.sleep(0.5)
            continue

        try:
            first = {
                name: (STATE_DIR / name).read_bytes()
                for name in STATE_FILES
            }
        except Exception as exc:
            print(
                f"⏳ Tentativo {attempt}: "
                f"lettura fallita: {exc}"
            )
            time.sleep(0.5)
            continue

        if journal.exists():
            print(
                f"⏳ Tentativo {attempt}: "
                "journal apparso durante acquisizione"
            )
            time.sleep(0.5)
            continue

        try:
            second = {
                name: (STATE_DIR / name).read_bytes()
                for name in STATE_FILES
            }
        except Exception as exc:
            print(
                f"⏳ Tentativo {attempt}: "
                f"seconda lettura fallita: {exc}"
            )
            time.sleep(0.5)
            continue

        if journal.exists():
            print(
                f"⏳ Tentativo {attempt}: "
                "journal apparso dopo acquisizione"
            )
            time.sleep(0.5)
            continue

        if all(first[name] == second[name] for name in STATE_FILES):
            print(f"✅ Stato stabile acquisito al tentativo {attempt}")
            return first

        print(
            f"⏳ Tentativo {attempt}: "
            "stato cambiato durante acquisizione"
        )
        time.sleep(0.5)

    raise RuntimeError(
        "Impossibile acquisire uno stato V37 consistente"
    )


def validate_state(captured):
    positions = json.loads(captured["positions.json"])
    trades = json.loads(captured["trades.json"])
    portfolio = json.loads(captured["portfolio.json"])

    if not isinstance(positions, dict):
        raise TypeError("positions.json non è un dict")

    if not isinstance(trades, list):
        raise TypeError("trades.json non è una lista")

    if not isinstance(portfolio, dict):
        raise TypeError("portfolio.json non è un dict")

    return positions, trades, portfolio


def main():
    print("=== V37 B22b BACKUP ===")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    captured = acquire_consistent_state()
    positions, trades, portfolio = validate_state(captured)

    timestamp = datetime.now().astimezone().strftime(
        "%Y%m%d_%H%M%S"
    )

    archive = (
        BACKUP_DIR /
        f"V37_STATE_{timestamp}.tar.gz"
    )

    checksum_file = Path(str(archive) + ".sha256")

    with tempfile.TemporaryDirectory(dir=BACKUP_DIR) as tmp_dir:
        tmp = Path(tmp_dir)
        snap = tmp / "V37_STATE"

        state_out = snap / "state"
        code_out = snap / "code"
        ops_out = snap / "ops"
        diag_out = snap / "diagnostics"

        state_out.mkdir(parents=True)
        code_out.mkdir(parents=True)
        ops_out.mkdir(parents=True)
        diag_out.mkdir(parents=True)

        for name, data in captured.items():
            (state_out / name).write_bytes(data)

        for rel in CODE_FILES:
            src = ROOT / rel

            if not src.exists():
                raise FileNotFoundError(
                    f"File codice richiesto assente: {rel}"
                )

            shutil.copy2(src, code_out / src.name)

        for rel in OPS_FILES:
            src = ROOT / rel

            if not src.exists():
                raise FileNotFoundError(
                    f"File operativo richiesto assente: {rel}"
                )

            shutil.copy2(src, ops_out / src.name)

        last_cycle = ROOT / "last_cycle.txt"

        if last_cycle.exists():
            shutil.copy2(
                last_cycle,
                diag_out / "last_cycle.txt"
            )

        readme = snap / "README_RESTORE.txt"
        readme.write_text(
            "Quantum V37 operational state backup\n"
            "\n"
            "Contiene:\n"
            "  state/positions.json\n"
            "  state/trades.json\n"
            "  state/portfolio.json\n"
            "  code/\n"
            "  ops/\n"
            "  manifest.json\n"
            "\n"
            "transaction_pending.json era ASSENTE\n"
            "durante l'acquisizione.\n"
            "\n"
            ".env e credenziali NON sono incluse.\n"
            "\n"
            "Non ripristinare automaticamente mentre\n"
            "V37 è in esecuzione.\n"
        )

        files = {}

        for p in sorted(snap.rglob("*")):
            if p.is_file() and p.name != "manifest.json":
                rel = str(p.relative_to(snap))

                files[rel] = {
                    "size": p.stat().st_size,
                    "sha256": sha256_file(p),
                }

        manifest = {
            "backup_type": "V37_OPERATIONAL_STATE",
            "created_local": (
                datetime.now().astimezone().isoformat()
            ),
            "created_utc": (
                datetime.now(timezone.utc).isoformat()
            ),
            "git_commit": git_value("rev-parse", "HEAD"),
            "git_branch": git_value(
                "rev-parse",
                "--abbrev-ref",
                "HEAD",
            ),
            "state": {
                "positions": len(positions),
                "trades": len(trades),
                "capital": portfolio.get("capital"),
                "initial_capital": (
                    portfolio.get("initial_capital")
                ),
                "transaction_pending": False,
            },
            "files": files,
        }

        (snap / "manifest.json").write_text(
            json.dumps(
                manifest,
                indent=2,
                ensure_ascii=False,
            )
        )

        with tarfile.open(archive, "w:gz") as tf:
            tf.add(
                snap,
                arcname="V37_STATE",
            )

    print("=== VERIFICA ARCHIVIO ===")

    with tarfile.open(archive, "r:gz") as tf:
        manifest_data = json.loads(
            tf.extractfile(
                tf.getmember(
                    "V37_STATE/manifest.json"
                )
            ).read().decode()
        )

        for rel, meta in manifest_data["files"].items():
            data = tf.extractfile(
                tf.getmember(
                    f"V37_STATE/{rel}"
                )
            ).read()

            if sha256_bytes(data) != meta["sha256"]:
                raise RuntimeError(
                    f"Hash interno errato: {rel}"
                )

        for name in STATE_FILES:
            data = tf.extractfile(
                tf.getmember(
                    f"V37_STATE/state/{name}"
                )
            ).read()

            json.loads(data)

    archive_hash = sha256_file(archive)

    checksum_file.write_text(
        f"{archive_hash}  {archive.name}\n"
    )

    print("✅ Archivio leggibile")
    print("✅ Hash interni verificati")
    print("✅ JSON stato validi")
    print("✅ transaction_pending assente")
    print()
    print("=== BACKUP COMPLETATO ===")
    print("Archivio :", archive)
    print("SHA256   :", archive_hash)
    print("Posizioni:", len(positions))
    print("Trade    :", len(trades))
    print("Capitale :", portfolio.get("capital"))
    print("Commit   :", git_value("rev-parse", "HEAD"))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"❌ BACKUP FALLITO: {exc}", file=sys.stderr)
        sys.exit(1)
