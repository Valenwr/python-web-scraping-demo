# IMDb Movie Web Scraper

This Python script is designed to scrape movie data from IMDb based on a specified genre. It utilizes Selenium and BeautifulSoup to extract detailed information about each movie, including its name, release year, genre, user score, certification, metascore, director, top cast, plot summary, and user reviews. The scraped data is then exported to a CSV file for further analysis.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Disclaimer](#disclaimer)

## Prerequisites

Before using this script, ensure you have the following installed:

- **Python 3.x**: The script is written in Python, so you need to have Python installed on your system.
- **Selenium**: Selenium is used for web scraping automation. You can install it via pip:

  ```bash
  pip install selenium
  ```

- **BeautifulSoup**: BeautifulSoup is a Python library for pulling data out of HTML and XML files. Install it using pip:

  ```bash
  pip install beautifulsoup4
  ```

- **Pandas**: Pandas is a powerful data analysis and manipulation library for Python. You can install it via pip:

  ```bash
  pip install pandas
  ```

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your_username/python-web-scraping-demo.git
   ```

2. **Install dependencies**:

   Navigate to the project directory and install the required dependencies using pip:

   ```bash
   cd python-web-scraping-demo
   pip install -r requirements.txt
   ```

3. **Download and configure ChromeDriver**:

   Download the appropriate version of [ChromeDriver](https://chromedriver.chromium.org/downloads) for your Chrome browser version. Make sure to place the executable file in your system's PATH or specify its path in the script.

## Usage

1. **Modify the genre variable**:

   Open the `web-scraping-demo-imdb.py` script and modify the `genre` variable to specify the genre of movies you want to scrape.

2. **Run the script**:

   Execute the script using the following command:

   ```bash
   python main.py
   ```

3. **Review the scraped data**:

   After the script finishes execution, the scraped movie data will be exported to a CSV file named `movies.csv`.

For your convenience, an example CSV file (example_movies.csv) containing information about 453 movies is provided in the repository. You can use this file to see the expected format of the scraped data and to test your data analysis workflows.

## Disclaimer

This script is provided for educational purposes only. It is meant to demonstrate web scraping techniques using Python and Selenium. It should not be used for commercial purposes or to violate IMDb's terms of service. Ensure compliance with IMDb's robots.txt file and terms of service before using the script. The author assumes no responsibility for any misuse of this script.
