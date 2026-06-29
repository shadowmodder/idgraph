# idgraph

Coordinated fraud and synthetic-identity rings show up as **accounts that quietly share signals** — the same device, document number, or email across "different" people. `idgraph` builds that linkage graph and clusters it with union-find, so you can spot rings at onboarding. Zero dependencies, pure stdlib.

## Install
```bash
pip install -e .
```

## Usage
```python
from idgraph import IdentityGraph

g = IdentityGraph()
g.add_account("a1", {"email": "x@e.com", "device": "D1", "doc": "P1"})
g.add_account("a2", {"email": "y@e.com", "device": "D1", "doc": "P2"})  # shares device with a1
g.add_account("a3", {"email": "y@e.com", "device": "D9", "doc": "P3"})  # shares email with a2

for ring in g.find_rings(min_size=3):
    print(ring["size"], ring["accounts"], ring["shared_signals"])
# 3 ['a1', 'a2', 'a3'] {'device': ['D1'], 'email': ['y@e.com']}
```

Returns the member accounts and the exact signals that bind each ring — useful as evidence for review queues. MIT licensed.
