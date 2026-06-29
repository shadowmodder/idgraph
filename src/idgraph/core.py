"""Cluster accounts that share signals (email, device, document, ...) — pure stdlib."""
from __future__ import annotations
from collections import defaultdict


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:          # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


class IdentityGraph:
    """Accounts linked when they share any (field, value) signal."""

    def __init__(self):
        self.accounts = {}                       # account_id -> {field: value}
        self.signal_index = defaultdict(set)     # (field, value) -> {account_id}

    def add_account(self, account_id, signals):
        self.accounts[account_id] = dict(signals)
        for field, value in signals.items():
            if value is None:
                continue
            self.signal_index[(field, str(value))].add(account_id)
        return self

    def _components(self):
        uf = UnionFind()
        for acc in self.accounts:
            uf.find(acc)
        for accts in self.signal_index.values():
            accts = list(accts)
            for other in accts[1:]:
                uf.union(accts[0], other)
        groups = defaultdict(set)
        for acc in self.accounts:
            groups[uf.find(acc)].add(acc)
        return list(groups.values())

    def clusters(self):
        return [set(c) for c in self._components()]

    def shared_signals(self, accounts):
        accounts = set(accounts)
        out = defaultdict(set)
        for (field, value), accts in self.signal_index.items():
            if len(accts & accounts) >= 2:
                out[field].add(value)
        return {f: sorted(v) for f, v in out.items()}

    def find_rings(self, min_size=3):
        """Connected components of >= min_size, with the signals that bind them."""
        rings = []
        for c in self.clusters():
            if len(c) >= min_size:
                rings.append({"accounts": sorted(c), "size": len(c),
                              "shared_signals": self.shared_signals(c)})
        rings.sort(key=lambda r: -r["size"])
        return rings
