"""Tests for ZipPackageBuilder."""
from __future__ import annotations
import zipfile
import io
import pytest
from archon.output.zip_builder import ZipPackageBuilder


class TestZipPackageBuilder:
    def test_build_returns_bytes(self, sample_package):
        builder = ZipPackageBuilder()
        data = builder.build(sample_package)
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_zip_contains_readme(self, sample_package):
        builder = ZipPackageBuilder()
        data = builder.build(sample_package)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = zf.namelist()
            assert any("README.md" in n for n in names)

    def test_zip_contains_review(self, sample_package):
        builder = ZipPackageBuilder()
        data = builder.build(sample_package)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = zf.namelist()
            assert any("review.md" in n for n in names)

    def test_zip_contains_findings(self, sample_package):
        builder = ZipPackageBuilder()
        data = builder.build(sample_package)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = zf.namelist()
            assert any("findings/" in n for n in names)

    def test_zip_contains_risk_register(self, sample_package):
        builder = ZipPackageBuilder()
        data = builder.build(sample_package)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = zf.namelist()
            assert any("risk-register.md" in n for n in names)

    def test_zip_contains_citations(self, sample_package):
        builder = ZipPackageBuilder()
        data = builder.build(sample_package)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = zf.namelist()
            assert any("citations.md" in n for n in names)

    def test_zip_valid(self, sample_package):
        builder = ZipPackageBuilder()
        data = builder.build(sample_package)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            assert zf.testzip() is None

    def test_write_creates_file(self, sample_package, tmp_path):
        builder = ZipPackageBuilder()
        path = builder.write(sample_package, str(tmp_path))
        assert path.exists()
        assert path.suffix == ".zip"

    def test_partial_package(self, partial_package):
        builder = ZipPackageBuilder()
        data = builder.build(partial_package)
        assert isinstance(data, bytes)
        assert len(data) > 0