"""
test_json_file_handler.py  [A]
Chạy: python -m unittest discover tests -v   (hoặc pytest tests -v)
Dùng thư mục tạm riêng, không đụng dữ liệu thật.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from json_file_handler import JsonFileHandler, JsonFileError


class TestJsonFileHandler(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.h = JsonFileHandler(backup_dir=self.tmp / "backup")
        self.f = self.tmp / "data.json"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_read_missing_returns_default(self):
        self.assertEqual(self.h.read(self.f, default=[]), [])

    def test_read_missing_returns_copy_of_default(self):
        default = {"a": []}
        result = self.h.read(self.f, default=default)
        result["a"].append(1)
        self.assertEqual(default, {"a": []})  # default gốc không bị sửa

    def test_read_empty_file_returns_default(self):
        self.f.write_text("", encoding="utf-8")
        self.assertEqual(self.h.read(self.f, default=[]), [])

    def test_read_whitespace_file_returns_default(self):
        self.f.write_text("  \n  ", encoding="utf-8")
        self.assertEqual(self.h.read(self.f, default={}), {})

    def test_read_invalid_json_raises(self):
        self.f.write_text("{bad json", encoding="utf-8")
        with self.assertRaises(JsonFileError):
            self.h.read(self.f)

    def test_json_file_error_is_value_error(self):
        self.assertTrue(issubclass(JsonFileError, ValueError))

    def test_read_file_with_bom(self):
        self.f.write_bytes(b"\xef\xbb\xbf" + json.dumps({"x": 1}).encode("utf-8"))
        self.assertEqual(self.h.read(self.f), {"x": 1})

    def test_write_then_read_unicode(self):
        data = [{"ten": "Lập trình Python", "so": 3}]
        self.h.write(self.f, data)
        self.assertEqual(self.h.read(self.f), data)

    def test_write_creates_parent_dirs(self):
        deep = self.tmp / "a" / "b" / "x.json"
        self.h.write(deep, [1])
        self.assertTrue(deep.exists())

    def test_write_leaves_no_tmp_file(self):
        self.h.write(self.f, [1, 2])
        self.assertEqual([p.name for p in self.tmp.iterdir() if p.suffix == ".tmp"], [])

    def test_write_failure_keeps_old_file_and_no_tmp(self):
        self.h.write(self.f, {"ok": True})
        with self.assertRaises(JsonFileError):
            self.h.write(self.f, {"bad": object()})   # không serialize được
        self.assertEqual(self.h.read(self.f), {"ok": True})
        self.assertEqual([p for p in self.tmp.iterdir() if p.suffix == ".tmp"], [])

    def test_write_relative_path_without_directory(self):
        old = os.getcwd()
        os.chdir(self.tmp)
        try:
            self.h.write("rel.json", [1])
            self.assertEqual(self.h.read("rel.json"), [1])
        finally:
            os.chdir(old)

    def test_accepts_str_and_path(self):
        self.h.write(str(self.f), [1])
        self.assertEqual(self.h.read(self.f), [1])

    def test_backup_copies_content(self):
        self.h.write(self.f, {"v": 1})
        bak = self.h.backup(self.f)
        self.assertTrue(bak.exists())
        self.assertEqual(self.h.read(bak), {"v": 1})

    def test_backup_missing_file_raises(self):
        with self.assertRaises(JsonFileError):
            self.h.backup(self.f)

    def test_restore_overwrites_and_keeps_safety_backup(self):
        self.h.write(self.f, {"v": 1})
        bak = self.h.backup(self.f)
        self.h.write(self.f, {"v": 2})
        before = len(self.h.list_backups())
        self.h.restore(bak, self.f)
        self.assertEqual(self.h.read(self.f), {"v": 1})
        self.assertEqual(len(self.h.list_backups()), before + 1)  # bản v=2 được giữ lại

    def test_restore_invalid_backup_keeps_target(self):
        self.h.write(self.f, {"v": 1})
        bad = self.tmp / "bad.json"
        bad.write_text("{oops", encoding="utf-8")
        with self.assertRaises(JsonFileError):
            self.h.restore(bad, self.f)
        self.assertEqual(self.h.read(self.f), {"v": 1})

    def test_restore_missing_backup_raises(self):
        with self.assertRaises(JsonFileError):
            self.h.restore(self.tmp / "khong_co.json", self.f)

    def test_restore_to_missing_target(self):
        self.h.write(self.f, [9])
        bak = self.h.backup(self.f)
        target = self.tmp / "new.json"
        self.h.restore(bak, target)
        self.assertEqual(self.h.read(target), [9])

    def test_list_backups_empty_when_no_dir(self):
        self.assertEqual(self.h.list_backups(), [])

    def test_list_backups_newest_first(self):
        self.h.write(self.f, [1])
        b1 = self.h.backup(self.f)
        b2 = self.h.backup(self.f)
        os.utime(b1, (1_000_000, 1_000_000))
        os.utime(b2, (2_000_000, 2_000_000))
        self.assertEqual(self.h.list_backups(), [b2, b1])


if __name__ == "__main__":
    unittest.main()