import mysql.connector
from faker import Faker
import random

# Database Configuration
config = {
    'user': 'root',
    'password': 'Hamhar321',
    'host': 'localhost',
    'database': 'LMS_1',
    'raise_on_warnings': True
}

# Establishing a Connection
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# Initialize Faker
fake = Faker()

# Helper Functions
def generate_date_of_birth():
    # Format the date of birth to match the MySQL standard
    return fake.date_of_birth(minimum_age=7, maximum_age=16).strftime("%Y-%m-%d")

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

# Set to keep track of used student IDs to ensure uniqueness
used_student_ids = set()


# Populate Students
students = []
for i in range(1, 301):  # Starting at 1, up to 300
    student_id = i
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = generate_unique_email(generated_emails)
    generated_emails.add(email)
    address = fake.address().replace("\n", ", ")
    dob = generate_date_of_birth()
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
for _ in range(15):  # Adjust the range based on how many mentors you want
    mentor_id = random.randint(1000, 9999)
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    address = fake.address().replace("\n", ", ")
    dob = generate_date_of_birth()
    years_experience = random.randint(1, 40)  # Random years of experience

    mentor_data = (mentor_id, first_name, last_name, email, address, dob, years_experience)
    mentors.append(mentor_data)

    insert_mentor = ("INSERT INTO Mentor (mentorID, fName, lName, email, address, dateOfBirth, yearsOfExperience) "
                     "VALUES (%s, %s, %s, %s, %s, %s, %s)")
    cursor.execute(insert_mentor, mentor_data)

# def generate_semester():
#     year = random.choice(range(2021, 2024))  # Choose a year between 2021 and 2023
#     term = random.choice([1, 2])  # Term 1 or 2
#     return f"{year}-{term}"

# # Populate Courses
# courses = []
# for i in range(100):  # Adjust the range for the number of courses you want
#     course_id = i + 1  # Unique course ID
#     course_instructor = random.choice(mentors)[0]  # Randomly choose a mentor ID
#     semester = generate_semester()
#     course_name = ' '.join(fake.words(nb=3)).title()
#     course_description = fake.paragraph(nb_sentences=3)
#     prerequisite = random.choice([None, random.choice(courses)[0]]) if courses else None

#     course_data = (course_id, course_instructor, semester, course_name, course_description, prerequisite)
#     courses.append(course_data)

#     insert_course = ("INSERT INTO Course (courseID, courseInstructor, semester, courseName, courseDescription, prerequisite) "
#                      "VALUES (%s, %s, %s, %s, %s, %s)")
#     cursor.execute(insert_course, course_data)

# enrollments = []
# for _ in range(500):  # Adjust as needed for the number of enrollment records you want
#     # Randomly choose a student and a course with its semester
#     student_id = random.choice(students)[0]
#     course_id, course_semester = random.choice(courses)[:2]  # Only get courseID and semester

#     # Insert into Enroll table
#     insert_enroll = ("INSERT INTO Enroll (courseID, studentID, semester) "
#                      "VALUES (%s, %s, %s)")
#     enroll_data = (course_id, student_id, course_semester)
    
#     # Execute the command and add to the enrollments list
#     cursor.execute(insert_enroll, enroll_data)
#     enrollments.append(enroll_data)









# Repeat similar steps for other tables, ensuring data consistency
# For example, when populating ProgressReport, use student IDs from the students list

# Committing the transactions
cnx.commit()

# Closing the connection
cursor.close()
cnx.close()
