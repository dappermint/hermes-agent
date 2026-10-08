import os
import subprocess
import tempfile
import time
from pathlib import Path

from hermes_cli.update_lock import UpdateLock, _parse_marker, process_create_time


def test_handoff_sibling_custodian_and_coarse_delegate_adopted():
    """Verify that a handoff sibling custodian and coarse-ct delegate marker are adopted,
    preventing exit code 2 lock contention on macOS."""
    parent_pid = os.getpid()
    os.environ["HERMES_UPDATE_HANDOFF_PID"] = str(parent_pid)

    sibling = subprocess.Popen(["sleep", "10"])
    try:
        # 1. Verify child of handoff is recognized as partner
        assert UpdateLock._is_partner(sibling.pid) is True

        # 2. Verify marker with coarse delegate ct is adopted
        pid = os.getpid()
        ct = process_create_time(pid) or time.time()
        coarse_ct = float(int(ct))

        with tempfile.TemporaryDirectory() as td:
            marker_path = Path(td) / ".hermes-update-in-progress"
            custodian_ct = process_create_time(sibling.pid) or ct
            marker_content = (
                f"{sibling.pid}\n{int(time.time())}\nct:{custodian_ct:.3f}\n"
                f"delegate:{pid} ct:{coarse_ct:.3f}\n"
            ).encode()
            marker_path.write_bytes(marker_content)

            parsed = _parse_marker(marker_path.read_bytes())
            assert parsed.delegate_live() is True

            lock = UpdateLock(path=marker_path, checkout_first=False)
            assert lock.acquire() is True
            lock.release()
    finally:
        sibling.terminate()
        os.environ.pop("HERMES_UPDATE_HANDOFF_PID", None)
