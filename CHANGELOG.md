Changelog
=========

All notable changes to this project will be documented in this file.

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

