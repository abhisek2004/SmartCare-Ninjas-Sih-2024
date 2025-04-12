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
app.use(express.static('public'));

// MongoDB Connection
mongoose.connect('mongodb://localhost:27017/passwordResetDB', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

// User Schemas
const DoctorSchema = new mongoose.Schema({
  email: String,
  password: String,
  resetPasswordToken: String,
  resetPasswordExpires: Date
});

const PatientSchema = new mongoose.Schema({
  email: String,
  password: String,
  resetPasswordToken: String,
  resetPasswordExpires: Date
});

const Doctor = mongoose.model('Doctor', DoctorSchema);
const Patient = mongoose.model('Patient', PatientSchema);

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
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Request Reset Endpoint
app.post('/request-reset', async (req, res) => {
  const { email, userType } = req.body;
  let User;

  if (userType === 'doctor') {
    User = Doctor;
  } else if (userType === 'patient') {
    User = Patient;
  } else {
    return res.status(400).send('Invalid user type.');
  }

  const user = await User.findOne({ email });

  if (!user) {
    return res.status(400).send('No user with that email address.');
  }

  const token = crypto.randomBytes(20).toString('hex');
  user.resetPasswordToken = token;
  user.resetPasswordExpires = Date.now() + 3600000; // 1 hour

  await user.save();

  const resetURL = `http://localhost:3000/reset/${token}`;

  await transporter.sendMail({
    to: user.email,
    from: 'your-email@gmail.com',
    subject: 'Password Reset',
    text: `You are receiving this email because you (or someone else) have requested the reset of the password for your account.\n\n` +
          `Please make a POST request to the following link to reset your password:\n\n` +
          `${resetURL}\n\n` +
          `If you did not request this, please ignore this email and your password will remain unchanged.`
  });

  res.status(200).send('Password reset link sent to your email.');
});

// Reset Password Endpoint
app.post('/reset/:token', async (req, res) => {
  const { token } = req.params;
  const { password } = req.body;

  let user;
  let User;

  // Check both collections for the token
  user = await Doctor.findOne({
    resetPasswordToken: token,
    resetPasswordExpires: { $gt: Date.now() }
  });

  if (!user) {
    user = await Patient.findOne({
      resetPasswordToken: token,
      resetPasswordExpires: { $gt: Date.now() }
    });
  }

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
