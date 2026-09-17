import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    os.environ["PHISHGUARD_DATABASE"] = str(tmp_path / "test.db")
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

