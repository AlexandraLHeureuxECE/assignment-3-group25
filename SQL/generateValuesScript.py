import mysql.connector
from faker import Faker
import random


# Establishing a Connection
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# Initialize Faker
fake = Faker()

# # Truncate the Mentor and Student tables to clear existing data
# cursor.execute("TRUNCATE TABLE Course;")
# cursor.execute("TRUNCATE TABLE Mentor;")
# cursor.execute("TRUNCATE TABLE Student;")

cnx.commit()  # Commit the changes

# Helper Functions
def generate_date_of_birth_students():
    # Format the date of birth to match the MySQL standard
    return fake.date_of_birth(minimum_age=7, maximum_age=16).strftime("%Y-%m-%d")

# Helper Functions
def generate_date_of_birth_mentors():
    # Format the date of birth to match the MySQL standard
    return fake.date_of_birth(minimum_age=19, maximum_age=35).strftime("%Y-%m-%d")


def generate_phone_number():
    # Generate a string phone number, ensuring it's within a realistic range
    return f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

def generate_unique_email(existing_emails):
    email = fake.email()
    while email in existing_emails:
        email = fake.email()
    return email

# Keep track of all generated emails to ensure uniqueness
generated_emails = set()

# Set to keep track of used student emails to ensure uniqueness
used_student_emails = set()

# Set to keep track of used student IDs to ensure uniqueness
used_student_ids = set(range(1, 301))  # Initialize with all possible student IDs

# ...
# Populate Students
students = []

# Find the highest existing student ID
cursor.execute("SELECT MAX(studentID) FROM Student")
max_student_id = cursor.fetchone()[0] or 0  # Handle the case where there are no students yet

# Set the number of students to add in each run
students_to_add = 100

for i in range(max_student_id + 1, max_student_id + 1 + students_to_add):  # Start from the highest ID + 1
    # Generate student data as before
    student_id = i
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    # Generate a unique email
    email = generate_unique_email(used_student_emails)
    used_student_emails.add(email)
    
    address = fake.address().replace("\n", ", ")
    dob = generate_date_of_birth_students()
    emergency_contact = generate_phone_number()

    student_data = (student_id, first_name, last_name, email, address, dob, emergency_contact)

    insert_student = ("INSERT INTO Student (studentID, fName, lName, email, address, dateOfBirth, emergencyContact) "
                      "VALUES (%s, %s, %s, %s, %s, %s, %s)")
    try:
        cursor.execute(insert_student, student_data)
        cnx.commit()  # Commit after each insert
    except mysql.connector.Error as err:
        print(f"An error occurred: {err}")
        cnx.rollback()  # Rollback in case of error





# Populate Mentors
mentors = []

# Find the highest existing mentor ID
cursor.execute("SELECT MAX(mentorID) FROM Mentor")
max_mentor_id = cursor.fetchone()[0] or 0  # Handle the case where there are no mentors yet

for i in range(max_mentor_id + 1, max_mentor_id + 16):  # Start from the highest ID + 1
    mentor_id = i

    # Generate mentor data
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    address = fake.address().replace("\n", ", ")
    dob = generate_date_of_birth_mentors()
    years_experience = random.randint(1, 40)  # Random years of experience

    # Mentor data tuple
    mentor_data = (mentor_id, first_name, last_name, email, address, dob, years_experience)

    # SQL INSERT statement
    insert_mentor = ("INSERT INTO Mentor (mentorID, fName, lName, email, address, dateOfBirth, yearsOfExperience) "
                     "VALUES (%s, %s, %s, %s, %s, %s, %s)")

    # Execute the SQL statement to insert mentor data
    cursor.execute(insert_mentor, mentor_data)

    # Append mentor data to the mentors list
    mentors.append(mentor_data)

# Now that mentors list is populated, you can use it to select a random mentor as the course instructor

def generate_semester():
    year = random.choice(range(2021, 2024))  # Choose a year between 2021 and 2023
    term = random.choice([1, 2])  # Term 1 or 2
    return f"{year}-{term}"

# Set to keep track of used course semesters to ensure uniqueness
used_course_semesters = set()

# Populate Courses
courses = []
for i in range(100):  # Adjust the range for the number of courses you want
    course_id = i + 1  # Unique course ID
    
    # Generate a unique semester
    semester = generate_semester()
    while semester in used_course_semesters:
        semester = generate_semester()
    used_course_semesters.add(semester)
    
    course_instructor = random.choice(mentors)[0]  # Randomly choose a mentor ID
    course_name = ' '.join(fake.words(nb=3)).title()
    course_description = fake.paragraph(nb_sentences=3)
    
    # Randomly choose a prerequisite course ID from existing courses
    prerequisite_course_id = random.choice([None] + [c[0] for c in courses])  # Include None and existing course IDs

    course_data = (course_id, course_instructor, semester, course_name, course_description, prerequisite_course_id)
    courses.append(course_data)

    insert_course = ("INSERT INTO Course (courseID, courseInstructor, semester, courseName, courseDescription, prerequisiteCourseID) "
                     "VALUES (%s, %s, %s, %s, %s, %s)")
    cursor.execute(insert_course, course_data)




# Get a list of all existing student IDs and course IDs
existing_student_ids = [student[0] for student in students]
existing_course_ids = [course[0] for course in courses]

# Define the number of enrollment records you want to create
num_enrollments = 500  # You can adjust this number as needed

for _ in range(num_enrollments):
    # Randomly choose a student and a course with its semester
    student_id = random.choice(existing_student_ids)
    course_id, course_semester = random.choice(courses)[:2]  # Only get courseID and semester

    # Insert into Enrollments table
    insert_enrollment = ("INSERT INTO Enrollments (courseID, studentID, semester) "
                         "VALUES (%s, %s, %s)")
    enrollment_data = (course_id, student_id, course_semester)

    try:
        cursor.execute(insert_enrollment, enrollment_data)
        cnx.commit()  # Commit after each insert
    except mysql.connector.Error as err:
        print(f"An error occurred: {err}")
        cnx.rollback()  # Rollback in case of error


# Repeat similar steps for other tables, ensuring data consistency
# For example, when populating ProgressReport, use student IDs from the students list

# Committing the transactions
cnx.commit()

# Closing the connection
cursor.close()
cnx.close()
