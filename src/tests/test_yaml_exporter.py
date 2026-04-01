from __future__ import annotations
import sys
from pathlib import Path
import json
import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))

import yaml
from archon.output.yaml_exporter import YAMLExporter


def test_yaml_export_is_valid_yaml(sample_package):
    exporter = YAMLExporter()
    result = exporter.export_yaml(sample_package)
    assert isinstance(result, str)
    parsed = yaml.safe_load(result)
    assert isinstance(parsed, dict)


def test_yaml_export_contains_all_findings(sample_package):
    exporter = YAMLExporter()
    result = exporter.export_yaml(sample_package)
    parsed = yaml.safe_load(result)
    assert len(parsed["findings"]) == len(sample_package.findings)


def test_yaml_export_contains_run_id(sample_package):
    exporter = YAMLExporter()
    result = exporter.export_yaml(sample_package)
    assert sample_package.run_id in result


def test_json_export_is_valid_json(sample_package):
    exporter = YAMLExporter()
    result = exporter.export_json(sample_package)
    parsed = json.loads(result)
    assert parsed["run_id"] == sample_package.run_id


def test_json_export_contains_all_findings(sample_package):
    exporter = YAMLExporter()
    result = exporter.export_json(sample_package)
    parsed = json.loads(result)
    assert len(parsed["findings"]) == len(sample_package.findings)


def test_yaml_findings_have_severity(sample_package):
    exporter = YAMLExporter()
    result = exporter.export_yaml(sample_package)
    parsed = yaml.safe_load(result)
    for f in parsed["findings"]:
        assert "severity" in f
