"""
json_file_handler.py
=====================
[A sở hữu] Đọc/ghi JSON an toàn - MỌI file lưu trữ trong dự án đều đi qua lớp này.

API (đã chốt):
    read(path, default)      file thiếu/rỗng -> trả bản sao của `default`
    write(path, data)        ghi file tạm rồi os.replace -> không bao giờ để file nửa vời
    backup(path)             copy vào thư mục backup kèm timestamp, trả về đường dẫn
    restore(backup, target)  kiểm tra bản backup hợp lệ, backup bản hiện tại, rồi ghi đè
    list_backups()           danh sách backup, mới nhất trước

Mọi lỗi (JSON hỏng, không có quyền...) đều ném JsonFileError - kế thừa ValueError
nên GUI chỉ cần bắt ValueError là đủ.
"""

import copy
import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from config import BACKUP_DIR

PathLike = Union[str, os.PathLike]


class JsonFileError(ValueError):
    """Lỗi đọc/ghi file JSON. Message viết sẵn để hiển thị thẳng cho người dùng."""


class JsonFileHandler:

    def __init__(self, backup_dir: Optional[PathLike] = None):
        self.backup_dir = Path(backup_dir) if backup_dir else Path(BACKUP_DIR)

    # ---------------- Đọc ----------------

    def read(self, path: PathLike, default: Any = None) -> Any:
        """Đọc file JSON. File chưa có hoặc rỗng -> trả bản sao của default."""
        p = Path(path)
        if not p.exists():
            return copy.deepcopy(default)
        try:
            # utf-8-sig: chịu được file do Notepad lưu kèm BOM
            text = p.read_text(encoding="utf-8-sig")
        except PermissionError:
            raise JsonFileError(
                f"Không có quyền đọc file '{p.name}'. Hãy kiểm tra quyền truy cập "
                "hoặc đóng chương trình khác đang mở file này."
            ) from None
        except UnicodeDecodeError:
            raise JsonFileError(
                f"File '{p.name}' không phải văn bản UTF-8. "
                "Hãy khôi phục từ bản sao lưu."
            ) from None
        except OSError as e:
            raise JsonFileError(f"Không đọc được file '{p.name}': {e}") from e

        if not text.strip():
            return copy.deepcopy(default)
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise JsonFileError(
                f"File '{p.name}' bị hỏng hoặc sai định dạng JSON "
                f"(dòng {e.lineno}, cột {e.colno}). "
                "Hãy sửa tay file hoặc dùng Menu > Khôi phục để lấy lại bản sao lưu."
            ) from e

    # ---------------- Ghi ----------------

    def write(self, path: PathLike, data: Any) -> None:
        """Ghi an toàn: ghi vào file tạm cùng thư mục, fsync, rồi thay thế file thật."""
        p = Path(path)
        tmp_name = None
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(dir=str(p.parent),
                                            prefix=p.name + ".", suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_name, p)
        except PermissionError:
            self._cleanup(tmp_name)
            raise JsonFileError(
                f"Không có quyền ghi file '{p.name}'. Hãy kiểm tra quyền thư mục "
                "hoặc đóng chương trình khác đang mở file này."
            ) from None
        except (OSError, TypeError, ValueError) as e:
            self._cleanup(tmp_name)
            raise JsonFileError(f"Không ghi được file '{p.name}': {e}") from e

    @staticmethod
    def _cleanup(tmp_name: Optional[str]) -> None:
        if tmp_name and os.path.exists(tmp_name):
            try:
                os.remove(tmp_name)
            except OSError:
                pass

    # ---------------- Sao lưu / khôi phục ----------------

    def backup(self, path: PathLike) -> Path:
        """Copy file vào thư mục backup, tên có timestamp. Trả về đường dẫn bản backup."""
        src = Path(path)
        if not src.exists():
            raise JsonFileError(f"Không có file '{src.name}' để sao lưu.")
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            dst = self.backup_dir / f"{src.stem}_{stamp}{src.suffix}"
            shutil.copy2(src, dst)
        except OSError as e:
            raise JsonFileError(f"Không sao lưu được '{src.name}': {e}") from e
        return dst

    def restore(self, backup_path: PathLike, target_path: PathLike) -> None:
        """
        Khôi phục target từ backup. Thứ tự an toàn:
        1) kiểm tra bản backup là JSON hợp lệ (hỏng thì dừng, target giữ nguyên)
        2) backup bản hiện tại (phòng khôi phục nhầm)
        3) ghi đè target
        """
        bak = Path(backup_path)
        target = Path(target_path)
        if not bak.exists():
            raise JsonFileError(f"Không tìm thấy bản sao lưu '{bak.name}'.")
        data = self.read(bak, default=None)
        if data is None:
            raise JsonFileError(f"Bản sao lưu '{bak.name}' rỗng, không thể khôi phục.")
        if target.exists():
            self.backup(target)
        self.write(target, data)

    def list_backups(self) -> list:
        """Danh sách file backup, mới nhất trước (dùng cho Menu > Khôi phục)."""
        if not self.backup_dir.exists():
            return []
        files = [f for f in self.backup_dir.iterdir() if f.is_file()]
        return sorted(files, key=lambda f: (f.stat().st_mtime_ns, f.name), reverse=True)