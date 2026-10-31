import unittest
from unittest.mock import patch

import main


class TestMain(unittest.TestCase):
    def test_login_cancelled_does_not_start_main_application(self):
        events = []
        login = patch("main.LoginWindow").start()
        login.return_value.logged_in_user = None
        ensure_dirs = patch("main.ensure_data_dirs", side_effect=lambda: events.append("dirs")).start()
        login.side_effect = lambda: (events.append("login"), login.return_value)[1]
        app = patch("main.MainApplication").start()
        self.addCleanup(patch.stopall)

        self.assertEqual(main.main([]), 0)
        ensure_dirs.assert_called_once_with()
        login.assert_called_once_with()
        login.return_value.mainloop.assert_called_once_with()
        app.assert_not_called()
        self.assertEqual(events, ["dirs", "login"])

    def test_successful_login_starts_app_with_repository_usage_checker(self):
        user = object()
        login = patch("main.LoginWindow").start()
        login.return_value.logged_in_user = user
        exam_repository = patch("main.ExamRepository").start()
        data_repository = patch("main.JsonDataRepository").start()
        app = patch("main.MainApplication").start()
        ensure_dirs = patch("main.ensure_data_dirs").start()
        self.addCleanup(patch.stopall)

        self.assertEqual(main.main([]), 0)

        ensure_dirs.assert_called_once_with()
        login.assert_called_once_with()
        login.return_value.mainloop.assert_called_once_with()
        exam_repository.assert_called_once_with()
        data_repository.assert_called_once_with(
            usage_checker=exam_repository.return_value.is_question_used
        )
        app.assert_called_once_with(user, data_repository.return_value)
        app.return_value.mainloop.assert_called_once_with()

    def test_rejects_unrecognized_arguments(self):
        ensure_dirs = patch("main.ensure_data_dirs").start()
        login = patch("main.LoginWindow").start()
        self.addCleanup(patch.stopall)

        with self.assertRaises(SystemExit) as raised:
            main.main(["--unknown"])

        self.assertEqual(raised.exception.code, 2)
        ensure_dirs.assert_not_called()
        login.assert_not_called()


if __name__ == "__main__":
    unittest.main()
