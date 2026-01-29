"""Snapshot Manager - Salvataggio atomico stato bot"""
import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SnapshotManager:
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("enabled", True)
        self.interval = config.get("interval_cycles", 10)
        self.directory = Path(config.get("directory", "./snapshots"))
        self.retention_days = config.get("retention_days", 30)
        self.version = config.get("version", "1.0")
        
        if self.enabled:
            self.directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"SnapshotManager inizializzato: {self.directory}")
    
    def save(self, state: Dict[str, Any], cycle: int) -> bool:
        if not self.enabled:
            return False
        
        try:
            snapshot = {
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "cycle": cycle,
                "state": state
            }
            
            filename = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.directory / filename
            tmp_filepath = self.directory / f"{filename}.tmp"
            
            with open(tmp_filepath, 'w') as f:
                json.dump(snapshot, f, indent=2)
            
            shutil.move(str(tmp_filepath), str(filepath))
            logger.info(f"✅ Snapshot salvato: {filename}")
            self._cleanup_old_snapshots()
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore salvataggio snapshot: {e}")
            if tmp_filepath.exists():
                tmp_filepath.unlink()
            return False
    
    def restore_latest(self) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None
        
        try:
            snapshots = sorted(
                self.directory.glob("snapshot_*.json"),
                key=os.path.getmtime,
                reverse=True
            )
            
            if not snapshots:
                return None
            
            for snapshot_file in snapshots:
                try:
                    with open(snapshot_file, 'r') as f:
                        snapshot = json.load(f)
                    
                    state = snapshot.get("state", {})
                    logger.info(f"✅ Snapshot recuperato: {snapshot_file.name}")
                    return state
                    
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore restore snapshot: {e}")
            return None
    
    def _cleanup_old_snapshots(self):
        try:
            cutoff = datetime.now() - timedelta(days=self.retention_days)
            
            for snapshot_file in self.directory.glob("snapshot_*.json"):
                file_time = datetime.fromtimestamp(os.path.getmtime(snapshot_file))
                if file_time < cutoff:
                    snapshot_file.unlink()
                    
        except Exception:
            pass
    
    def should_save(self, cycle: int) -> bool:
        return self.enabled and (cycle % self.interval == 0)


def init_snapshot_manager(config_path: str = "bot_improvements_config.json") -> SnapshotManager:
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return SnapshotManager(config["snapshot"])
    except Exception as e:
        logger.error(f"❌ Errore init snapshot manager: {e}")
        return SnapshotManager({"enabled": False})


def save_bot_state(snapshot_mgr, cycle, capital, positions, trailing_states, daily_pnl, **kwargs):
    if not snapshot_mgr.should_save(cycle):
        return False
    
    state = {
        "capital": capital,
        "positions": positions,
        "trailing_states": trailing_states,
        "daily_pnl": daily_pnl,
        **kwargs
    }
    
    return snapshot_mgr.save(state, cycle)


def restore_bot_state(snapshot_mgr) -> Optional[Dict[str, Any]]:
    return snapshot_mgr.restore_latest()
