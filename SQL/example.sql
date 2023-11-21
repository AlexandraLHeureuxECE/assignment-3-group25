CREATE TABLE Student(
	studentID INT PRIMARY KEY NOT NULL, 
    fName VARCHAR(50) NOT NULL, 
    lName VARCHAR(50) NOT NULL, 
    email VARCHAR(100) UNIQUE NOT NULL, 
    address TEXT,
    dateOfBirth Date NOT NULL, 
    emergencyContact INT
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
    prerequisite VARCHAR (255),
    PRIMARY KEY (courseID, semester),
    FOREIGN KEY (courseInstructor) REFERENCES Mentor(mentorID),
    FOREIGN KEY (prerequisite) references Course(CourseID) 
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
    PRIMARY KEY (courseID, semester, studentID, assesmentName),
    FOREIGN KEY (courseID) REFERENCES Course(courseID),
	FOREIGN KEY (semester) REFERENCES Course(semester),
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
    FOREIGN KEY (courseID) REFERENCES Course(courseID),
	FOREIGN KEY (classDate) REFERENCES Class(classDate),
	FOREIGN KEY (studentID) REFERENCES Student(studentID)
);

CREATE TABLE Enrollments(
	courseID INT NOT NULL,
    studentID INT NOT NULL, 
    semester VARCHAR(255) NOT NULL, 
    PRIMARY KEY (courseID, semester, studentID),
    FOREIGN KEY (courseID) REFERENCES Course(courseID),
	FOREIGN KEY (semester) REFERENCES Course(semester),
	FOREIGN KEY (studentID) REFERENCES Student(studentID)
);


INSERT INTO Mentor(methorID, fName, lName, email, address, dateOfBirth, yearsOfExperience)
VALUES 
(1, 'John', 'Doe', 'JohnDoe@gmail.com', '110 Dundas Street', 01/01/2003, 3)

INSERT INTO Course(courseInstructor)
SELECT mentorID FROM Mentor;

INSERT INTO Enrollments(courseID,studentID)
SELECT Course.courseID, Student.studentID
FROM Course, Student;
