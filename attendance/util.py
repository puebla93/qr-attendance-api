TEACHERS_EMAIL_ADDRESS = '@matcom.uh.cu'

def is_valid_teacher_email(teacher_email):
    return teacher_email.endswith(TEACHERS_EMAIL_ADDRESS)

def is_valid_student_id(student_id):
    from datetime import datetime

    birthday = student_id[:6]
    try:
        datetime(int("19"+birthday[:2]), int(birthday[2:4]), int(birthday[4:6]))
    except ValueError:
        try:
            datetime(int("20"+birthday[:2]), int(birthday[2:4]), int(birthday[4:6]))
        except ValueError:
            return False

    return True