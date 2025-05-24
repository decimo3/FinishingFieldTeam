# Web Automation Project

A Python-based web automation project using Selenium WebDriver. This project provides a high-level interface for web automation tasks with proper resource management and error handling.

## Features

- Simplified web automation interface
- Automatic ChromeDriver management
- Resource cleanup through context manager
- Configurable browser settings
- Headless mode support
- Comprehensive error handling

## Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- ChromeDriver (automatically managed by the project)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/decimo3/FinishingFieldTeam.git
cd FinishingFieldTeam
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
FinishingFieldTeam/
├── src/
│   ├── __init__.py
│   ├── webhandler.py      # Main WebHandler implementation
│   ├── constants.py       # Configuration constants
│   └── chromedriver/      # ChromeDriver storage
├── tests/
│   └── test_webhandler.py # Test suite
├── www/                   # Chrome user data directory
├── requirements.txt
└── README.md
```

## Usage

### Basic Usage

```python
from src.webhandler import WebHandler
from selenium.webdriver.common.by import By

# Initialize the web handler
web_handler = WebHandler()

# Use the web handler with context manager for proper cleanup
with web_handler as driver:
    driver.navigate_to_url("http://example.com")
    element = driver.find_element(By.TAG_NAME, "h1")
    print(element.text)
```

### Headless Mode

```python
# Initialize with headless mode
web_handler = WebHandler(headless=True)
```

### Error Handling

```python
from src.webhandler import WebHandler, WebHandlerError

try:
    with WebHandler() as web_handler:
        web_handler.navigate_to_url("http://example.com")
except WebHandlerError as e:
    print(f"Error occurred: {str(e)}")
```

## Configuration

The project uses the following default configurations in `src/constants.py`:

- Service Port: 7826
- Default Timeout: 300 seconds
- Chrome Data Directory: `www` folder in the project root
- Default Window Size: 1920x1080

You can modify these settings by editing the constants in `src/constants.py`.

## Development

### Running Tests

Run tests using pytest:
```bash
pytest
```

### Code Style

The project follows PEP 8 style guidelines. You can check your code style using:
```bash
pylint src/
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Selenium WebDriver](https://www.selenium.dev/)
- [ChromeDriver](https://chromedriver.chromium.org/)
- [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager) 