from idgraph import IdentityGraph


def test_ring_via_shared_device_and_email():
    g = IdentityGraph()
    g.add_account("a1", {"email": "x@e.com", "device": "D1", "doc": "P1"})
    g.add_account("a2", {"email": "y@e.com", "device": "D1", "doc": "P2"})  # shares device
    g.add_account("a3", {"email": "y@e.com", "device": "D9", "doc": "P3"})  # shares email w/ a2
    g.add_account("solo", {"email": "z@e.com", "device": "D5"})
    rings = g.find_rings(min_size=3)
    assert len(rings) == 1
    assert set(rings[0]["accounts"]) == {"a1", "a2", "a3"}
    assert "device" in rings[0]["shared_signals"]


def test_risk_score_ring():
    g = IdentityGraph()
    g.add_account("a1", {"device": "D1", "email": "x@e.com"})
    g.add_account("a2", {"device": "D1", "email": "y@e.com"})
    g.add_account("a3", {"device": "D1"})
    score = g.risk_score({"a1", "a2", "a3"})
    assert score > 0.0


def test_risk_score_singleton():
    g = IdentityGraph()
    g.add_account("solo", {"device": "D1"})
    assert g.risk_score({"solo"}) == 0.0


def test_edge_list():
    g = IdentityGraph()
    g.add_account("a", {"device": "D1"})
    g.add_account("b", {"device": "D1"})
    edges = g.edge_list()
    assert len(edges) >= 1
    assert edges[0][2] == "device"


def test_independent_accounts_not_linked():
    g = IdentityGraph()
    g.add_account("a", {"device": "D1"})
    g.add_account("b", {"device": "D2"})
    assert g.find_rings(min_size=2) == []
    assert len(g.clusters()) == 2
