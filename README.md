# Programming Fundamentals Quiz Application

A dynamic, interactive quiz application built with Flask. Features include question shuffling, multiple retry attempts, detailed result analysis, and support for multiple quizzes.

## Features

- 📚 **Multiple Quizzes**: Support for multiple quiz files (quiz_data1.json, quiz_data2.json, etc.)
- 🔀 **Shuffled Questions & Answers**: Questions and answer options are randomly shuffled on each quiz start
- 🔄 **Unlimited Retries**: Get unlimited retry rounds until all questions are answered correctly
- 📊 **Detailed Results**: See which questions you got right on first try vs. which ones required retrying
- ⏱️ **Time Tracking**: Tracks how long it takes to complete the quiz
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- ✏️ **Multiple Question Types**: Supports both multiple choice and fill-in-the-blank questions

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/sarahpoulin/programming_quizzes.git
   cd programming_quizzes
   ```

2. **Create a virtual environment** (recommended)
   
   **On Windows:**
   - If you're not sure whether python is installed:
   ```bash
   python --version
   ```
   
   - If it's not:
   - Go to the official Python website:
   - 👉 https://www.python.org/downloads/windows/
   
   - Click "Download Python 3.x.x" (choose the latest stable release).
   - If, after running, you get a popup that asks if you want to allow on Public and Private networks, say yes (this will allow you to be able to connect with your phone).
    
    After installation:
   
   ```bash
   python -m venv prog_env
   prog_env\Scripts\activate
   ```
   
   **On macOS/Linux:**
   ```bash
   python3 -m venv prog_env
   source prog_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   - Local: `http://localhost:5000` (or on Mac,`http://localhost:5001`)
   - Optional: Scan the QR Code to access the quiz with your mobile device!
   
   The application will automatically detect all `quiz_data*.json` files and display them on the quiz selector page.

6. **Subsequent Runs**
   - When you stop the app (ctrl + c), and if you close the terminal, you need to establish your venv or virtual environment, again. First `cd` into `programming_quizzes`:
   
   **Windows**
   ```bash
   prog_env\Scripts\activate
   ```
   
   **macOS/Linux**
   ```bash
   source prog_env/bin/activate
   ```

## How It Works

1. **Quiz Selection**: Users start at the selector page to choose a quiz
2. **Main Quiz**: Questions are presented one at a time in shuffled order
3. **Retry System**: After completing all questions, users are asked to retry any questions they got wrong
4. **Retry Rounds**: This process repeats until all questions are answered correctly
5. **Results**: Detailed results show:
   - Overall score and percentage
   - Questions answered correctly on first try (green)
   - Questions that required retrying (red)
   - Time taken to complete

## Deactivating the Virtual Environment

When you're done, deactivate the virtual environment:

```bash
deactivate
```

## Troubleshooting

**"No quizzes found" error**
- Ensure you have at least one `quiz_data*.json` file in the project root directory

**Port 5000 already in use**
- Edit `app.py` and change `port=5000` (at bottom of script) to another port like `port=5001`

**Python not found**
- Ensure Python is installed and added to your PATH
- Try `python3 app.py` instead of `python app.py`

## OS Compatibility

This application is **cross-platform compatible**:
- ✅ Windows
- ✅ macOS
- ✅ Linux

The main differences are in the virtual environment activation commands (shown above).
