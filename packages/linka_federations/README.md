# Linka federation SDK

Distribution: `linkaFederations`. Import: `linka_federations`. Requires Python 3.12+.

```python
from linka_federations import LinkaFederations

client = LinkaFederations(db_path="/absolute/path/to/slug-cache.db")
client.actual_server = "http://127.0.0.1:5000"
```

The client provides slug caching, `resolve_target`, `receiveConnection`, and `sendPayload`. Construction initializes the selected SQLite cache; importing the package has no filesystem or network effects. Supply an explicit cache path to avoid state in the current working directory.

The backend retains a separate internal federation helper with signed requests. This public SDK retains its existing handshake behavior; packaging does not make the two protocols interchangeable.

Develop from the workspace with `uv sync --all-packages --frozen`. See [contributor instructions](../../CONTRIBUTING.md).
