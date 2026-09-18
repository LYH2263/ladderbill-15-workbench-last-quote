import pytest
from pydantic import ValidationError

from app.config import DATA_DIR, DB_FILENAME
from app.schemas.billing import BillRequest
from app.seed import init_db
from app.services.billing_service import BillingService


@pytest.fixture()
def svc():
    db = DATA_DIR / DB_FILENAME
    if db.exists():
        db.unlink()
    init_db()
    with BillingService() as s:
        yield s


def test_success_saves_summary(svc):
    r = svc.run_bill(220, True, 1, True)
    s = svc.get_last_success(1)
    assert s is not None
    assert s["account_id"] == 1
    assert s["kwh"] == 220
    assert s["peak"] is True
    assert s["total"] == r["total"]
    assert s["run_id"] == r["run_id"]
    assert s["success_at"]


def test_latest_success_overwrites(svc):
    svc.run_bill(100, False, 1, True)
    r2 = svc.run_bill(300, True, 1, True)
    s = svc.get_last_success(1)
    assert s["kwh"] == 300
    assert s["peak"] is True
    assert s["run_id"] == r2["run_id"]


def test_summaries_are_per_account(svc):
    svc.run_bill(100, False, 1, True)
    svc.run_bill(400, True, 2, True)
    assert svc.get_last_success(1)["kwh"] == 100
    assert svc.get_last_success(2)["kwh"] == 400


def test_failed_calc_keeps_previous_summary(svc):
    svc.run_bill(100, False, 1, True)
    before = svc.get_last_success(1)
    with pytest.raises(ValueError):
        svc.run_bill(-5, False, 1, True)
    assert svc.get_last_success(1) == before


def test_validation_rejection_does_not_touch_summary(svc):
    svc.run_bill(100, False, 1, True)
    before = svc.get_last_success(1)
    with pytest.raises(ValidationError):
        BillRequest(account_id=1, kwh=-1)
    assert svc.get_last_success(1) == before


def test_run_without_account_saves_nothing(svc):
    svc.run_bill(100, False, None, True)
    assert svc.get_last_success(1) is None
    assert svc.get_last_success(2) is None


def test_clear_summary(svc):
    svc.run_bill(100, False, 1, True)
    svc.clear_last_success(1)
    assert svc.get_last_success(1) is None
    # 重复清除幂等，不报错
    svc.clear_last_success(1)
