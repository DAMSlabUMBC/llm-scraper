# Contributing
Fork and Clone the Repo! 🤗

Follow: https://docs.github.com/en/get-started/quickstart/fork-a-repo

### Prerequisite

1. Docker [[Download]](https://www.docker.com/get-started/)
2. ChromeDriver [[Download]](https://developer.chrome.com/docs/chromedriver/downloads) [[Video]](https://www.youtube.com/watch?v=WnWQgUerR0c)
3. ArrangoDB [Download](https://arangodb.com/download/)

## Local Setup Instructions

### 1. Navigate to the `server` directory
```bash
cd server
```

### 2. Create a virtual environment
Create a virtual environment named `env` to manage dependencies.

```bash
python3 -m venv env
```
or
```bash
python -m venv env
```


### 3. Activate the virtual environment
Activate the environment to start using it.

- On macOS/Linux:
  ```bash
  source env/bin/activate
  ```
- On Windows:
  ```bash
  .\env\Scripts\activate
  ```

### 4. Install dependencies
Install the required Python packages for the scraper to run:

```bash
pip install -r requirements.txt
```

### 5. Create a `.env` file
Create a `.env` file in the `server` directory with the following content:

```bash
OPENAI_API_KEY=your_openai_api_key_here
CHROME_PATH=your_chrome_extension_path_here
```

Replace `your_openai_api_key_here` with your actual OpenAI API key.
Replace `your_chrome_extension_path_here` with your actual OpenAI API key.

### 6. Navigate to the `scripts` directory
```bash
cd scripts
```

### 5. Run the scraper
Run the `main.py` script to start the web scraper.

```bash
python main.py
```

### 7. Select the correct Python interpreter (for Visual Studio Code users)
If you are using Visual Studio Code, make sure to select the correct Python interpreter associated with your virtual environment. You can do this by:

- Pressing `Cmd + Shift + P`, then selecting `Python: Select Interpreter`.
- Choose the interpreter located in the `env/bin/python` folder.
