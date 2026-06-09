#!/usr/bin/env python3
"""Generate golden-run artifacts for demo-service (deterministic, no LLM)."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

POLICY_VERSION = "1.2.0"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def submission_ready(decision: str) -> bool:
    return decision in ("Pass", "ConditionalPass")


def generate_run(root: Path, run_id: str, scenario: str) -> dict:
    runs = root / ".claude" / "runs" / run_id
    middleware_rel = "compliance/examples/middleware_cases.sample.json"
    if scenario == "unmatched":
        middleware_rel = "compliance/examples/middleware_cases.unmatched.json"

    subprocess.check_call(
        [
            sys.executable,
            str(root / "compliance/scripts/init_run.py"),
            "--project-root",
            str(root),
            "--run-id",
            run_id,
            "--repo-path",
            "compliance/fixtures/demo-service",
            "--services",
            "order-service",
            "--middleware",
            middleware_rel,
        ],
        cwd=str(root),
    )

    ctx = {
        "service": "order-service",
        "role": "REST API with MySQL persistence",
        "entryPoints": ["REST /api/orders/{id}"],
        "dataStores": ["MySQL via Spring datasource"],
        "externalCalls": [],
        "sensitiveAssets": ["order records"],
    }
    (runs / "01-context" / "order-service.json").write_text(
        json.dumps(ctx, indent=2) + "\n", encoding="utf-8"
    )

    applicability = {
        "service": "order-service",
        "applicableBaselines": [
            {
                "baselineId": "sql-injection-baseline",
                "domain": "SQLI",
                "coverageScope": "serviceVerified",
                "applicable": True,
                "reason": "Uses JDBC/MySQL and dynamic SQL patterns",
            },
            {
                "baselineId": "auth-baseline",
                "domain": "AUTH",
                "coverageScope": "serviceInferred",
                "applicable": True,
                "reason": "Public REST endpoints without visible auth annotations",
            },
            {
                "baselineId": "secrets-baseline",
                "domain": "SECRETS",
                "coverageScope": "productOnly",
                "applicable": True,
                "reason": "Datasource credentials in configuration",
            },
            {
                "baselineId": "dependency-baseline",
                "domain": "DEPENDENCY",
                "coverageScope": "productOnly",
                "applicable": True,
                "reason": "Maven dependencies present",
            },
        ],
        "excludedBaselines": [
            {
                "baselineId": "command-injection-baseline",
                "domain": "CMDI",
                "reason": "No Runtime.exec or ProcessBuilder usage detected",
            },
            {
                "baselineId": "file-operation-baseline",
                "domain": "FILE",
                "reason": "No file upload/download APIs detected",
            },
        ],
    }
    (runs / "02-applicability" / "order-service.json").write_text(
        json.dumps(applicability, indent=2) + "\n", encoding="utf-8"
    )

    sig_dir = runs / "03-signals" / "order-service"
    sig_dir.mkdir(parents=True, exist_ok=True)

    exposure = {
        "service": "order-service",
        "signalType": "exposure",
        "signals": [
            {
                "signalId": "S-EXP-001",
                "domain": "AUTH",
                "strength": "likely",
                "serviceLevelSummary": "REST order API lacks visible authentication controls on controller",
                "anchors": ["OrderController.java:17"],
                "confidence": 0.7,
            }
        ],
    }
    dataflow = {
        "service": "order-service",
        "signalType": "dataflow",
        "signals": [
            {
                "signalId": "S-DF-001",
                "domain": "SQLI",
                "strength": "confirmed",
                "serviceLevelSummary": "Order lookup builds SQL via string concatenation with user input",
                "anchors": ["OrderDao.java:8"],
                "confidence": 0.92,
            }
        ],
    }
    controlplane = {
        "service": "order-service",
        "signalType": "controlplane",
        "signals": [
            {
                "signalId": "S-CP-001",
                "domain": "SECRETS",
                "strength": "likely",
                "serviceLevelSummary": "Database credentials configured in application.yml",
                "anchors": ["application.yml:3"],
                "confidence": 0.75,
            },
            {
                "signalId": "S-CP-002",
                "domain": "CMDI",
                "strength": "not_applicable",
                "serviceLevelSummary": "Command execution surface not applicable for this service",
                "anchors": [],
                "confidence": 1.0,
            },
        ],
    }
    (sig_dir / "exposure.json").write_text(json.dumps(exposure, indent=2) + "\n", encoding="utf-8")
    (sig_dir / "dataflow.json").write_text(json.dumps(dataflow, indent=2) + "\n", encoding="utf-8")
    (sig_dir / "controlplane.json").write_text(json.dumps(controlplane, indent=2) + "\n", encoding="utf-8")

    if scenario == "soft":
        mappings = {
            "mappings": [
                {
                    "riskId": "R-SQL-001",
                    "caseId": "CASE-SQL-ALL-001",
                    "coverageState": "Covered",
                    "coverageScope": "serviceVerified",
                    "confidence": 0.8,
                    "explanation": "SQLI domain matched via wildcard case [domain_matched] [partial:depth_insufficient]",
                },
                {
                    "riskId": "R-AUTH-001",
                    "caseId": "CASE-AUTH-001",
                    "coverageState": "Covered",
                    "coverageScope": "serviceInferred",
                    "confidence": 0.85,
                    "explanation": "AUTH domain matched via wildcard middleware case [domain_matched]",
                },
            ],
            "mappingExplanation": [
                "Lenient phase: SQLI domain matched; depth noted for audit only",
                "Wildcard middleware cases used as fallback coverage for AUTH on order-service",
                "CMDI and FILE baselines excluded for order-service",
            ],
        }
        gaps = {"gaps": []}
        decision = {
            "decision": "ConditionalPass",
            "reasons": ["domain_matched_lenient_phase"],
            "policyVersion": POLICY_VERSION,
        }
    elif scenario == "hard":
        mappings = {
            "mappings": [
                {
                    "riskId": "R-SQL-001",
                    "caseId": "CASE-SQL-001",
                    "coverageState": "Covered",
                    "coverageScope": "serviceVerified",
                    "confidence": 0.9,
                    "explanation": "SQLI domain matched; service case FAIL noted for audit [domain_matched] [partial:case_failed]",
                },
                {
                    "riskId": "R-AUTH-001",
                    "caseId": "CASE-AUTH-001",
                    "coverageState": "Covered",
                    "coverageScope": "serviceInferred",
                    "confidence": 0.85,
                    "explanation": "AUTH domain matched via wildcard middleware case [domain_matched]",
                },
            ],
            "mappingExplanation": [
                "Lenient phase: SQLI domain matched despite service-level FAIL",
                "Wildcard middleware cases used as fallback coverage for AUTH on order-service",
                "CMDI and FILE baselines excluded for order-service",
            ],
        }
        gaps = {
            "gaps": [
                {
                    "riskId": "R-SQL-001",
                    "service": "order-service",
                    "category": "SQLI",
                    "gapType": "CaseFailed",
                    "caseId": "CASE-SQL-001",
                    "suggestion": "Remediate SQL injection pattern and re-run middleware case",
                }
            ]
        }
        decision = {
            "decision": "ConditionalPass",
            "reasons": ["domain_matched_lenient_phase"],
            "policyVersion": POLICY_VERSION,
        }
    else:
        mappings = {
            "mappings": [
                {
                    "riskId": "R-AUTH-001",
                    "caseId": "CASE-AUTH-001",
                    "coverageState": "Covered",
                    "coverageScope": "serviceInferred",
                    "confidence": 0.85,
                    "explanation": "AUTH domain matched via wildcard middleware case [domain_matched]",
                }
            ],
            "mappingExplanation": [
                "SQLI open risk has no middleware case in same domain (unmatched fixture)",
                "AUTH domain matched",
            ],
        }
        gaps = {
            "gaps": [
                {
                    "riskId": "R-SQL-001",
                    "service": "order-service",
                    "category": "SQLI",
                    "gapType": "NoCaseMatched",
                    "suggestion": "Add sql-injection-baseline middleware case for order-service or wildcard",
                }
            ]
        }
        decision = {
            "decision": "Block",
            "reasons": ["risk_domain_without_matching_case"],
            "policyVersion": POLICY_VERSION,
        }

    ready = submission_ready(decision["decision"])
    profile = {
        "service": "order-service",
        "applicableBaselines": [
            "sql-injection-baseline",
            "auth-baseline",
            "secrets-baseline",
            "dependency-baseline",
        ],
        "excludedBaselines": applicability["excludedBaselines"],
        "riskPointIds": ["R-SQL-001", "R-AUTH-001"],
        "riskPoints": [
            {
                "riskId": "R-SQL-001",
                "service": "order-service",
                "category": "SQLI",
                "severity": "P1",
                "status": "Open",
                "codeEvidence": ["OrderDao.java:8"],
                "serviceLevelSummary": "Dynamic SQL concatenation in order lookup",
            },
            {
                "riskId": "R-AUTH-001",
                "service": "order-service",
                "category": "AUTH",
                "severity": "P1",
                "status": "Open",
                "codeEvidence": ["OrderController.java:17"],
                "serviceLevelSummary": "Order API may lack authentication enforcement",
            },
        ],
        "overallExposure": "high",
        "readyForSubmission": ready,
    }
    (runs / "04-profiles" / "order-service.json").write_text(
        json.dumps(profile, indent=2) + "\n", encoding="utf-8"
    )

    subprocess.check_call(
        [
            sys.executable,
            str(root / "compliance/scripts/merge_risk_points.py"),
            "--profiles-dir",
            str(runs / "04-profiles"),
            "--output",
            str(runs / "05-risk-points.json"),
        ],
        cwd=str(root),
    )

    (runs / "06-mappings.json").write_text(json.dumps(mappings, indent=2) + "\n", encoding="utf-8")
    (runs / "07-gaps.json").write_text(json.dumps(gaps, indent=2) + "\n", encoding="utf-8")
    (runs / "08-decision.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")

    middleware = json.loads((root / middleware_rel).read_text(encoding="utf-8"))
    risk_points = json.loads((runs / "05-risk-points.json").read_text(encoding="utf-8"))

    trace = []
    for step, path in [
        ("init", runs / "manifest.json"),
        ("slices", runs / "00-service-slices.json"),
        ("context", runs / "01-context/order-service.json"),
        ("applicability", runs / "02-applicability/order-service.json"),
        ("signals", sig_dir / "dataflow.json"),
        ("profile", runs / "04-profiles/order-service.json"),
        ("mappings", runs / "06-mappings.json"),
        ("decision", runs / "08-decision.json"),
    ]:
        trace.append(
            {
                "runId": run_id,
                "agentType": step,
                "inputHash": "golden",
                "outputHash": sha256_file(path),
                "artifactPath": str(path.relative_to(root)),
                "latencyMs": 0,
                "retryCount": 0,
            }
        )

    evidence = {
        "version": "1.0.0",
        "releaseId": run_id,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "policyVersion": POLICY_VERSION,
        "taxonomyVersion": "1.0.0",
        "decision": decision,
        "riskPoints": risk_points,
        "middlewareCases": middleware,
        "mappings": mappings["mappings"],
        "gaps": gaps["gaps"],
        "agentRunTrace": trace,
    }
    evidence_dir = runs / "09-evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "index.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    validator = root / "compliance/scripts/validate_artifact.py"
    checks = [
        ("service-context", runs / "01-context/order-service.json"),
        ("applicability", runs / "02-applicability/order-service.json"),
        ("threat-signal", sig_dir / "dataflow.json"),
        ("service-risk-profile", runs / "04-profiles/order-service.json"),
        ("risk-points", runs / "05-risk-points.json"),
        ("risk-case-mapping", runs / "06-mappings.json"),
        ("gaps", runs / "07-gaps.json"),
        ("decision", runs / "08-decision.json"),
    ]
    for schema, path in checks:
        subprocess.check_call(
            [
                sys.executable,
                str(validator),
                "--schema",
                schema,
                "--file",
                str(path),
                "--schema-dir",
                str(root / "compliance/schemas"),
            ],
            cwd=str(root),
        )

    return {
        "runId": run_id,
        "scenario": scenario,
        "decision": decision["decision"],
        "readyForSubmission": ready,
        "evidence": str(evidence_dir / "index.json"),
    }


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    results = [
        generate_run(root, "golden-demo-soft", "soft"),
        generate_run(root, "golden-demo-hard", "hard"),
        generate_run(root, "golden-demo-unmatched", "unmatched"),
    ]
    print(json.dumps({"runs": results, "policyVersion": POLICY_VERSION}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
