<?php
// login.php
session_start();

// Include the configuration file
require_once 'config.php';

// Enable error reporting for development (remove in production)
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Check if the user is already logged in
if (isset($_SESSION['user_id'])) {
    header("Location: form.php");
    exit();
}

// Check if the form was submitted
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Retrieve and sanitize form data
    $username = trim($_POST['username']);
    $password = $_POST['password'];

    try {
        // Establish a PDO connection
        $pdo = new PDO($dsn, $db_user, $db_pass, $options);

        // Prepare the SELECT statement
        $stmt = $pdo->prepare("SELECT id, password FROM users WHERE username = :username");

        // Bind parameters
        $stmt->bindParam(':username', $username);

        // Execute the statement
        $stmt->execute();

        // Fetch the user record
        $user = $stmt->fetch();

        if ($user && password_verify($password, $user['password'])) {
            // Authentication successful
            session_regenerate_id(true);
            $_SESSION['user_id'] = $user['id'];
            $_SESSION['username'] = $username;

            // Redirect to the protected form page
            header("Location: form.php");
            exit();
        } else {
            // Authentication failed
            $error_message = 'Invalid username or password.';
        }
    } catch (PDOException $e) {
        // Handle errors (avoid displaying sensitive info in production)
        $error_message = 'An error occurred. Please try again later.';
    }
} 
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Welcome Back!</title>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600&display=swap" rel="stylesheet">
    <!-- Font Awesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" integrity="sha512-Fo3rlrZj/k7ujTnHq6RlYmZ4S5I1Y+SnzDw5LcYjKqzZZgox6NroPbZkC3rXx5+VjHwVKVt3iVdqzFONV8S3VA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    <!-- Internal CSS -->
    <style>
        /* Global Styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html, body {
            height: 100%;
            font-family: 'Nunito', sans-serif;
        }

        body {
            /* Background Image */
            background: url('https://images.unsplash.com/photo-1518606371677-2d71f0a9e4e5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80') no-repeat center center fixed;
            background-size: cover;
            position: relative;
        }

        /* Overlay for Background Image */
        body::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5); /* Dark overlay */
            z-index: 1;
        }

        /* Centered Container */
        .login-container {
            position: relative;
            z-index: 2; /* Above the overlay */
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        /* Login Box */
        .login-box {
            background: rgba(255, 255, 255, 0.9);
            padding: 40px 30px;
            border-radius: 10px;
            box-shadow: 0 15px 25px rgba(0, 0, 0, 0.5);
            width: 100%;
            max-width: 400px;
            transition: transform 0.3s ease;
        }

        .login-box:hover {
            transform: translateY(-5px);
        }

        /* Heading */
        .login-box h2 {
            text-align: center;
            margin-bottom: 30px;
            color: #333;
            font-weight: 600;
        }

        /* Input Fields */
        .form-group {
            position: relative;
            margin-bottom: 25px;
        }

        .form-group i {
            position: absolute;
            top: 50%;
            left: 15px;
            transform: translateY(-50%);
            color: #666;
            transition: color 0.3s;
        }

        .form-group input {
            width: 100%;
            padding: 15px 15px 15px 45px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s, box-shadow 0.3s;
        }

        .form-group input:focus {
            border-color: #6c63ff;
            box-shadow: 0 0 5px rgba(108, 99, 255, 0.5);
            outline: none;
        }

        /* Button */
        .btn-login {
            width: 100%;
            padding: 15px;
            background: #6c63ff;
            border: none;
            border-radius: 5px;
            color: #fff;
            font-size: 18px;
            cursor: pointer;
            transition: background 0.3s, transform 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .btn-login:hover {
            background: #5753d9;
            transform: scale(1.02);
        }

        .btn-login i {
            margin-left: 10px;
        }

        /* Error Message */
        .error {
            color: #e74c3c;
            text-align: center;
            margin-bottom: 15px;
            font-weight: 500;
        }

        /* Responsive Design */
        @media (max-width: 480px) {
            .login-box {
                padding: 30px 20px;
            }

            .login-box h2 {
                font-size: 24px;
            }

            .form-group input {
                padding: 12px 12px 12px 40px;
                font-size: 14px;
            }

            .btn-login {
                padding: 12px;
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-box">
            <h2>Welcome Back!</h2>
            
            <?php
            // Display error message if redirected with an error
            if (isset($_GET['error'])) {
                echo '<p class="error">Invalid username or password.</p>';
            }
            ?>
            <form action="login.php" method="POST">
                <div class="form-group">
                    <i class="fas fa-user"></i>
                    <input type="text" id="username" name="username" placeholder="Username" required autofocus>
                </div>
                <div class="form-group">
                    <i class="fas fa-lock"></i>
                    <input type="password" id="password" name="password" placeholder="Password" required>
                </div>
                <button type="submit" class="btn-login">Login <i class="fas fa-sign-in-alt"></i></button>
            </form>
        </div>
    </div>
</body>
</html>

