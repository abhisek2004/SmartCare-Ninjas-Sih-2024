const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const crypto = require('crypto');
const bcrypt = require('bcryptjs');
const nodemailer = require('nodemailer');
const path = require('path');

const app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// MongoDB Connection
mongoose.connect('mongodb://localhost:27017/passwordResetDB', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

// User Schema and Model
const UserSchema = new mongoose.Schema({
  email: String,
  password: String,
  resetPasswordToken: String,
  resetPasswordExpires: Date
});

const User = mongoose.model('User', UserSchema);

// Nodemailer Transporter
const transporter = nodemailer.createTransport({
  service: 'Gmail',
  auth: {
    user: 'your-email@gmail.com',
    pass: 'your-email-password'
  }
});

// Serve HTML Page
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset</title>
    </head>
    <body>
        <h1>Password Reset</h1>
        <div id="reset-request-container">
            <h2>Request Password Reset</h2>
            <form id="reset-request-form">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
                <button type="submit">Send Reset Link</button>
            </form>
            <p id="reset-request-message"></p>
        </div>
        <div id="password-reset-container" style="display: none;">
            <h2>Reset Password</h2>
            <form id="reset-password-form">
                <input type="hidden" id="token" name="token" value="">
                <label for="password">New Password:</label>
                <input type="password" id="password" name="password" required>
                <button type="submit">Reset Password</button>
            </form>
            <p id="password-reset-message"></p>
        </div>
        <script>
            document.getElementById('reset-request-form').addEventListener('submit', async (event) => {
                event.preventDefault();
                const email = document.getElementById('email').value;
                const response = await fetch('/request-reset', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email })
                });
                const message = await response.text();
                document.getElementById('reset-request-message').textContent = message;
            });

            const urlParams = new URLSearchParams(window.location.search);
            const token = urlParams.get('token');
            if (token) {
                document.getElementById('reset-request-container').style.display = 'none';
                document.getElementById('password-reset-container').style.display = 'block';
                document.getElementById('token').value = token;
            }

            document.getElementById('reset-password-form').addEventListener('submit', async (event) => {
                event.preventDefault();
                const password = document.getElementById('password').value;
                const token = document.getElementById('token').value;
                const response = await fetch(\`/reset/\${token}\`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ password })
                });
                const message = await response.text();
                document.getElementById('password-reset-message').textContent = message;
            });
        </script>
    </body>
    </html>
  `);
});

// Request Reset Endpoint
app.post('/request-reset', async (req, res) => {
  const { email } = req.body;
  
  const user = await User.findOne({ email });

  if (!user) {
    return res.status(400).send('No user with that email address.');
  }

  const token = crypto.randomBytes(20).toString('hex');

  user.resetPasswordToken = token;
  user.resetPasswordExpires = Date.now() + 3600000; // 1 hour

  await user.save();

  const resetURL = `http://localhost:3000/?token=${token}`;

  await transporter.sendMail({
    to: user.email,
    from: 'your-email@gmail.com',
    subject: 'Password Reset',
    text: `You are receiving this email because you (or someone else) have requested the reset of the password for your account.\n\n` +
          `Please visit the following link to reset your password:\n\n` +
          `${resetURL}\n\n` +
          `If you did not request this, please ignore this email and your password will remain unchanged.`
  });

  res.status(200).send('Password reset link sent to your email.');
});

// Reset Password Endpoint
app.post('/reset/:token', async (req, res) => {
  const { token } = req.params;
  const { password } = req.body;

  const user = await User.findOne({
    resetPasswordToken: token,
    resetPasswordExpires: { $gt: Date.now() }
  });

  if (!user) {
    return res.status(400).send('Password reset token is invalid or has expired.');
  }

  const hashedPassword = await bcrypt.hash(password, 10);

  user.password = hashedPassword;
  user.resetPasswordToken = undefined;
  user.resetPasswordExpires = undefined;

  await user.save();

  res.status(200).send('Password has been successfully updated.');
});

app.listen(3000, () => {
  console.log('Server started on http://localhost:3000');
});
