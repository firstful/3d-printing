#!/usr/bin/env bash
# Re-slice the committed 3MF headlessly and report filament/time.
# usage: ./slice.sh [output-dir]        (default: build/slices)
set -euo pipefail
cd "$(dirname "$0")"

out="${1:-build/slices}"
bambu="${BAMBU:-$HOME/Applications/BambuStudio.AppImage}"

mkdir -p "$out"
"$bambu" --slice 1 --outputdir "$out" ramp_half_hex.3mf >/dev/null 2>&1 \
  || { echo "SLICE FAILED (see $out)"; exit 1; }

python3 - "$out/result.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
p = d["sliced_plates"][0]
print(f"{p['filaments'][0]['total_used_g']:7.1f} g   "
      f"{p['sliced_time']/3600:5.2f} h   {d['error_string']}")
PY
