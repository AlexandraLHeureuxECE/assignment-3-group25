//server.js
const express = require('express');
const mysql = require('mysql');
const cors = require('cors');
const bodyParser = require('body-parser');




// Create express app
const app = express();
app.use(cors());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));
app.use(express.json());




// MySQL connection
const db = mysql.createConnection({
   host: 'localhost',
   user: 'root',
   password: 'Amjad1947-',
   database: 'LMS_1'
});


// Connect to MySQL
db.connect(err => {
   if (err) {
       throw err;
   }
   console.log('MySQL connected...');
});


app.get('/get-student-name', (req, res) => {
   db.query('SELECT fName, lName FROM Student WHERE studentID = 1', (err, result) => {
       if (err) {
           throw err;
       }
       if (result.length > 0) {
           res.json(result[0]);
       } else {
           res.status(404).send('Student not found');
       }
   });
});


app.use((req, res, next) => {
   console.log('Method:', req.method);
   console.log('Body:', req.body);
   next();
});
app.post('/login', (req, res) => {
   const { email, password } = req.body;
   let query = `SELECT studentID as id, fName, lName, 'Student' as type FROM Student WHERE email = ? AND password = ?
                UNION
                SELECT mentorID as id, fName, lName, 'Mentor' as type FROM Mentor WHERE email = ? AND password = ?`;


   db.query(query, [email, password, email, password], (err, result) => {
       if (err) {
           res.status(500).send('Error in database operation');
       } else {
           if (result.length > 0) {
               const user = result[0];
               res.json({
                   redirect: user.type === 'Student' ? '/client/studentDash.html' : '/client/mentorDash.html',
                   user: { id: user.id, fName: user.fName, lName: user.lName, type: user.type }
               });
           } else {
               res.status(401).send('Invalid credentials');
           }
       }
   });
});




app.get('/get-mentor-courses', (req, res) => {
    const mentorId = req.query.mentorId;
    const query = `
        SELECT c.courseID, c.semester, c.courseName, s.studentID, s.fName, s.lName
        FROM Course c
        JOIN Enrollments e ON c.courseID = e.courseID AND c.semester = e.semester
        JOIN Student s ON e.studentID = s.studentID
        WHERE c.courseInstructor = ?
    `;
    db.query(query, [mentorId], (err, results) => {
        if (err) {
            res.status(500).send('Error in database operation');
        } else {
            // Group students by course and semester
            const courses = {};
            results.forEach(row => {
                const courseKey = row.courseID + '-' + row.semester;
                if (!courses[courseKey]) {
                    courses[courseKey] = {
                        courseID: row.courseID,
                        semester: row.semester,
                        courseName: row.courseName,
                        students: []
                    };
                }
                courses[courseKey].students.push({
                    studentID: row.studentID,
                    fName: row.fName,
                    lName: row.lName
                });
            });

            // Convert to array
            const coursesArray = Object.keys(courses).map(courseKey => courses[courseKey]);

            res.json(coursesArray);
        }
    });
});



app.post('/add-student', (req, res) => {
    const { studentId, courseId, semester } = req.body;
    const query = 'INSERT INTO Enrollments (courseID, studentID, semester) VALUES (?, ?, ?)';

    db.query(query, [courseId, studentId, semester], (err, result) => {
        if (err) {
            console.error(err); // Log the error to the server console
            res.status(500).send('Error adding student to course: ' + err.message);
        
        } else {
            res.status(200).send('Student added successfully');
        }
    });
});



// Route to remove a student from a course
app.post('/remove-student', (req, res) => {
   const { studentId, courseId } = req.body;
   const query = 'DELETE FROM Enrollments WHERE courseID = ? AND studentID = ?';


   db.query(query, [courseId, studentId], (err, result) => {
       if (err) {
           res.status(500).send('Error removing student from course');
       } else {
           res.status(200).send('Student removed successfully');
       }
   });
});


app.get('/courses', (req, res) => {
    const query = 'SELECT courseID, courseName, semester FROM Course';
    db.query(query, (err, results) => {
        if (err) {
            return res.status(500).send('Error fetching courses: ' + err.message);
        }
        res.json(results);
    });
});





// Add a route to insert a progress report from mentors side 
app.post('/add-progress-report', (req, res) => {
    const { courseID, studentID, semester, assessmentName, assessmentGrade, assessmentWeight, comments } = req.body;

    const query = `
        INSERT INTO ProgressReport (courseID, studentID, semester, assessmentName, assessmentGrade, assessmentWeight, comments)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    `;

    db.query(query, [courseID, studentID, semester, assessmentName, assessmentGrade, assessmentWeight, comments], (err, result) => {
        if (err) {
            console.error('Error adding progress report:', err);
            res.status(500).send('Error adding progress report');
        } else {
            res.status(200).send('Progress report added successfully');
        }
    });
});


app.post('/mark-attendance', (req, res) => {
    const { courseID, classDate, selectedStudents } = req.body;


    // First, check if the class exists
    const checkClassQuery = 'SELECT * FROM class WHERE courseID = ? AND classDate = ?';
    db.query(checkClassQuery, [courseID, classDate], (err, classResults) => {
        if (err) {
            console.error('Database error:', err);
            return res.status(500).json({ error: 'Database error', details: err.message });
        }


        // If class does not exist, insert it
        if (classResults.length === 0) {
            const insertClassQuery = 'INSERT INTO class (courseID, classDate, classDescription) VALUES (?, ?, ?)';
            // Assuming a default description or you can modify to include a description
            db.query(insertClassQuery, [courseID, classDate, 'Default description'], (insertClassErr, insertClassResults) => {
                if (insertClassErr) {
                    console.error('Error inserting class:', insertClassErr);
                    return res.status(500).json({ error: 'Error inserting class', details: insertClassErr.message });
                }
                // Proceed to insert attendance after class insertion
                insertAttendanceRecords(db, courseID, classDate, selectedStudents, res);
            });
        } else {
            // Class exists, directly insert attendance records
            insertAttendanceRecords(db, courseID, classDate, selectedStudents, res);
        }
    });
});


function insertAttendanceRecords(db, courseID, classDate, selectedStudents, res) {
    const attendanceValues = selectedStudents.map(studentID => [courseID, studentID, classDate]);
    const insertAttendanceQuery = 'INSERT INTO Attendance (courseID, studentID, classDate) VALUES ?';


    db.query(insertAttendanceQuery, [attendanceValues], (insertErr, insertResults) => {
        if (insertErr) {
            console.error('Error inserting attendance:', insertErr);
            return res.status(500).json({ error: 'Error inserting attendance', details: insertErr.message });
        }
        // Respond with success and the number of records inserted
        res.json({
            message: 'Attendance marked successfully',
            recordsInserted: insertResults.affectedRows
        });
        console.log(insertResults); // Log the results for more insight


    });


}


app.get('/get-attendance', (req, res) => {
    const { courseID, classDate } = req.query;


    const query = `
        SELECT s.fName, s.lName
        FROM Attendance a
        JOIN Student s ON a.studentID = s.studentID
        WHERE a.courseID = ? AND a.classDate = ?
    `;


    db.query(query, [courseID, classDate], (err, results) => {
        if (err) {
            console.error('Database error:', err);
            return res.status(500).json({ error: 'Database error', details: err.message });
        }
        res.json(results);
    });
});


// Add this route to server.js
app.get('/get-student-courses', (req, res) => {
    const studentId = req.query.studentId;
 
    const query = `
        SELECT c.courseID, c.courseName, c.semester, m.fName as instructorFirstName, m.lName as instructorLastName
        FROM Enrollments e
        JOIN Course c ON e.courseID = c.courseID
        JOIN Mentor m ON c.courseInstructor = m.mentorID
        WHERE e.studentID = ?
    `;
 
    db.query(query, [studentId], (err, results) => {
        if (err) {
            res.status(500).send('Error in database operation');
        } else {
            res.json(results);
        }
    });
 });

// Route to get progress reports for a student in each course
app.get('/get-student-progress-reports', (req, res) => {
    const studentId = req.query.studentId;


    const query = `
        SELECT pr.courseID, c.courseName, pr.semester, pr.assessmentName, pr.assessmentGrade, pr.assessmentWeight, pr.comments
        FROM ProgressReport pr
        JOIN Course c ON pr.courseID = c.courseID
        WHERE pr.studentID = ?
    `;


    db.query(query, [studentId], (err, results) => {
        if (err) {
            res.status(500).send('Error in database operation');
        } else {
            res.json(results);
        }
    });
});

// Route to get final grades for a student in each course
app.get('/get-final-grades', (req, res) => {
    const studentId = req.query.studentId;


    const query = `
        SELECT courseID, studentID, semester,
               SUM(CAST(assessmentGrade AS DECIMAL(10,2)) * (CAST(REPLACE(assessmentWeight, '%', '') AS DECIMAL(10,2)) / 100)) AS finalGrade
        FROM ProgressReport
        WHERE studentID = ?
        GROUP BY courseID, studentID, semester;
    `;


    db.query(query, [studentId], (err, results) => {
        if (err) {
            console.error('Error in database operation:', err);
            res.status(500).send('Error in database operation');
        } else {
            console.log(results); // Log the results
            res.json(results);
        }
    });
});


// Route to get average final grades for each course
app.get('/get-average-final-grades', (req, res) => {
    const query = `
        SELECT courseID, semester, AVG(SUM(CAST(assessmentGrade AS DECIMAL(10,2)) * (CAST(REPLACE(assessmentWeight, '%', '') AS DECIMAL(10,2)) / 100))) AS averageFinalGrade
        FROM ProgressReport
        GROUP BY courseID, semester;
    `;


    db.query(query, (err, results) => {
        if (err) {
            console.error('Error in database operation:', err);
            res.status(500).send('Error in database operation');
        } else {
            console.log(results); // Log the results
            res.json(results);
        }
    });
});


// Route to get overall average grades for all courses
app.get('/get-overall-course-averages', (req, res) => {
    const query = `
        SELECT
            courseID,
            AVG(AverageStudentGrade) AS OverallCourseAverage
        FROM (
            SELECT
                PR.courseID,
                PR.studentID,
                AVG(CAST(PR.assessmentGrade AS DECIMAL(10,2))) AS AverageStudentGrade
            FROM
                ProgressReport AS PR
            GROUP BY
                PR.courseID, PR.studentID
        ) AS Subquery
        GROUP BY
            courseID;
    `;


    db.query(query, (err, results) => {
        if (err) {
            res.status(500).send('Error in database operation');
        } else {
            res.json(results);
        }
    });
});

// Route to calculate overall average assessment grade for each assessment in each course
app.get('/get-overall-assessment-averages', (req, res) => {
    const query = `
        SELECT
            PR.courseID,
            PR.assessmentName,
            AVG(CAST(PR.assessmentGrade AS DECIMAL(10,2))) AS OverallAssessmentAverage
        FROM
            ProgressReport AS PR
        GROUP BY
            PR.courseID, PR.assessmentName;
    `;


    db.query(query, (err, results) => {
        if (err) {
            console.error('Error in database operation:', err);
            res.status(500).send('Error in database operation');
        } else {
            console.log(results); // Log the results
            res.json(results);
        }
    });
});

app.post('/add-progress-report', (req, res) => {
    const { courseID, studentID, semester, assessmentName, assessmentGrade, assessmentWeight, comments } = req.body;
 
 
    const query = `
        INSERT INTO ProgressReport (courseID, studentID, semester, assessmentName, assessmentGrade, assessmentWeight, comments)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    `;
 
 
    db.query(query, [courseID, studentID, semester, assessmentName, assessmentGrade, assessmentWeight, comments], (err, result) => {
        if (err) {
            console.error('Error adding progress report:', err);
            res.status(500).send('Error adding progress report: ' + err.message); // Send back the error message
        } else {
            res.status(200).send('Progress report added successfully');
        }
    });
 });

 
 app.get('/get-mentor-courses-progressReports', (req, res) => {
    const mentorId = req.query.mentorId;
 
 
    const query = `
        SELECT c.courseID, c.semester, c.courseName, s.studentID, s.fName, s.lName
        FROM Course c
        JOIN Enrollments e ON c.courseID = e.courseID AND c.semester = e.semester
        JOIN Student s ON e.studentID = s.studentID
        WHERE c.courseInstructor = ?
    `;
 
 
    db.query(query, [mentorId], (err, results) => {
        if (err) {
            res.status(500).send('Error in database operation');
            return;
        }
        const courses = {};
        results.forEach(row => {
            const courseKey = `${row.courseID}-${row.semester}`;
            if (!courses[courseKey]) {
                courses[courseKey] = {
                    courseID: row.courseID,
                    semester: row.semester,
                    courseName: row.courseName,
                    students: []
                };
            }
            courses[courseKey].students.push({
                studentID: row.studentID,
                fName: row.fName,
                lName: row.lName
            });
        });
        res.json(Object.values(courses));
    });
 });
 

 // Get all courses
app.get('/get-all-courses', (req, res) => {
    // Inside your '/get-all-courses' endpoint
 
 
 const query = `
 SELECT c.courseID, c.courseName, c.courseDescription, c.semester, m.fName, m.lName
 FROM Course c
 JOIN Mentor m ON c.courseInstructor = m.mentorID
 `;
 
 
 
 
    db.query(query, (err, results) => {
        if (err) {
            res.status(500).send('Error in database operation');
        } else {
            res.json(results);
        }
    });
 });

 app.post('/add-student', (req, res) => {
    const { studentId, courseId, semester } = req.body;
    console.log(`Attempting to add student ${studentId} to course ${courseId} for semester ${semester}`);
   
    const query = 'INSERT INTO Enrollments (courseID, studentID, semester) VALUES (?, ?, ?)';
   
    db.query(query, [courseId, studentId, semester], (err, result) => {
        if (err) {
            console.error('Database error:', err);
            res.status(500).send('Error adding student to course: ' + err.code + ' - ' + err.message);
        } else {
            res.status(200).send('Student added successfully');
        }
    });
 });

 app.post('/enroll-course', (req, res) => {
    const { studentId, courseId, semester } = req.body; // Now taking studentId from the body

    // Validate that courseId, studentId and semester are provided
    if (!studentId || !courseId || !semester) {
        return res.status(400).send('Student ID, Course ID and semester are required');
    }

    const query = 'INSERT INTO Enrollments (courseID, studentID, semester) VALUES (?, ?, ?)';

    db.query(query, [courseId, studentId, semester], (err, result) => {
        if (err) {
            console.error('Database error:', err);
            if (err.code === 'ER_DUP_ENTRY') {
                res.status(409).send('You are already enrolled in this course for the specified semester');
            } else {
                res.status(500).send('Error enrolling in course: ' + err.message);
            }
        } else {
            res.status(200).send('Enrollment successful');
        }
    });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
