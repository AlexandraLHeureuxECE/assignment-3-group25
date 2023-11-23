import mysql.connector
from faker import Faker
import random

# Database Configuration
config = {
    "user": "root",
    "password": "",
    "host": "localhost",
    "database": "LMS_1",
    "raise_on_warnings": True,
}

# Establishing a Connection
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# Disable foreign key checks
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

tables_to_truncate = [
    "ProgressReport",
    "Enrollments",
    "Class",
    "Attendance",
    "Course",
    "Mentor",
    "Student",
]
for table in tables_to_truncate:
    try:
        cursor.execute(f"TRUNCATE TABLE {table};")
    except mysql.connector.Error as err:
        print(f"An error occurred when truncating {table}: {err}")

# Re-enable foreign key checks
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

cnx.commit()

# Initialize Faker
fake = Faker()


# Helper Functions
def generate_date_of_birth_students():
    return fake.date_of_birth(minimum_age=7, maximum_age=16).strftime("%Y-%m-%d")


def generate_date_of_birth_mentors():
    return fake.date_of_birth(minimum_age=19, maximum_age=50).strftime("%Y-%m-%d")


def generate_phone_number():
    return f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


def generate_unique_email(existing_emails, first_name, last_name):
    email = (
        f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 100)}@example.com"
    )
    while email in existing_emails:
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 100)}@example.com"
    return email


# Sets to keep track of unique values
generated_emails = set()
used_student_emails = set()
used_student_ids = set()
# Initialize the set for tracking existing student IDs
existing_student_ids = set()
# Populate Students
students = []
cursor.execute("SELECT MAX(studentID) FROM Student")
max_student_id = cursor.fetchone()[0] or 0

students_to_add = 100
for i in range(max_student_id + 1, max_student_id + 1 + students_to_add):
    student_id = i
    first_name = fake.first_name()  # Generate first name
    last_name = fake.last_name()  # Generate last name
    email = generate_unique_email(
        used_student_emails, first_name, last_name
    )  # Generate unique email
    used_student_emails.add(email)  # Ensure email uniqueness
    address = fake.address().replace("\n", ", ")  # Generate address
    dob = generate_date_of_birth_students()  # Generate date of birth
    emergency_contact = generate_phone_number()  # Generate emergency contact

    student_data = (
        student_id,
        first_name,
        last_name,
        email,
        address,
        dob,
        emergency_contact,
    )
    students.append(student_data)  # Append to students list

    insert_student = "INSERT INTO Student (studentID, fName, lName, email, address, dateOfBirth, emergencyContact) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    try:
        cursor.execute(insert_student, student_data)
        existing_student_ids.add(student_id)  # Add this line here
    except mysql.connector.Error as err:
        print(f"An error occurred: {err}")

# Commit the student data
cnx.commit()

# Populate Mentors
mentors = []
cursor.execute("SELECT MAX(mentorID) FROM Mentor")
max_mentor_id = cursor.fetchone()[0] or 0

for i in range(max_mentor_id + 1, max_mentor_id + 16):
    mentor_id = i
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    address = fake.address().replace("\n", ", ")
    dob = generate_date_of_birth_mentors()
    years_experience = random.randint(1, 40)

    mentor_data = (
        mentor_id,
        first_name,
        last_name,
        email,
        address,
        dob,
        years_experience,
    )
    mentors.append(mentor_data)  # Append to mentors list

    insert_mentor = "INSERT INTO Mentor (mentorID, fName, lName, email, address, dateOfBirth, yearsOfExperience) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    try:
        cursor.execute(insert_mentor, mentor_data)
    except mysql.connector.Error as err:
        print(f"An error occurred: {err}")

# Commit the mentor data
cnx.commit()

# Other parts of the script remain unchanged

# Close Connection
cursor.close()
cnx.close()
