import json
from pathlib import Path
from typing import Optional, Tuple
from src.utils import get_logger

logger = get_logger("datasheets")

class Datasheets:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.index = {}  # designation -> attrs map
        self._load()

    def _load(self):
        for fp in sorted(self.data_dir.glob("*.json")):
            try:
                obj = json.loads(fp.read_text(encoding="utf-8"))
                designation = obj.get("designation") or obj.get("title")
                if not designation:
                    continue
                key = designation.strip()
                if key not in self.index:
                    self.index[key] = {"attrs": {}, "sources": []}
                entry = self.index[key]
                # dimensions
                for d in obj.get("dimensions", []):
                    name = d.get("name","").strip().lower()
                    if name and "value" in d and d["value"] is not None:
                        val = d["value"]
                        if d.get("unit"):
                            entry["attrs"][name] = f"{val} {d['unit']}"
                        else:
                            entry["attrs"][name] = str(val)
                # properties, performance, logistics, specifications
                for section in ("properties","performance","logistics","specifications"):
                    for p in obj.get(section, []):
                        name = p.get("name","").strip().lower()
                        if name and "value" in p and p["value"] is not None:
                            val = p["value"]
                            if p.get("unit"):
                                entry["attrs"][name] = f"{val} {p['unit']}"
                            else:
                                entry["attrs"][name] = str(val)
                # some helpful aliases
                entry["attrs"].setdefault("designation", key)
                entry["sources"].append(str(fp))
            except Exception as e:
                logger.warning("failed load %s: %s", fp, e)

    def _normalize_attr_candidates(self, attr: str):
        a = attr.strip().lower()
        mapping = {
            "width": ["width","b"],
            "outside diameter": ["outside diameter","d","diameter"],
            "bore diameter": ["bore diameter","d","bore"],
            "product net weight": ["product net weight","weight","net weight"],
            "ean code": ["ean code","ean"],
        }
        # include direct lowercase attr and common keys
        candidates = [a]
        for k, vals in mapping.items():
            if a == k or a in vals or a in k:
                candidates = vals + [k] + candidates
        return list(dict.fromkeys(candidates))  # preserve order unique

    def lookup(self, designation: str, attribute: str) -> Tuple[Optional[str], Optional[str]]:
        # find entry
        entry = None
        if designation in self.index:
            entry = self.index[designation]
        else:
            for k in self.index:
                if k.lower() == designation.lower():
                    entry = self.index[k]
                    break
        if not entry:
            return None, None

        candidates = self._normalize_attr_candidates(attribute)
        # also try keys present in entry
        candidates += list(entry["attrs"].keys())
        for c in candidates:
            c_l = c.lower()
            if c_l in entry["attrs"]:
                return entry["attrs"][c_l], ",".join(entry["sources"])
        return None, None

datasheets = Datasheets()
