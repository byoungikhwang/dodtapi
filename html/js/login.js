document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    loginForm.addEventListener('submit', function(event) {
        let isValid = true;

        // Email validation
        if (!emailInput.value.trim()) {
            emailInput.classList.add('is-invalid');
            isValid = false;
        } else if (!isValidEmail(emailInput.value.trim())) {
            emailInput.classList.add('is-invalid');
            isValid = false;
        } else {
            emailInput.classList.remove('is-invalid');
        }

        // Password validation
        if (!passwordInput.value.trim()) {
            passwordInput.classList.add('is-invalid');
            isValid = false;
        } else {
            passwordInput.classList.remove('is-invalid');
        }

        if (!isValid) {
            event.preventDefault(); // Prevent form submission
        } else {
            // In a real application, you would send the form data to the server here
            // For now, we'll just log it and prevent default submission for demonstration
            event.preventDefault();
            alert('Login successful (simulated)! Email: ' + emailInput.value + ', Password: ' + passwordInput.value);
            // Optionally redirect
            // window.location.href = '/dashboard';
        }
    });

    // Function to validate email format
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }

    // Remove validation feedback when user starts typing
    emailInput.addEventListener('input', function() {
        if (emailInput.classList.contains('is-invalid')) {
            emailInput.classList.remove('is-invalid');
        }
    });

    passwordInput.addEventListener('input', function() {
        if (passwordInput.classList.contains('is-invalid')) {
            passwordInput.classList.remove('is-invalid');
        }
    });
});
