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

    def risk_score(self, accounts):
        """Heuristic ring risk 0–1: driven by cluster size and overlapping signal values."""
        accounts = set(accounts)
        if len(accounts) < 2:
            return 0.0
        shared = self.shared_signals(accounts)
        signal_count = sum(len(v) for v in shared.values())
        size_factor = min(len(accounts) / 20.0, 1.0)
        sig_factor = min(signal_count / 5.0, 1.0)
        return round((size_factor + sig_factor) / 2.0, 4)

    def edge_list(self):
        """Return (account_a, account_b, field, value) tuples for every shared signal pair."""
        edges = []
        for (field, value), accts in self.signal_index.items():
            accts = sorted(accts)
            for i in range(len(accts)):
                for j in range(i + 1, len(accts)):
                    edges.append((accts[i], accts[j], field, value))
        return edges

    def find_rings(self, min_size=3):
        """Connected components of >= min_size, with the signals that bind them."""
        rings = []
        for c in self.clusters():
            if len(c) >= min_size:
                rings.append({"accounts": sorted(c), "size": len(c),
                              "shared_signals": self.shared_signals(c)})
        rings.sort(key=lambda r: -r["size"])
        return rings
