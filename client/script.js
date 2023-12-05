const BASE_URL = 'http://localhost:3000'
// document.getElementById('btn').addEventListener('click', function () {
//     fetch(`${BASE_URL}/get-student-name`)
//         .then(response => response.json())
//         .then(data => alert("Student Name: " + data.fName + " " + data.lName))
//         .catch(error => console.error('Error:', error));
// });

document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    var formData = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

    fetch('http://localhost:3000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(formData)
    })

    .then(response => response.json()) // Handle JSON response
    .then(data => {
        if (data.redirect) {
            // Redirect based on the response
            localStorage.setItem('user', JSON.stringify(data.user));
            window.location.href = data.redirect;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});


// Example JavaScript
document.addEventListener('DOMContentLoaded', function() {
    var user = JSON.parse(localStorage.getItem('user'));
    if(user) {
        document.getElementById('userName').textContent = `Welcome, ${user.fName} ${user.lName}`;
    }
});
