"""Verify the installed src-layout package can be imported."""

import importlib

import pytest


@pytest.mark.parametrize(
    "module_name",
    ["lexaflow", "lexaflow.builder", "lexaflow.builder.data", "lexaflow.shared"],
)
def test_package_import(module_name: str) -> None:
    assert importlib.import_module(module_name).__name__ == module_name
