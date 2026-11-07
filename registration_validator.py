import sys

ALLOWED_CODES = ["WOOD", "GARDEN", "BIKE", "CODE"]


def split_fields(line):
    """Split one line on commas and remove the spaces around each field."""
    return [field.strip() for field in line.split(",")]


def is_valid_email(email):
    """An email needs an @ and a dot somewhere after the @."""
    if "@" not in email:
        return False
    after_at = email.split("@")[-1]
    return "." in after_at


def check_registrations(lines):
    """Check every line and return (report, valid_count, problem_count)."""
    report = []
    valid_count = 0
    problem_count = 0
    seen_emails = []

    for line_number, line in enumerate(lines, start=1):
        if line.strip() == "":
            continue

        fields = split_fields(line)
        problems = []
        name = ""
        email = ""
        code = ""
        phone = ""

        if len(fields) == 1:
            problems.append("expected name, email, workshop code and optional phone")
        elif len(fields) == 2:
            email = fields[0]
            code = fields[1]
            name = ""
        elif len(fields) == 3:
            name = fields[0]
            email = fields[1]
            code = fields[2]
        elif len(fields) == 4:
            name = fields[0]
            email = fields[1]
            code = fields[2]
            phone = fields[3]
        else:
            problems.append("expected name, email, workshop code and optional phone")

        if not problems:
            if name == "":
                problems.append("missing name")

            if not is_valid_email(email):
                problems.append("invalid email " + email)
            elif email.lower() in seen_emails:
                problems.append("duplicate email " + email)
            else:
                seen_emails.append(email.lower())

            if code not in ALLOWED_CODES:
                problems.append("unknown workshop code " + code)

        if problems:
            for problem in problems:
                report.append("Line " + str(line_number) + ": " + problem)
            problem_count += len(problems)
        else:
            summary = "Line " + str(line_number) + ": confirmed " + name
            summary += " <" + email + "> for " + code
            if phone:
                summary += " (phone " + phone + ")"
            report.append(summary)
            valid_count += 1

    return report, valid_count, problem_count


def main(args):
    if len(args) != 1:
        print("Please give the registration file name,\nfor example: registrations.txt")
        return 1

    try:
        with open(args[0], encoding="utf-8-sig") as file:
            lines = file.read().splitlines()
    except FileNotFoundError:
        print("File not found: " + args[0])
        return 1

    report, valid_count, problem_count = check_registrations(lines)
    for message in report:
        print(message)
    print("Valid registrations: " + str(valid_count))
    print("Total problems: " + str(problem_count))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
