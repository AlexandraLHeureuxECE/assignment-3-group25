import mysql.connector
from faker import Faker
import random
import datetime

# Database Configuration
config = {
    "user": "root",
    "password": "Hamhar321",
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


# Function to Generate Semester Data
def generate_semester():
    year = random.choice([2022, 2023, 2024, 2025])
    semester = random.choice([1, 2])
    return f"{year}-{semester}"

# Fetch Existing Mentor IDs
cursor.execute("SELECT mentorID FROM Mentor")
mentor_ids = [row[0] for row in cursor.fetchall()]

# Populate Course Table
courses = []  # Array to hold course data
courses_to_add = 40  # Adjust the number of courses as needed
for i in range(1, courses_to_add + 1):
    course_id = i
    course_instructor = random.choice(mentor_ids)
    semester = generate_semester()
    
    # You can generate or define courseName and courseDescription as needed
    course_name = f"Course {i}"  # Example course name
    course_description = "Description of the course"  # Example description

    # For prerequisiteCourseID, either set a valid courseID or NULL
    prerequisite_course_id = None if len(courses) == 0 else random.choice([None, random.randint(1, len(courses))])

    course_data = (
        course_id,
        course_instructor,
        semester,
        course_name,
        course_description,
        prerequisite_course_id
    )
    courses.append(course_data)  # Append to courses list

# Insert Courses into Database
for course in courses:
    insert_course = "INSERT INTO Course (courseID, courseInstructor, semester, courseName, courseDescription, prerequisiteCourseID) VALUES (%s, %s, %s, %s, %s, %s)"
    try:
        cursor.execute(insert_course, course)
    except mysql.connector.Error as err:
        print(f"An error occurred: {err}")

# Fetch Existing Course IDs and Semesters
cursor.execute("SELECT courseID, semester FROM Course")
courses = cursor.fetchall()  # List of tuples (courseID, semester)

# Fetch Existing Student IDs
cursor.execute("SELECT studentID FROM Student")
student_ids = [row[0] for row in cursor.fetchall()]

# Populate Enrollments Table
enrollments = []  # Array to hold enrollment data
enrollments_to_add = 400  # Adjust as needed

enrollment_set = set()  # Use a set to track unique enrollments
while len(enrollments) < enrollments_to_add:
    course_id, semester = random.choice(courses)
    student_id = random.choice(student_ids)
    enrollment = (course_id, student_id, semester)

    # Check for uniqueness before adding
    if enrollment not in enrollment_set:
        enrollment_set.add(enrollment)
        enrollments.append(enrollment)  # Append to enrollments list

# Insert Enrollments into Database
for enrollment in enrollments:
    insert_enrollment = "INSERT INTO Enrollments (courseID, studentID, semester) VALUES (%s, %s, %s)"
    try:
        cursor.execute(insert_enrollment, enrollment)
    except mysql.connector.Error as err:
        print(f"An error occurred: {err}")

# Function to Generate Class Dates
def generate_class_dates(year):
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Using 28 to avoid invalid dates
    return datetime.date(year, month, day)

# Fetch Existing Course IDs and Their Years
cursor.execute("SELECT courseID, semester FROM Course")
course_data = cursor.fetchall()

# Populate Class Table
classes = []  # Array to hold class data
class_dates_per_course = {}  # Dictionary to track class dates for each course
classes_per_course = 30  # Adjust as needed

for course_id, semester in course_data:
    year = int(semester.split('-')[0])  # Extract year from semester
    class_dates_per_course[course_id] = set()  # Initialize an empty set for each course

    while len(class_dates_per_course[course_id]) < classes_per_course:
        class_date = generate_class_dates(year)
        if class_date not in class_dates_per_course[course_id]:
            class_dates_per_course[course_id].add(class_date)
            class_description = f"Description for class on {class_date}"  # Example description
            class_info = (course_id, class_date, class_description)
            classes.append(class_info)  # Append to classes list

# Insert Classes into Database
for class_info in classes:
    insert_class = "INSERT INTO Class (courseID, classDate, classDescription) VALUES (%s, %s, %s)"
    try:
        cursor.execute(insert_class, class_info)
    except mysql.connector.Error as err:
        print(f"An error occurred: {err}")

# Fetch Class Information
cursor.execute("SELECT courseID, classDate FROM Class")
class_info = cursor.fetchall()  # List of tuples (courseID, classDate)

# Fetch Enrollment Information
cursor.execute("SELECT courseID, studentID FROM Enrollments")
enrollment_info = cursor.fetchall()  # List of tuples (courseID, studentID)

# Populate Attendance Table
attendance_records = []  # Array to hold attendance data
attendance_set = set()  # Use a set to track unique attendance records

desired_records = 5000  # Desired number of attendance records

for class_course_id, class_date in class_info:
    for enroll_course_id, student_id in enrollment_info:
        if len(attendance_records) >= desired_records:
            break  # Stop if the desired number of records is reached

        # Match students with the classes they are enrolled in
        if class_course_id == enroll_course_id:
            attendance_record = (class_course_id, student_id, class_date)

            # Check for uniqueness before adding
            if attendance_record not in attendance_set:
                attendance_set.add(attendance_record)
                attendance_records.append(attendance_record)  # Append to attendance records list

# Break out of the nested loop if the desired record count is reached
    if len(attendance_records) >= desired_records:
        break

# Insert Attendance Records into Database
for attendance_record in attendance_records:
    insert_attendance = "INSERT INTO Attendance (courseID, studentID, classDate) VALUES (%s, %s, %s)"
    try:
        cursor.execute(insert_attendance, attendance_record)
    except mysql.connector.Error as err:
        print(f"An error occurred: {err}")


        
# Commit the mentor data
cnx.commit()

# Other parts of the script remain unchanged

# Close Connection
cursor.close()
cnx.close()
