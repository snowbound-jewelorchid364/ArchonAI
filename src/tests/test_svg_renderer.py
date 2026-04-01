from __future__ import annotations
import sys
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parents[1]))

from archon.output.svg_renderer import SVGRenderer
from archon.core.models.artifact import Artifact, ArtifactType


def _make_pkg_with_diagram(sample_package):
    diagram = Artifact(
        id="diag-001",
        artifact_type=ArtifactType.DIAGRAM,
        title="System Context",
        content="graph TD\n  A --> B",
        filename="system-context.mmd",
    )
    sample_package.artifacts.append(diagram)
    return sample_package


def test_svg_renderer_fallback_when_mmdc_missing(sample_package):
    pkg = _make_pkg_with_diagram(sample_package)
    renderer = SVGRenderer()
    with patch("subprocess.run", side_effect=FileNotFoundError("mmdc not found")):
        result = renderer.render(pkg)
    assert "diag-001" in result
    assert "mmd-fallback" in result["diag-001"]
    assert "graph TD" in result["diag-001"]


def test_svg_renderer_returns_svg_on_success(sample_package, tmp_path):
    pkg = _make_pkg_with_diagram(sample_package)
    renderer = SVGRenderer()
    fake_svg = "<svg>test</svg>"

    def mock_run(cmd, **kwargs):
        out_path = Path(cmd[cmd.index("-o") + 1])
        out_path.write_text(fake_svg)
        m = MagicMock()
        m.returncode = 0
        return m

    with patch("subprocess.run", side_effect=mock_run):
        result = renderer.render(pkg)
    assert result.get("diag-001") == fake_svg


def test_svg_renderer_fallback_on_nonzero_returncode(sample_package):
    pkg = _make_pkg_with_diagram(sample_package)
    renderer = SVGRenderer()
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "error"
    with patch("subprocess.run", return_value=mock_result):
        result = renderer.render(pkg)
    assert "mmd-fallback" in result["diag-001"]


def test_svg_renderer_empty_when_no_diagrams(sample_package):
    sample_package.artifacts = []
    renderer = SVGRenderer()
    assert renderer.render(sample_package) == {}
