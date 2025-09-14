Changelog
=========

All notable changes to this project will be documented in this file.

v0.4.0 - 2025-09-14
-------------------
- Add `--script` (`-s`) option to write a runnable shell script containing the generated FFmpeg commands
- Script includes shebang and `set -euo pipefail`; commands are not executed automatically
- Commands stream to the script alongside CSV output as files are processed

v0.3.0 - 2025-09-14
-------------------
- Single ffprobe call (JSON) to obtain both video codec and audio channel count
- Optional concurrency via `--jobs` to parallelize metadata probing (default up to CPU count, capped at 32)
- Explicit FFmpeg stream mapping (`-map 0:v:0`, `-map 0:a:0?`) and `-an` when no audio
- Continue streaming CSV writing during processing

v0.2.1 - 2025-09-14
-------------------
- Faster file discovery using a single directory walk and suffix filtering
- Robust FFmpeg command quoting that safely handles single quotes in paths
- Avoid unnecessary ffprobe calls for files already using good codecs
- Stream CSV writing during processing to reduce memory usage on large sets
- Safer default Opus bitrate (128k) when audio channel count is unknown
- Update Python requirement to 3.10+

v0.2.0 - 2025-09-13
-------------------
- Python packaging, CLI entry point, and test suite
- Config via env and YAML
- Initial codec check and FFmpeg command generation
v0.5.0 - 2025-09-14
-------------------
- Add `scripts/convert_template.sh` to execute a file of FFmpeg commands with logging and optional dry-run
- Ignore generated conversion CSV outputs in `.gitignore` (e.g., `*_conversions.csv`)
- Remove previously tracked generated CSV from repository
