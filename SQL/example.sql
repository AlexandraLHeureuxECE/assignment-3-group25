Create database LMS_1;
use LMS_1;


CREATE TABLE Student(
	studentID INT PRIMARY KEY NOT NULL, 
    fName VARCHAR(50) NOT NULL, 
    lName VARCHAR(50) NOT NULL, 
    email VARCHAR(100) UNIQUE NOT NULL, 
    address TEXT,
    dateOfBirth Date NOT NULL, 
    emergencyContact VARCHAR(20)
);

CREATE TABLE Mentor(
	mentorID INT PRIMARY KEY NOT NULL,
    fName VARCHAR(50) NOT NULL, 
    lName VARCHAR(50) NOT NULL, 
    email VARCHAR(100) UNIQUE NOT NULL, 
    address TEXT,
    dateOfBirth Date, 
    yearsOfExperience INT
);

CREATE TABLE Course(
	courseID INT NOT NULL, 
    courseInstructor INT, 
    semester VARCHAR(255) NOT NULL, 
    courseName VARCHAR(100), 
    courseDescription TEXT,
    prerequisiteCourseID INT,  -- Use a separate column for the prerequisite course ID
    PRIMARY KEY (courseID, semester),
    FOREIGN KEY (courseInstructor) REFERENCES Mentor(mentorID),
    FOREIGN KEY (prerequisiteCourseID, semester) REFERENCES Course(courseID, semester) 
    -- This assumes that the prerequisite course is offered in the same semester
);

-- check self reference

CREATE TABLE ProgressReport(
    courseID INT NOT NULL, 
    studentID INT NOT NULL, 
    semester VARCHAR(255) NOT NULL, 
    assessmentName VARCHAR(255) NOT NULL, 
    assessmentGrade VARCHAR(255),
    assessmentWeight VARCHAR(255),
    comments TEXT,
    PRIMARY KEY (courseID, semester, studentID, assessmentName), -- Corrected spelling here
    FOREIGN KEY (courseID, semester) REFERENCES Course(courseID, semester), -- Composite foreign key reference
    FOREIGN KEY (studentID) REFERENCES Student(studentID)
);


CREATE TABLE Class(
	courseID INT NOT NULL, 
    classDate Date NOT NULL, 
    classDescription VARCHAR(500),
    PRIMARY KEY (courseID, classDate),
    FOREIGN KEY (courseID) REFERENCES Course(courseID)
);

CREATE TABLE Attendance(
	courseID INT NOT NULL,  
    studentID INT NOT NULL, 
    classDate Date NOT NULL,
    PRIMARY KEY (courseID, classDate, studentID),
    FOREIGN KEY (courseID, classDate) REFERENCES Class(courseID, classDate),
    FOREIGN KEY (studentID) REFERENCES Student(studentID)
);


CREATE TABLE Enrollments(
    courseID INT NOT NULL,
    studentID INT NOT NULL, 
    semester VARCHAR(255) NOT NULL, 
    PRIMARY KEY (courseID, semester, studentID),
    FOREIGN KEY (courseID, semester) REFERENCES Course(courseID, semester), -- Composite foreign key
    FOREIGN KEY (studentID) REFERENCES Student(studentID)
);

INSERT INTO Mentor(mentorID, fName, lName, email, address, dateOfBirth, yearsOfExperience)
VALUES 
(1, 'John', 'Doe', 'JohnDoe@gmail.com', '110 Dundas Street', '2003-01-01', 3);


ALTER TABLE Course
DROP FOREIGN KEY course_ibfk_2;

ALTER TABLE Course
ADD CONSTRAINT course_ibfk_2 FOREIGN KEY (prerequisiteCourseID, semester) REFERENCES Course(courseID, semester);

SELECT * FROM Student;

SELECT * FROM Mentor;

SELECT * FROM Enrollments;

SELECT * FROM Course;

SELECT * FROM ProgressReport;

SELECT * FROM Class;

DELETE FROM Student;

INSERT INTO Course(courseInstructor)
SELECT mentorID FROM Mentor;

INSERT INTO Enrollments(courseID, studentID)
SELECT Course.courseID, Student.studentID
FROM Course, Student;

-- Retrieve names and email address students enrolled in a specific course for a particular semester
SELECT 
fName, lName, email
From Student
JOIN Enrollments ON Student.studentID = Enrollments.studentID
-- can change it once we have the dummy data
WHERE Enrollments.courseID = 'CourseID' AND Enrollments.semester = 'Semester'; 

-- Count the number of students enrolled in each semester
SELECT
semester, Count(*) AS NumberofStudents
FROM Enrollments
GROUP BY semester

-- Count number of students in each class 
SELECT
    C.courseID,
    C.classDate,
    COUNT(DISTINCT A.studentID) AS NumberOfStudentsInClass
FROM
    Class AS C
LEFT JOIN
    Attendance AS A ON C.courseID = A.courseID AND C.classDate = A.classDate
GROUP BY
    C.courseID, C.classDate;

-- List progress reports for a specific course, semester, and student, ordered by assessment weight
SELECT assessmentName, assessmentWeight
FROM ProgressReport
WHERE courseID = 'CourseID'
  AND semester = 'Semester'
  AND studentID = 'StudentID'
ORDER BY assessmentWeight;

-- To calculate the final grade for each student in each course
SELECT
    courseID,
    studentID,
    semester,
    SUM(CAST(assessmentGrade AS DECIMAL) * CAST(assessmentWeight AS DECIMAL)) AS FinalGrade
FROM
    ProgressReport 
GROUP BY
    courseID, studentID, semester;

-- Find the mentor with the most years of experience.
SELECT
    fName,
    lName,
    MAX(yearsOfExperience) AS MaxExperience
FROM
    Mentor;

-- List the top 2 courses with the most enrollments
SELECT
    courseID,
    COUNT(*) AS EnrollmentCount
FROM
    Enrollments 
GROUP BY
    courseID
ORDER BY
    EnrollmentCount DESC
LIMIT 2;

-- Retrieve names and email addresses of students enrolled in a specific course for a particular semester
SELECT 
    Student.fName,
    Student.lName,
    Student.email
FROM 
    Student
JOIN 
    Enrollments ON Student.studentID = Enrollments.studentID
WHERE 
    Enrollments.courseID = 1 -- Replace with actual course ID
    AND Enrollments.semester = '2025-1'; -- Replace with actual semester in the format 'YYYY-S'
   

