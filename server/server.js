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




// MySQL connection
const db = mysql.createConnection({
   host: 'localhost',
   user: 'root',
   password: '',
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




// Route to get courses taught by a mentor and the students enrolled in those courses
app.get('/get-mentor-courses', (req, res) => {
   const mentorId = req.query.mentorId;


   const query = `
       SELECT c.courseID, c.courseName, s.studentID, s.fName, s.lName
       FROM Course c
       JOIN Enrollments e ON c.courseID = e.courseID
       JOIN Student s ON e.studentID = s.studentID
       WHERE c.courseInstructor = ?
   `;


   db.query(query, [mentorId], (err, results) => {
       if (err) {
           res.status(500).send('Error in database operation');
       } else {
           // Group students by course
           const courses = {};
           results.forEach(row => {
               if (!courses[row.courseID]) {
                   courses[row.courseID] = {
                       courseName: row.courseName,
                       students: []
                   };
               }
               courses[row.courseID].students.push({
                   studentID: row.studentID,
                   fName: row.fName,
                   lName: row.lName
               });
           });


           // Convert to array
           const coursesArray = Object.keys(courses).map(courseID => ({
               courseID: courseID,
               courseName: courses[courseID].courseName,
               students: courses[courseID].students
           }));


           res.json(coursesArray);
       }
   });
});


// Route to add a student to a course
app.post('/add-student', (req, res) => {
   const { studentId, courseId } = req.body;
   const query = 'INSERT INTO Enrollments (courseID, studentID) VALUES (?, ?)';


   db.query(query, [courseId, studentId], (err, result) => {
       if (err) {
           res.status(500).send('Error adding student to course');
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


// ... existing code to start the server ...








// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
