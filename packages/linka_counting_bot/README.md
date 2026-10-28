# Linka counting bot scaffold

An installable home for the existing unfinished counting bot. No gameplay loop is implemented.

```sh
uv run linka-counting-bot --init-db /absolute/path/to/counting.db
```

This initializes the original `config` table only. Imports do not open or create databases. The shared bot SDK is declared as a dependency for continued development. The original sketch is retained in `examples/legacy_counting.py` for reference, not as an executable example.
