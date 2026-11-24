from dataclasses import FrozenInstanceError, replace
import pytest
from src.core.quality_contract import (
    EvidenceBinding, MetricTarget, QualityContract, QualityEvidence, evidence_issues,
)


@pytest.fixture
def sample():
    contract = QualityContract("v1", (MetricTarget("clarity", 90, 96, 100),
                                     MetricTarget("coherence", 90, 95, 100)),
                               ("valid", "rights"))
    binding = EvidenceBinding("task", "r1", "a" * 64, contract.digest, "producer")
    evidence = QualityEvidence(binding, "reviewer", "b" * 64,
                               (("clarity", 96), ("coherence", 95)),
                               (("valid", True), ("rights", True)), (), ())
    return contract, binding, evidence


def test_target_and_all_checks_are_required(sample):
    assert evidence_issues(*sample) == ()


@pytest.mark.parametrize("values", [(90, 90, 100), (90, 101, 100), (True, 96, 100), (90, 96.0, 100)])
def test_invalid_targets_rejected(values):
    with pytest.raises(ValueError):
        MetricTarget("m", *values)


@pytest.mark.parametrize("change,issue", [
    ({"metrics": (("clarity", 95), ("coherence", 100))}, "BELOW_TARGET:clarity"),
    ({"metrics": (("clarity", 89), ("coherence", 100))}, "OUTSIDE_REQUIRED_RANGE:clarity"),
    ({"metrics": (("clarity", 101), ("coherence", 100))}, "OUTSIDE_REQUIRED_RANGE:clarity"),
    ({"metrics": (("clarity", 100),)}, "METRIC_SET_MISMATCH"),
    ({"checks": (("valid", True), ("rights", False))}, "CHECK_NOT_PASSED:rights"),
    ({"checks": (("valid", True),)}, "CHECK_SET_MISMATCH"),
    ({"unresolved_defects": ("d1",)}, "UNRESOLVED_DEFECTS"),
    ({"unassessed": ("d2",)}, "UNASSESSED"),
    ({"evaluator_id": "producer"}, "SELF_EVALUATION"),
])
def test_fail_closed(sample, change, issue):
    c, b, e = sample
    assert issue in evidence_issues(c, b, replace(e, **change))


@pytest.mark.parametrize("field,value", [("revision", "r2"), ("task_id", "other"),
                                         ("artifact_sha256", "c" * 64),
                                         ("contract_sha256", "d" * 64), ("producer_id", "other")])
def test_binding_cannot_be_reused(sample, field, value):
    c, b, e = sample
    assert "STALE_OR_MISMATCHED_BINDING" in evidence_issues(c, b, replace(e, binding=replace(b, **{field: value})))


def test_changed_contract_cannot_use_old_evidence(sample):
    c, b, e = sample
    changed = replace(c, metrics=(replace(c.metrics[0], target=97), c.metrics[1]))
    assert changed.digest != c.digest
    assert "STALE_OR_MISMATCHED_BINDING" in evidence_issues(changed, b, e)


@pytest.mark.parametrize("change", [
    {"metrics": (("clarity", True),)}, {"metrics": (("clarity", 96), ("clarity", 97))},
    {"checks": (("valid", 1),)}, {"checks": [("valid", True)]},
    {"report_sha256": "invalid"}, {"unassessed": []},
])
def test_malformed_evidence_rejected(sample, change):
    with pytest.raises(ValueError):
        replace(sample[2], **change)


def test_contract_immutable_and_order_independent(sample):
    c, _, _ = sample
    with pytest.raises(FrozenInstanceError):
        c.version = "v2"
    assert replace(c, metrics=c.metrics[::-1], checks=c.checks[::-1]).digest == c.digest
    with pytest.raises(ValueError):
        replace(c, checks=("valid", "valid"))
    with pytest.raises(ValueError):
        replace(c, metrics=list(c.metrics))
