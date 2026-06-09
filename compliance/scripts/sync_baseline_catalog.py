#!/usr/bin/env python3
"""Validate or scaffold baseline-catalog.yaml from public_baseline categoryCatalog."""
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


DEFAULT_DOMAIN_MAP = {
    "安全配置": ("SEC_CONFIG", "productOnly", {"alwaysApplicable": True}),
    "命令注入": ("CMDI", "serviceVerified", {"requiresCommandExecution": True}),
    "模板注入": ("TEMPLATE_INJ", "serviceVerified", {"requiresTemplateEngine": True}),
    "CSV注入": ("CSV_INJ", "serviceVerified", {"requiresCsvExport": True}),
    "SQL注入": ("SQLI", "serviceVerified", {"requiresDataStore": True}),
    "XML注入": ("XML_INJ", "serviceVerified", {"requiresXmlParsing": True}),
    "XSS注入": ("XSS", "serviceVerified", {"requiresHttpEntry": True}),
    "密码算法安全": ("CRYPTO", "serviceInferred", {"requiresCryptoUsage": True}),
    "敏感信息保护": ("SECRETS", "productOnly", {"alwaysApplicable": True}),
    "身份管理": ("AUTH", "serviceInferred", {"requiresHttpEntry": True}),
    "文件上传下载": ("FILE", "serviceVerified", {"requiresFileIO": True}),
    "D-DoS": ("DOS", "serviceInferred", {"requiresHttpEntry": True}),
    "SUDO提权": ("PRIV_ESC", "serviceVerified", {"requiresShellOrSudo": True}),
    "WEB安全": ("WEB", "serviceInferred", {"requiresHttpEntry": True}),
}


def slugify(rule_type: str) -> str:
    mapping = {
        "安全配置": "security-config",
        "命令注入": "command-injection",
        "模板注入": "template-injection",
        "CSV注入": "csv-injection",
        "SQL注入": "sql-injection",
        "XML注入": "xml-injection",
        "XSS注入": "xss-injection",
        "密码算法安全": "crypto-security",
        "敏感信息保护": "secrets-protection",
        "身份管理": "identity-management",
        "文件上传下载": "file-upload-download",
        "D-DoS": "dos",
        "SUDO提权": "sudo-privilege",
        "WEB安全": "web-security",
    }
    return mapping.get(rule_type, rule_type.lower().replace(" ", "-"))


def load_category_catalog(template_path: Path) -> List[Dict[str, str]]:
    template = json.loads(template_path.read_text(encoding="utf-8"))
    return template.get("categoryCatalog", [])


def build_baseline_entry(item: Dict[str, str]) -> Dict[str, Any]:
    rule_type = item["ruleType"]
    domain, coverage, hints = DEFAULT_DOMAIN_MAP[rule_type]
    return {
        "baselineId": f"category-{slugify(rule_type)}",
        "title": item.get("ruleTypeEn", rule_type),
        "ruleType": rule_type,
        "ruleTypeEn": item.get("ruleTypeEn", ""),
        "domain": domain,
        "coverageScope": coverage,
        "applicabilityHints": hints,
    }


def load_catalog_rule_types(catalog_path: Path) -> set:
    text = catalog_path.read_text(encoding="utf-8")
    if yaml is not None:
        catalog = yaml.safe_load(text)
        return {b.get("ruleType") for b in catalog.get("baselines", []) if b.get("ruleType")}
    import re
    return set(re.findall(r"^\s*ruleType:\s*(.+?)\s*$", text, re.MULTILINE))


def validate_catalog(catalog_path: Path, template_path: Path) -> List[str]:
    errors: List[str] = []
    catalog_rule_types = load_catalog_rule_types(catalog_path)
    expected = {item["ruleType"] for item in load_category_catalog(template_path)}

    missing = expected - catalog_rule_types
    extra = catalog_rule_types - expected
    if missing:
        errors.append(f"baseline-catalog missing ruleTypes: {sorted(missing)}")
    if extra:
        errors.append(f"baseline-catalog has unknown ruleTypes: {sorted(extra)}")
    return errors


def write_catalog_skeleton(output_path: Path, template_path: Path) -> None:
    if yaml is None:
        raise RuntimeError("PyYAML required; pip install pyyaml")

    entries = [build_baseline_entry(item) for item in load_category_catalog(template_path)]
    doc = {
        "version": "1.1.0",
        "description": "Security baseline checklist aligned with public_baseline categoryCatalog (14 ruleTypes).",
        "baselines": entries,
    }
    output_path.write_text(
        yaml.dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync or validate baseline-catalog against categoryCatalog")
    parser.add_argument(
        "--template",
        default="compliance/examples/public_baseline.template.json",
        help="Path to public_baseline template JSON",
    )
    parser.add_argument(
        "--catalog",
        default="compliance/taxonomy/baseline-catalog.yaml",
        help="Path to baseline-catalog.yaml",
    )
    parser.add_argument(
        "--output",
        help="Write scaffold catalog to this path (default: validate only)",
    )
    args = parser.parse_args()

    template_path = Path(args.template)
    catalog_path = Path(args.catalog)

    if args.output:
        write_catalog_skeleton(Path(args.output), template_path)
        print(json.dumps({"written": args.output, "entries": len(load_category_catalog(template_path))}))
        return 0

    errors = validate_catalog(catalog_path, template_path)
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({"valid": True, "catalog": str(catalog_path), "ruleTypes": len(load_category_catalog(template_path))}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
