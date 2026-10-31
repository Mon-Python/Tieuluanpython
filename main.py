"""Application entry point."""

import argparse
import sys
from typing import Optional, Sequence

from config import ensure_data_dirs
from data_repository import JsonDataRepository
from auth import get_auth_manager
from sample_data import initialize_sample_data
from exam_repository import ExamRepository
from gui.app import MainApplication
from gui.login_window import LoginWindow


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Initialize the application and return its process exit code."""
    parser = argparse.ArgumentParser(description="Question bank management system")
    parser.parse_args(argv)

    ensure_data_dirs()

    exam_repository = ExamRepository()
    repository = JsonDataRepository(
        usage_checker=exam_repository.is_question_used
    )
    initialize_sample_data(repository, get_auth_manager())

    login_window = LoginWindow()
    login_window.mainloop()
    current_user = login_window.logged_in_user
    if current_user is None:
        return 0

    application = MainApplication(current_user, repository)
    application.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
