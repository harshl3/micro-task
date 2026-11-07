import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from registration_validator import check_registrations, is_valid_email, main


class EmailTests(unittest.TestCase):
    def test_good_email(self):
        self.assertTrue(is_valid_email("ana@mail.com"))

    def test_email_without_at(self):
        self.assertFalse(is_valid_email("ana.mail.com"))

    def test_email_without_dot_after_at(self):
        self.assertFalse(is_valid_email("ana@silva@mail"))


class CheckRegistrationsTests(unittest.TestCase):
    def test_example_from_the_task(self):
        lines = ["Ana Silva, ana@mail.com, WOOD", "Bob, bob@mail.com, ART"]
        report, valid, problems = check_registrations(lines)
        self.assertEqual(
            report,
            [
                "Line 1: confirmed Ana Silva <ana@mail.com> for WOOD",
                "Line 2: unknown workshop code ART",
            ],
        )
        self.assertEqual(valid, 1)
        self.assertEqual(problems, 1)

    def test_blank_lines_are_skipped_but_still_counted(self):
        lines = ["", " ", "Ana Silva, ana@mail.com, WOOD"]
        report, valid, problems = check_registrations(lines)
        self.assertEqual(report, ["Line 3: confirmed Ana Silva <ana@mail.com> for WOOD"])
        self.assertEqual((valid, problems), (1, 0))

    def test_extra_spaces_and_phone(self):
        lines = [" Carla Mendes , carla@mail.com , GARDEN , 555-0101 "]
        report, valid, problems = check_registrations(lines)
        self.assertEqual(
            report,
            ["Line 1: confirmed Carla Mendes <carla@mail.com> for GARDEN (phone 555-0101)"],
        )
        self.assertEqual((valid, problems), (1, 0))

    def test_missing_name(self):
        report, valid, problems = check_registrations([", dan@mail.com, BIKE"])
        self.assertEqual(report, ["Line 1: missing name"])
        self.assertEqual((valid, problems), (0, 1))

    def test_invalid_email(self):
        report, valid, problems = check_registrations(["Eve Stone, eve.mail.com, CODE"])
        self.assertEqual(report, ["Line 1: invalid email eve.mail.com"])
        self.assertEqual((valid, problems), (0, 1))

    def test_duplicate_email_flags_only_the_second(self):
        lines = ["Ana Silva, ana@mail.com, WOOD", "Gina Ruiz, ANA@mail.com, CODE"]
        report, valid, problems = check_registrations(lines)
        self.assertEqual(
            report,
            [
                "Line 1: confirmed Ana Silva <ana@mail.com> for WOOD",
                "Line 2: duplicate email ANA@mail.com",
            ],
        )
        self.assertEqual((valid, problems), (1, 1))

    def test_one_line_can_have_several_problems(self):
        report, valid, problems = check_registrations(["nobody, ART"])
        self.assertEqual(
            report,
            [
                "Line 1: missing name",
                "Line 1: invalid email nobody",
                "Line 1: unknown workshop code ART",
            ],
        )
        self.assertEqual((valid, problems), (0, 3))

    def test_wrong_number_of_fields(self):
        report, valid, problems = check_registrations(["Ana Silva ana@mail.com WOOD"])
        self.assertEqual(report, ["Line 1: expected name, email, workshop code and optional phone"])
        self.assertEqual((valid, problems), (0, 1))


class MainTests(unittest.TestCase):
    def run_main(self, args):
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(args)
        return exit_code, output.getvalue()

    def test_reads_a_windows_file_with_crlf(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "list.txt")
            with open(path, "w", newline="") as file:
                file.write("Ana Silva, ana@mail.com, WOOD\r\nBob, bob@mail.com, ART\r\n")

            exit_code, text = self.run_main([path])
            self.assertEqual(exit_code, 0)
            self.assertEqual(
                text.splitlines(),
                [
                    "Line 1: confirmed Ana Silva <ana@mail.com> for WOOD",
                    "Line 2: unknown workshop code ART",
                    "Valid registrations: 1",
                    "Total problems: 1",
                ],
            )

    def test_reads_a_windows_file_with_crlf_and_extra_spaces(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "list.txt")
            with open(path, "w", newline="") as file:
                file.write("Ana Silva, ana@mail.com, WOOD\r\nBob, bob@mail.com, ART\r\n")

            exit_code, text = self.run_main([path])
            self.assertEqual(exit_code, 0)
            self.assertIn("Valid registrations: 1", text)
            self.assertIn("Total problems: 1", text)

    def test_missing_file(self):
        exit_code, text = self.run_main(["no_such_file.txt"])
        self.assertEqual(exit_code, 1)
        self.assertIn("File not found: no_such_file.txt", text)


if __name__ == "__main__":
    unittest.main()
