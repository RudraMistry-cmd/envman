import sys
sys.path.insert(0, ".")
from harvest.tests.mock_docker_shim import (
    test_healthy_when_pg_isready_rc0,
    test_unhealthy_when_rc1_paused_or_starting,
    test_inspect_health_status_parsing,
)
# pytest discovers test_* automatically; this re-export keeps a single-file skeleton runnable.
