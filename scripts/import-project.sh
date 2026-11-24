#!/usr/bin/env bash
# Import (or refresh) a 3D print project from a working directory into this repo.
#
# usage: scripts/import-project.sh <source-dir> [dest-name] [--mirror]
#
#   <source-dir>  usually ~/opencode-sessions/<project>
#   [dest-name]   repo directory name, defaults to the source basename
#   --mirror      also delete files in the destination that no longer exist in
#                 the source (refuses to delete a hand-written README.md)
#
# Excludes build/slicing output, extracted 3MF trees, envs and large
# intermediates. It never touches files outside <source-dir> and this repo.
set -euo pipefail

die() { printf 'error: %s\n' "$*" >&2; exit 1; }

src="${1:-}"
[ -n "$src" ] || die "usage: scripts/import-project.sh <source-dir> [dest-name] [--mirror]"
shift
mirror=0
dest_name=""
for arg in "$@"; do
  case "$arg" in
    --mirror) mirror=1 ;;
    -*) die "unknown option: $arg" ;;
    *) dest_name="$arg" ;;
  esac
done

[ -d "$src" ] || die "source directory not found: $src"
src="$(cd "$src" && pwd)"
root="$(cd "$(dirname "$0")/.." && pwd)"
[ "$src" != "$root" ] || die "source is the repository itself"
case "$src/" in
  "$root"/*) die "source is already inside the repository: $src" ;;
esac

dest_name="${dest_name:-$(basename "$src")}"
dest="$root/$dest_name"
mkdir -p "$dest"

excludes=(
  --exclude '.git/'
  --exclude '.venv/'
  --exclude '__pycache__/'
  --exclude '*.pyc'
  # build / slicing output
  --exclude 'build/'
  --exclude '*.gcode'
  --exclude '*.gcode.3mf'
  --exclude '*.bak'
  --exclude '*.3mf.bak'
  # large regenerable intermediates
  --exclude '*.npy'
  --exclude '*.npz'
  --exclude '*.tar.gz'
  --exclude '*.AppImage'
  # extracted 3MF trees and make_3mf temp dir
  --exclude 'project/'
  --exclude 'preview/*.stl'
  --exclude 'preview_light/*.stl'
)

rsync_args=(-a --info=stats2 "${excludes[@]}")
# The committed README is usually richer than the working copy's. Never clobber
# it on refresh; delete it by hand first if the working copy's is authoritative.
if [ -f "$dest/README.md" ]; then
  rsync_args+=(--exclude 'README.md')
  printf 'note: keeping existing %s/README.md (delete it first to import the source copy)\n' "$dest_name"
fi
if [ "$mirror" -eq 1 ]; then
  rsync_args+=(--delete)
fi

printf 'importing %s -> %s\n\n' "$src" "$dest"
rsync "${rsync_args[@]}" "$src/" "$dest/"

# Flag the things the exclude list cannot guess.
if find "$dest" -maxdepth 2 -type d \( -name 3D -o -name Metadata -o -name _rels -o -name Auxiliaries \) -print -quit | grep -q .; then
  printf '\nwarning: extracted 3MF tree left in %s — re-zip it and delete the tree\n' "$dest_name"
fi
if find "$dest" -maxdepth 3 -type f \( -name '*.gcode.3mf' -o -name '*.gcode' \) -print -quit | grep -q .; then
  printf 'warning: g-code found under %s\n' "$dest_name"
fi

printf '\nnext:\n'
printf '  1. write %s/README.md (what it is, print orientation, rebuild command,\n' "$dest_name"
printf '     provenance, safety note)\n'
printf '  2. add or update its row in README.md\n'
printf '  3. git add %s && git commit -m "%s: import project"\n' "$dest_name" "$dest_name"
