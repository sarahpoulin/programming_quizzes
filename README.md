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
   git clone <repository-url>
   cd prog_fundy_quiz
   ```

2. **Create a virtual environment** (recommended)
   
   **On Windows:**
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
   - Local: `http://localhost:5000`
   - Network: Check the console output for your IP address

The application will automatically detect all `quiz_data*.json` files and display them on the quiz selector page.

## How It Works

1. **Quiz Selection**: Users start at the selector page to choose a quiz
2. **Main Quiz**: Questions are presented one at a time in shuffled order
3. **Retry System**: After completing all questions, users are asked to retry any questions they got wrong
4. **Retry Rounds**: This process repeats until all questions are answered correctly
5. **Results**: Detailed results show:
   - Overall score and percentage
   - Questions answered correctly on first try (green)
   - Questions that required retrying (blue)
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
- Edit `app.py` and change `port=5000` to another port like `port=5001`

**Python not found**
- Ensure Python is installed and added to your PATH
- Try `python3 app.py` instead of `python app.py`

## OS Compatibility

This application is **cross-platform compatible**:
- ✅ Windows
- ✅ macOS
- ✅ Linux

The main differences are in the virtual environment activation commands (shown above).
