"""Tier 1 tests for PortAllocator (TECHNICAL_SPEC.md Part 7 §3).

Tests verify port availability checking, sequential conflict reallocation,
common port fallback, release, and allocation tracking.
"""

import socket
import pytest
from app.engine.port_allocator import PortAllocator, NoPortAvailableError


class TestPortAllocator:
    def test_allocate_preferred_port_when_free(self):
        allocator = PortAllocator()
        # Pick a high port that is free
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", 0))
            free_port = s.getsockname()[1]
        
        allocated = allocator.allocate("test_svc", preferred_port=free_port)
        assert allocated == free_port
        assert allocator.get_allocation_map()["test_svc"] == free_port

    def test_allocate_reassigns_to_next_free_when_taken(self):
        allocator = PortAllocator()
        # Bind a socket on a port to simulate conflict
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", 0))
        taken_port = sock.getsockname()[1]
        sock.listen(1)

        try:
            allocated = allocator.allocate("postgres", preferred_port=taken_port)
            assert allocated != taken_port
            assert allocated > taken_port
            assert allocator.is_available(allocated) is False  # Now reserved in allocator
        finally:
            sock.close()

    def test_internal_allocated_prevents_duplicate_assignment(self):
        allocator = PortAllocator()
        port = 55555
        p1 = allocator.allocate("svc1", preferred_port=port)
        p2 = allocator.allocate("svc2", preferred_port=port)
        assert p1 == port
        assert p2 == port + 1

    def test_release_allows_reallocation(self):
        allocator = PortAllocator()
        port = 55556
        p1 = allocator.allocate("svc1", preferred_port=port)
        assert p1 == port
        allocator.release(port)
        assert port not in allocator.allocated

    def test_invalid_ports_not_available(self):
        allocator = PortAllocator()
        assert allocator.is_available(-1) is False
        assert allocator.is_available(0) is False
        assert allocator.is_available(70000) is False

    def test_allocate_no_preferred_uses_common_ports(self):
        allocator = PortAllocator()
        port = allocator.allocate("redis")
        assert port in [6379] or (49152 <= port <= 65535)

    def test_no_port_available_raises(self, monkeypatch):
        allocator = PortAllocator()
        monkeypatch.setattr(allocator, "is_available", lambda p: False)
        with pytest.raises(NoPortAvailableError):
            allocator.allocate("test", preferred_port=5000)
