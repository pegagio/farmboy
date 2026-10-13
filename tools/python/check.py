"""Check the project Python, PyYAML, and virtual environment contract."""

from pathlib import Path
import sys

expected_python = "3.11.16"
expected_pyyaml = "6.0.3"
expected_prefix = (Path.cwd() / ".venv").resolve()
actual_python = ".".join(str(part) for part in sys.version_info[:3])
actual_prefix = Path(sys.prefix).resolve()
print(f"python:check: interpreter={sys.executable}; prefix={sys.prefix}; Python={actual_python}")
try:
    import yaml
    sample = {"items": ["one", 2], "enabled": True}
    assert yaml.safe_load(yaml.safe_dump(sample)) == sample
except Exception as exc:
    print(f"python:check: PyYAML import or safe YAML round-trip failed: {exc}", file=sys.stderr)
    print("Inspect .venv; after approving repair, install requirements into that environment.", file=sys.stderr)
    raise SystemExit(1)

if actual_python != expected_python:
    print(f"python:check: expected Python {expected_python}, found {actual_python}.", file=sys.stderr)
    raise SystemExit(1)
if actual_prefix != expected_prefix:
    print(f"python:check: expected project prefix {expected_prefix}, found {actual_prefix}.", file=sys.stderr)
    raise SystemExit(1)
if yaml.__version__ != expected_pyyaml:
    print(f"python:check: expected PyYAML {expected_pyyaml}, found {yaml.__version__}.", file=sys.stderr)
    raise SystemExit(1)

print(f"python:check: ready; executable={sys.executable}; prefix={sys.prefix}; Python={actual_python}; PyYAML={yaml.__version__}")
