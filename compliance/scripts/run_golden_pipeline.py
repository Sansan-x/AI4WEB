#!/usr/bin/env python3
"""Generate golden-run artifacts for demo-service (deterministic, no LLM)."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

POLICY_VERSION = "1.3.0"
TAXONOMY_VERSION = "1.1.0"


def build_order_service_applicability() -> dict:
    applicable = [
        {
            "baselineId": "category-sql-injection",
            "ruleType": "SQL注入",
            "ruleTypeEn": "SQL Injection",
            "domain": "SQLI",
            "coverageScope": "serviceVerified",
            "applicable": True,
            "reason": "Uses JDBC/MySQL and dynamic SQL patterns",
        },
        {
            "baselineId": "category-identity-management",
            "ruleType": "身份管理",
            "ruleTypeEn": "Identity Management",
            "domain": "AUTH",
            "coverageScope": "serviceInferred",
            "applicable": True,
            "reason": "Public REST endpoints without visible auth annotations",
        },
        {
            "baselineId": "category-secrets-protection",
            "ruleType": "敏感信息保护",
            "ruleTypeEn": "Sensitive Information Protection",
            "domain": "SECRETS",
            "coverageScope": "productOnly",
            "applicable": True,
            "reason": "Datasource credentials in configuration",
        },
        {
            "baselineId": "category-security-config",
            "ruleType": "安全配置",
            "ruleTypeEn": "Security Configuration",
            "domain": "SEC_CONFIG",
            "coverageScope": "productOnly",
            "applicable": True,
            "reason": "Spring Boot configuration and Maven dependencies present",
        },
        {
            "baselineId": "category-web-security",
            "ruleType": "WEB安全",
            "ruleTypeEn": "Web Security",
            "domain": "WEB",
            "coverageScope": "serviceInferred",
            "applicable": True,
            "reason": "Public REST API endpoints exposed",
        },
        {
            "baselineId": "category-dos",
            "ruleType": "D-DoS",
            "ruleTypeEn": "Denial of Service",
            "domain": "DOS",
            "coverageScope": "serviceInferred",
            "applicable": True,
            "reason": "HTTP API service without visible rate limiting",
        },
        {
            "baselineId": "category-crypto-security",
            "ruleType": "密码算法安全",
            "ruleTypeEn": "Cryptographic Algorithm Security",
            "domain": "CRYPTO",
            "coverageScope": "serviceInferred",
            "applicable": True,
            "reason": "TLS and credential handling in Spring configuration",
        },
    ]
    excluded = [
        {
            "baselineId": "category-command-injection",
            "ruleType": "命令注入",
            "ruleTypeEn": "Command Injection",
            "domain": "CMDI",
            "reason": "No Runtime.exec or ProcessBuilder usage detected",
        },
        {
            "baselineId": "category-file-upload-download",
            "ruleType": "文件上传下载",
            "ruleTypeEn": "File Upload and Download",
            "domain": "FILE",
            "reason": "No file upload/download APIs detected",
        },
        {
            "baselineId": "category-sudo-privilege",
            "ruleType": "SUDO提权",
            "ruleTypeEn": "SUDO Privilege Escalation",
            "domain": "PRIV_ESC",
            "reason": "No shell or sudo invocation patterns detected",
        },
        {
            "baselineId": "category-template-injection",
            "ruleType": "模板注入",
            "ruleTypeEn": "Template Injection",
            "domain": "TEMPLATE_INJ",
            "reason": "No server-side template engine with user input detected",
        },
        {
            "baselineId": "category-csv-injection",
            "ruleType": "CSV注入",
            "ruleTypeEn": "CSV Injection",
            "domain": "CSV_INJ",
            "reason": "No CSV export endpoints detected",
        },
        {
            "baselineId": "category-xml-injection",
            "ruleType": "XML注入",
            "ruleTypeEn": "XML Injection",
            "domain": "XML_INJ",
            "reason": "No XML parsing of user-controlled input detected",
        },
        {
            "baselineId": "category-xss-injection",
            "ruleType": "XSS注入",
            "ruleTypeEn": "Cross-Site Scripting",
            "domain": "XSS",
            "reason": "JSON REST API only; no HTML rendering detected",
        },
    ]
    return {
        "service": "order-service",
        "applicableBaselines": applicable,
        "excludedBaselines": excluded,
    }


def not_applicable_signal(signal_id: str, domain: str, summary: str) -> dict:
    return {
        "signalId": signal_id,
        "domain": domain,
        "strength": "not_applicable",
        "serviceLevelSummary": summary,
        "anchors": [],
        "confidence": 1.0,
    }


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

    applicability = build_order_service_applicability()
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
            },
            not_applicable_signal("S-EXP-002", "WEB", "WEB security ruleType applicable; no additional exposure beyond AUTH scan"),
            not_applicable_signal("S-EXP-003", "DOS", "No unbounded resource patterns beyond standard REST API"),
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
            },
            not_applicable_signal("S-DF-002", "FILE", "File upload/download ruleType excluded"),
            not_applicable_signal("S-DF-003", "XSS", "XSS ruleType excluded for JSON REST API"),
            not_applicable_signal("S-DF-004", "XML_INJ", "XML injection ruleType excluded"),
            not_applicable_signal("S-DF-005", "CSV_INJ", "CSV injection ruleType excluded"),
            not_applicable_signal("S-DF-006", "TEMPLATE_INJ", "Template injection ruleType excluded"),
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
            not_applicable_signal("S-CP-002", "CMDI", "Command injection ruleType excluded"),
            not_applicable_signal("S-CP-003", "PRIV_ESC", "SUDO privilege escalation ruleType excluded"),
            not_applicable_signal("S-CP-004", "SEC_CONFIG", "Security configuration applicable; no critical misconfigurations detected"),
            not_applicable_signal("S-CP-005", "CRYPTO", "Cryptographic usage present; no weak algorithm patterns detected"),
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
                "CMDI, FILE, and other excluded ruleTypes not evaluated for order-service",
            ],
        }
        gaps = {"gaps": []}
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
                "CMDI, FILE, and other excluded ruleTypes not evaluated for order-service",
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
    elif scenario == "ratio-block":
        mappings = {
            "mappings": [
                {
                    "riskId": "R-SQL-001",
                    "caseId": "CASE-SQL-ALL-001",
                    "coverageState": "Covered",
                    "coverageScope": "serviceVerified",
                    "confidence": 0.8,
                    "explanation": "SQLI domain matched via wildcard case [domain_matched]",
                }
            ],
            "mappingExplanation": [
                "SQLI mandatory coverage met",
                "AUTH ratio-eligible risk has no middleware case in same domain",
            ],
        }
        gaps = {
            "gaps": [
                {
                    "riskId": "R-AUTH-001",
                    "service": "order-service",
                    "category": "AUTH",
                    "gapType": "NoCaseMatched",
                    "suggestion": "Add auth-baseline middleware case for order-service",
                }
            ]
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

    profile = {
        "service": "order-service",
        "applicableBaselines": [b["baselineId"] for b in applicability["applicableBaselines"]],
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
        "readyForSubmission": False,
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

    subprocess.check_call(
        [
            sys.executable,
            str(root / "compliance/scripts/compute_service_decision.py"),
            "--run-id",
            run_id,
            "--project-root",
            str(root),
        ],
        cwd=str(root),
    )

    decision = json.loads((runs / "08-decision.json").read_text(encoding="utf-8"))
    service_decision = json.loads(
        (runs / "08-decisions" / "order-service.json").read_text(encoding="utf-8")
    )
    ready = service_decision["readyForSubmission"]

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
        ("service-decision", runs / "08-decisions/order-service.json"),
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
        "taxonomyVersion": TAXONOMY_VERSION,
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
        ("service-decision", runs / "08-decisions/order-service.json"),
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
                "--project-root",
                str(root),
            ],
            cwd=str(root),
        )

    return {
        "runId": run_id,
        "scenario": scenario,
        "decision": decision["decision"],
        "serviceDecision": service_decision["decision"],
        "reasons": service_decision.get("reasons", []),
        "readyForSubmission": ready,
        "evidence": str(evidence_dir / "index.json"),
    }


def run_product_golden(root: Path) -> dict:
    product_run_id = "golden-product-eval"
    product_dir = root / ".claude" / "runs" / product_run_id
    product_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "productId": "demo-product",
        "productRunId": product_run_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "serviceRuns": [
            {
                "service": "order-service",
                "runId": "golden-demo-soft",
                "decisionPath": ".claude/runs/golden-demo-soft/08-decisions/order-service.json",
            },
            {
                "service": "order-service",
                "runId": "golden-demo-ratio-block",
                "decisionPath": ".claude/runs/golden-demo-ratio-block/08-decisions/order-service.json",
            },
        ],
        "policyGatePath": "compliance/taxonomy/policy-gate.yaml",
    }
    manifest_path = product_dir / "product-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    validator = root / "compliance/scripts/validate_artifact.py"
    schema_dir = root / "compliance/schemas"
    subprocess.check_call(
        [
            sys.executable,
            str(validator),
            "--schema",
            "product-manifest",
            "--file",
            str(manifest_path),
            "--schema-dir",
            str(schema_dir),
        ],
        cwd=str(root),
    )

    output_path = product_dir / "product-decision.json"
    subprocess.check_call(
        [
            sys.executable,
            str(root / "compliance/scripts/aggregate_product_decision.py"),
            "--manifest",
            str(manifest_path),
            "--project-root",
            str(root),
            "--output",
            str(output_path),
        ],
        cwd=str(root),
    )

    subprocess.check_call(
        [
            sys.executable,
            str(validator),
            "--schema",
            "product-decision",
            "--file",
            str(output_path),
            "--schema-dir",
            str(schema_dir),
        ],
        cwd=str(root),
    )

    product_decision = json.loads(output_path.read_text(encoding="utf-8"))
    if product_decision["decision"] != "ConditionalPass":
        raise RuntimeError(
            f"expected product ConditionalPass, got {product_decision['decision']!r}"
        )
    if not product_decision["readyForSubmission"]:
        raise RuntimeError("expected product readyForSubmission=true")

    return {
        "productRunId": product_run_id,
        "decision": product_decision["decision"],
        "reasons": product_decision.get("reasons", []),
        "output": str(output_path),
    }


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    results = [
        generate_run(root, "golden-demo-soft", "soft"),
        generate_run(root, "golden-demo-hard", "hard"),
        generate_run(root, "golden-demo-unmatched", "unmatched"),
        generate_run(root, "golden-demo-ratio-block", "ratio-block"),
    ]

    unmatched = next(r for r in results if r["runId"] == "golden-demo-unmatched")
    if unmatched["serviceDecision"] != "Block":
        raise RuntimeError(f"expected unmatched Block, got {unmatched['serviceDecision']!r}")
    if "mandatory_coverage_gap" not in unmatched["reasons"]:
        raise RuntimeError(f"expected mandatory_coverage_gap in reasons, got {unmatched['reasons']!r}")

    soft = next(r for r in results if r["runId"] == "golden-demo-soft")
    if soft["serviceDecision"] != "ConditionalPass":
        raise RuntimeError(f"expected soft ConditionalPass, got {soft['serviceDecision']!r}")

    ratio_block = next(r for r in results if r["runId"] == "golden-demo-ratio-block")
    if ratio_block["serviceDecision"] != "Block":
        raise RuntimeError(f"expected ratio-block Block, got {ratio_block['serviceDecision']!r}")

    product = run_product_golden(root)
    print(
        json.dumps(
            {"runs": results, "product": product, "policyVersion": POLICY_VERSION},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
