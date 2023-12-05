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
    password: 'mARINA24222!',
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
    let query = `SELECT 'Student' as type FROM Student WHERE email = ? AND password = ?
                 UNION
                 SELECT 'Mentor' as type FROM Mentor WHERE email = ? AND password = ?`;

    db.query(query, [email, password, email, password], (err, result) => {
        if (err) {
            res.status(500).send('Error in database operation');
        } else {
            if (result.length > 0) {
                if (result[0].type === 'Student') {
                    res.json({ redirect: '/client/studentDash.html' });
                } else if (result[0].type === 'Mentor') {
                    res.json({ redirect: '/client/mentorDash.html' });
                }
            } else {
                res.status(401).send('Invalid credentials');
            }
        }
    });
});



// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
