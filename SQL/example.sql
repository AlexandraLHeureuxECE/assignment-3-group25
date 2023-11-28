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

-- Insert statements

INSERT INTO Mentor(mentorID, fName, lName, email, address, dateOfBirth, yearsOfExperience)
VALUES 
(1, 'John', 'Doe', 'JohnDoe@gmail.com', '110 Dundas Street', '2003-01-01', 3);

INSERT INTO ProgressReport (courseID, studentID, semester, assessmentName, assessmentGrade, assessmentWeight, comments)
SELECT E.courseID, E.studentID, E.semester, CONCAT('Assessment_', RAND()), NULL, '20%', 'No comments'
FROM Enrollments E
WHERE E.courseID IN (SELECT courseID FROM Course WHERE semester = '2023-1')
LIMIT 5;

INSERT INTO Student (studentID, fName, lName, email, address, dateOfBirth, emergencyContact)
SELECT 
    12345, 
    'Jane',
    'Doe', 
    'jane.doe@example.com',
    '456 Oak Street, Anytown', 
    '1999-04-15', 
    '987-654-3210'
FROM 
    dual
WHERE 
    NOT EXISTS (
        SELECT 1 FROM Student WHERE studentID = 12345
    );

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
    Enrollments.courseID = 1 
    AND Enrollments.semester = '2022-1';
   
   
-- Count the number of students enrolled in each semester
SELECT
    semester,
    COUNT(studentID) AS NumberOfStudents
FROM 
    Enrollments
GROUP BY 
    semester;
   
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
WHERE courseID = 1
  AND semester = '2022-1'
  AND studentID = 8
ORDER BY assessmentWeight;

-- To calculate the final grade for each student in each course
SELECT
    courseID,
    studentID,
    semester,
    SUM(CAST(assessmentGrade AS DECIMAL(10,2)) * (CAST(REPLACE(assessmentWeight, '%', '') AS DECIMAL(10,2)) / 100)) AS FinalGrade
FROM
    ProgressReport
GROUP BY
    courseID, studentID, semester;

-- List the top 2 courses with the most enrollments
SELECT
    E.courseID,
    C.courseName,
    COUNT(*) AS EnrollmentCount
FROM
    Enrollments AS E
JOIN
    Course AS C ON E.courseID = C.courseID
GROUP BY
    E.courseID, C.courseName
ORDER BY
    EnrollmentCount DESC
LIMIT 2;

-- Find the mentor with the most years of experience.
SELECT
    fName,
    lName,
    MAX(yearsOfExperience) AS MaxExperience
FROM
    Mentor;

-- Update Statement 

-- Updating Using Join
UPDATE Course AS C
JOIN Mentor AS M ON C.courseInstructor = M.mentorID
SET C.courseName = CONCAT('New_', C.courseName)
WHERE M.yearsOfExperience > 5; 

-- Updating Based on Another Table
UPDATE Student AS S
JOIN Enrollments AS E ON S.studentID = E.studentID
SET S.emergencyContact = '883-299-9222'
WHERE E.semester = '2022-1';

-- Delete attendance records for a sepcific class 
DELETE FROM Attendance
WHERE courseID = 1 AND classDate = '2023-01-15';