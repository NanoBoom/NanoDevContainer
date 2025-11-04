"""Unit tests for bump_version.py using stdlib unittest."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from bump_version import (
    parse_version,
    increment_version,
    find_templates,
    update_template_version,
)


class TestVersionParsing(unittest.TestCase):
    """Tests for version parsing."""

    def test_parse_valid_version(self):
        """Test parsing valid semver strings."""
        major, minor, patch = parse_version("1.2.3")
        self.assertEqual(major, 1)
        self.assertEqual(minor, 2)
        self.assertEqual(patch, 3)

    def test_parse_invalid_version(self):
        """Test parsing invalid semver raises ValueError."""
        with self.assertRaises(ValueError):
            parse_version("invalid")

    def test_parse_incomplete_version(self):
        """Test parsing incomplete version."""
        with self.assertRaises(ValueError):
            parse_version("1.2")


class TestVersionIncrement(unittest.TestCase):
    """Tests for version incrementing."""

    def test_increment_patch(self):
        """Test patch version increment."""
        self.assertEqual(increment_version("1.2.3", "patch"), "1.2.4")

    def test_increment_minor(self):
        """Test minor version increment."""
        self.assertEqual(increment_version("1.2.3", "minor"), "1.3.0")

    def test_increment_major(self):
        """Test major version increment."""
        self.assertEqual(increment_version("1.2.3", "major"), "2.0.0")

    def test_increment_invalid_level(self):
        """Test invalid level raises ValueError."""
        with self.assertRaises(ValueError):
            increment_version("1.2.3", "invalid")


class TestTemplateFinding(unittest.TestCase):
    """Tests for template discovery."""

    def test_find_single_template(self):
        """Test finding single template file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            template = tmp_path / "devcontainer-template.json"
            template.write_text('{"version": "1.0.0"}')

            templates = find_templates(template)
            self.assertEqual(len(templates), 1)
            self.assertEqual(templates[0], template)

    def test_find_multiple_templates(self):
        """Test finding multiple templates in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "template1").mkdir()
            (tmp_path / "template1" / "devcontainer-template.json").write_text('{}')

            (tmp_path / "template2").mkdir()
            (tmp_path / "template2" / "devcontainer-template.json").write_text('{}')

            templates = find_templates(tmp_path)
            self.assertEqual(len(templates), 2)

    def test_find_no_templates(self):
        """Test error when no templates found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                find_templates(Path(tmpdir))

    def test_find_nonexistent_path(self):
        """Test error when path doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            find_templates(Path("/nonexistent/path"))


class TestTemplateUpdate(unittest.TestCase):
    """Tests for template version updating."""

    def test_update_template_success(self):
        """Test successful template update."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            template = tmp_path / "devcontainer-template.json"
            template.write_text(json.dumps({
                "id": "test-template",
                "version": "1.0.0"
            }))

            result = update_template_version(template, "patch", dry_run=False)
            self.assertTrue(result)

            # Verify file was updated
            with open(template) as f:
                data = json.load(f)
            self.assertEqual(data["version"], "1.0.1")

    def test_update_template_dry_run(self):
        """Test dry-run doesn't modify file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            template = tmp_path / "devcontainer-template.json"
            original_content = json.dumps({"id": "test", "version": "1.0.0"})
            template.write_text(original_content)

            result = update_template_version(template, "patch", dry_run=True)
            self.assertTrue(result)

            # Verify file was NOT updated
            self.assertEqual(template.read_text(), original_content)

    def test_update_template_invalid_json(self):
        """Test handling of invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            template = tmp_path / "devcontainer-template.json"
            template.write_text("invalid json")

            result = update_template_version(template, "patch", dry_run=False)
            self.assertFalse(result)

    def test_update_template_missing_version(self):
        """Test handling of missing version field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            template = tmp_path / "devcontainer-template.json"
            template.write_text(json.dumps({"id": "test"}))

            result = update_template_version(template, "patch", dry_run=False)
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
