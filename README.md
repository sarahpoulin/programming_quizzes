# Programming Fundamentals Quiz Application

A dynamic, interactive quiz application built with Flask and JavaScript.  
Quizzes are now managed **entirely in the browser using localStorage**, allowing users to upload, delete, and run their own custom quizzes without restarting the server.

---

## 🚀 What’s New (localStorage Mode)

### 🧠 Browser-Stored Quizzes
- Quizzes are stored in **browser localStorage**, not on the server
- Each user can upload and manage their **own personal quizzes**
- No server restart required when adding or removing quizzes

### 📤 Upload Your Own Quizzes
- Upload quiz JSON files directly from the quiz selector page
- Uploaded quizzes persist in your browser until you delete them
- Multiple quizzes can coexist side-by-side

### 🗑️ Delete Quizzes Safely
- Remove quizzes from localStorage with one click
- Deletions affect only **your browser**, not the server or other users

### 🔄 Server Still Handles Logic
Flask continues to manage:
- Question flow and retry rounds
- Scoring and first-attempt tracking
- Session state
- Timing and results calculation

The browser handles:
- Quiz storage
- Quiz selection
- Quiz uploads

---

## ✨ Features

- 📚 **Multiple Quizzes**: Upload and manage multiple quiz files
- 🔀 **Shuffled Questions & Answers**: Randomized each time a quiz starts
- 🔄 **Unlimited Retries**: Retry incorrect questions until all are correct
- 📊 **Detailed Results**:
  - First-attempt correct answers
  - Retried questions
  - Final score and percentage
- ⏱️ **Time Tracking**: Tracks total quiz completion time
- 📱 **Mobile Friendly**: Works on phones, tablets, and desktops
- 📷 **QR Code Access**: Scan to open the quiz on your phone
- ✏️ **Multiple Question Types**:
  - Multiple Choice
  - Multiple Answer
  - Fill-in-the-Blank (including inline blanks)
  - True / False (auto-detected)

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/sarahpoulin/programming_quizzes.git
   cd programming_quizzes
