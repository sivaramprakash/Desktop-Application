# Desktop AI Assistant

A Desktop AI Assistant Application that controls your computer through voice commands or typed commands using natural language.

## Features
- **Voice & Text Input**: Control via microphone or text box.
- **Desktop Control**: Open apps, close apps, type text, click, and take screenshots using PyAutoGUI.
- **Web Browser Automation**: Perform web searches on Google or YouTube and open specific websites using Playwright.
- **Intelligent Parsing**: Understands natural language commands using OpenAI's language models.
- **Memory & History**: Remembers your recent activity and commands.

## Prerequisites
- Windows OS
- Python 3.9 or higher
- An active OpenAI API Key

## Setup Guide

1. **Navigate to the Directory**
   Open PowerShell or Command Prompt and navigate to this folder.

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Add your API Key**
   Open the `.env` file in the project directory and replace the placeholder with your actual OpenAI API Key:
   ```env
   OPENAI_API_KEY=your_actual_key_here
   ```

5. **Run the Application**
   ```bash
   python main.py
   ```

## Usage Examples

Once the GUI opens, you can either click the **🎤 Voice** button to speak a command, or type it into the text box and press Enter.

Try commands like:
- "Open notepad"
- "Open chrome"
- "Search Google for today's weather"
- "Search YouTube for workout music"
- "Open website https://en.wikipedia.org"
- "Take a screenshot"
- "Close application"

## Troubleshooting
- **Microphone issues**: Check if your default recording device is set correctly in Windows Sound Settings.
- **API Key Error**: Ensure `.env` is properly formatted and the key is valid. The `gpt-4o-mini` model is used by default.
