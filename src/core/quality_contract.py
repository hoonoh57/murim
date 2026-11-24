"""Pure evidence checks for the five-axis platform; no promotion authority."""
from dataclasses import dataclass
from hashlib import sha256
import json
import re


def _name(value: str) -> None:
    if type(value) is not str or not value.strip() or value != value.strip():
        raise ValueError("invalid identifier")


def _digest(value: str) -> None:
    if type(value) is not str or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("invalid SHA-256")


@dataclass(frozen=True)
class MetricTarget:
    name: str
    minimum: int
    target: int
    ceiling: int

    def __post_init__(self):
        _name(self.name)
        values = (self.minimum, self.target, self.ceiling)
        if any(type(v) is not int for v in values) or not self.minimum < self.target <= self.ceiling:
            raise ValueError("target must exceed minimum and fit the declared integer scale")


@dataclass(frozen=True)
class QualityContract:
    version: str
    metrics: tuple[MetricTarget, ...]
    checks: tuple[str, ...]

    def __post_init__(self):
        _name(self.version)
        if type(self.metrics) is not tuple or not self.metrics or any(type(m) is not MetricTarget for m in self.metrics):
            raise ValueError("metrics must be immutable and nonempty")
        if type(self.checks) is not tuple or not self.checks:
            raise ValueError("checks must be immutable and nonempty")
        for name in self.checks:
            _name(name)
        if len({m.name for m in self.metrics}) != len(self.metrics) or len(set(self.checks)) != len(self.checks):
            raise ValueError("duplicate requirement")

    @property
    def digest(self) -> str:
        data = {"version": self.version,
                "metrics": sorted((m.name, m.minimum, m.target, m.ceiling) for m in self.metrics),
                "checks": sorted(self.checks)}
        return sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


@dataclass(frozen=True)
class EvidenceBinding:
    task_id: str
    revision: str
    artifact_sha256: str
    contract_sha256: str
    producer_id: str

    def __post_init__(self):
        for value in (self.task_id, self.revision, self.producer_id):
            _name(value)
        for value in (self.artifact_sha256, self.contract_sha256):
            _digest(value)


@dataclass(frozen=True)
class QualityEvidence:
    binding: EvidenceBinding
    evaluator_id: str
    report_sha256: str
    metrics: tuple[tuple[str, int], ...]
    checks: tuple[tuple[str, bool], ...]
    unresolved_defects: tuple[str, ...]
    unassessed: tuple[str, ...]

    def __post_init__(self):
        if type(self.binding) is not EvidenceBinding:
            raise ValueError("invalid binding")
        _name(self.evaluator_id)
        _digest(self.report_sha256)
        for pairs, kind in ((self.metrics, int), (self.checks, bool)):
            if type(pairs) is not tuple:
                raise ValueError("mutable evidence")
            names = set()
            for pair in pairs:
                if type(pair) is not tuple or len(pair) != 2 or type(pair[1]) is not kind:
                    raise ValueError("invalid observation")
                _name(pair[0])
                if pair[0] in names:
                    raise ValueError("duplicate observation")
                names.add(pair[0])
        for group in (self.unresolved_defects, self.unassessed):
            if type(group) is not tuple:
                raise ValueError("mutable evidence")
            for item in group:
                _name(item)


def evidence_issues(contract: QualityContract, expected: EvidenceBinding,
                    evidence: QualityEvidence) -> tuple[str, ...]:
    """Check declared evidence only. Manager must authenticate and verify it.

    An empty result is NOT a promotion, independent review or content PASS.
    """
    issues = []
    if expected.contract_sha256 != contract.digest or evidence.binding != expected:
        issues.append("STALE_OR_MISMATCHED_BINDING")
    if evidence.evaluator_id == expected.producer_id:
        issues.append("SELF_EVALUATION")
    if evidence.unresolved_defects:
        issues.append("UNRESOLVED_DEFECTS")
    if evidence.unassessed:
        issues.append("UNASSESSED")
    observed = dict(evidence.metrics)
    checks = dict(evidence.checks)
    if set(observed) != {m.name for m in contract.metrics}:
        issues.append("METRIC_SET_MISMATCH")
    if set(checks) != set(contract.checks):
        issues.append("CHECK_SET_MISMATCH")
    for metric in contract.metrics:
        if metric.name in observed:
            value = observed[metric.name]
            if not metric.minimum <= value <= metric.ceiling:
                issues.append("OUTSIDE_REQUIRED_RANGE:" + metric.name)
            elif value < metric.target:
                issues.append("BELOW_TARGET:" + metric.name)
    for name in contract.checks:
        if checks.get(name) is not True:
            issues.append("CHECK_NOT_PASSED:" + name)
    return tuple(issues)
