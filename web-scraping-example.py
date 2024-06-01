from collections import namedtuple
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import os
import time

# Define a named tuple to represent movie data
Movie = namedtuple('Movie', ['name', 'year', 'genre', 'users_score', 'certification', 'metascore', 'director', 'top_cast', 'plot_summary', 'users_reviews'])

def export_to_csv(movie_list, csv_file_path):
    """
    Export movie data to a CSV file.
    
    Args:
        movie_list (list): List of named tuples representing movie data.
        csv_file_path (str): File path for the CSV file.

    Returns:
        str: Success message if export is successful.
    """
    data = []
    for movie in movie_list:
        print(movie.name)
        data.append({
            'Name': str(movie.name),
            'Year': str(movie.year),
            'Genres': str(movie.genre),
            'Users-Score': str(movie.users_score),
            'Certification': str(movie.certification),
            'Metascore': str(movie.metascore),
            'Director': str(movie.director),
            'Top-Cast': str(movie.top_cast),
            'Plot-Summary': str(movie.plot_summary),
            'Users-Reviews':str(movie.users_reviews)
        })
    df = pd.DataFrame(data)
    if os.path.exists(csv_file_path):
        try:
            with open(csv_file_path, 'a', newline='', encoding='utf-8') as existing_file:
                df.to_csv(existing_file, header=False, encoding='utf-8', index=False)
            return 'Information exported successfully'
        except Exception as e:
            print("An error occurred during CSV export:", e)
    else:
        df.to_csv(csv_file_path, encoding='utf-8', index=False)
        return 'Information exported successfully'

def find_movies(soup, driver, num_movies):
    """
    Find and extract link movie.

    Args:
        soup (BeautifulSoup): BeautifulSoup object for the genre page.
        driver (WebDriver): Selenium WebDriver instance.
        num_movies (int): Number of movies to extract.

    Returns:
        list: List of named tuples containing movie data.
    """
    movies_list = []
    try:
        movies = soup.find_all('div', class_='ipc-title ipc-title--base ipc-title--title ipc-title-link-no-icon ipc-title--on-textPrimary sc-b189961a-9 iALATN dli-title')
        for i, movie in enumerate(movies):
            if i >= num_movies:
                break
            link = movie.a['href']
            full_link = f"https://www.imdb.com{link}"
            # Visit the movie page to create a new soup object for each movie
            driver.get(full_link)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
            movie_soup = BeautifulSoup(driver.page_source, 'html.parser')
            movies_list.append((full_link, movie_soup))
        return movies_list
    except Exception as e:
        print(f"An error occurred while extracting movie data: {e}")
        return []

def extract_reviews_link(soup):
    """
    Extract the link to the reviews section from the movie page.

    Args:
        soup (BeautifulSoup): BeautifulSoup object for the movie page.

    Returns:
        str: URL of the reviews section, or None if not found.
    """
    try:
        reviews_button = soup.find('a', href=True, text='User reviews')
        if reviews_button:
            reviews_url = reviews_button['href']
            return f"https://www.imdb.com{reviews_url}"
        else:
            return None
    except Exception as e:
        print(f"An error occurred while extracting the reviews link: {e}")
        return None

def extract_reviews(driver, url):
    """
    Extract user reviews from a movie detail page.

    Args:
        driver (WebDriver): Selenium WebDriver instance.
        url (str): URL of the movie detail page.

    Returns:
        str: User reviews for the movie, or 'N/A' if not found.
    """
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract all user reviews
        review_elements = soup.find_all('div', class_='text show-more__control')
        reviews = [review.text.strip() for review  in review_elements]
        return reviews
    except Exception as e:
        print(f"An error occurred while extracting user reviews: {e}")
        return 'N/A'  

def extract_year_and_certification(soup):
    """
    Extract the year and certification from the movie page.

    Args:
        soup (BeautifulSoup): BeautifulSoup object for the movie page.

    Returns:
        tuple: Year and certification.
    """
    year = 'N/A'
    certification = 'N/A'

    try:
        # Attempt to find the year and certification in the first possible structure
        inline_list = soup.find('ul', class_='ipc-inline-list ipc-inline-list--show-dividers sc-d8941411-2 cdJsTz baseAlt')
        if inline_list:
            year_elements = inline_list.find_all('a', class_='ipc-link ipc-link--baseAlt ipc-link--inherit-color')
            if len(year_elements) >= 1:
                year = year_elements[0].text.strip()
            # Look for certification if available
            if len(year_elements) >= 2:
                certification = year_elements[1].text.strip()

        # If the first structure doesn't provide certification, check the second possible structure
        if certification == 'N/A':
            list_items = inline_list.find_all('li', class_='ipc-inline-list__item')
            if len(list_items) >= 2:
                certification = list_items[1].text.strip()

    except (AttributeError, IndexError) as e:
        print(f'Error extracting year or certification: {e}')

    return year, certification

def extract_movie_details(driver, url, users_reviews):
    """
    Extract detailed movie information from the movie detail page.

    Args:
        driver (WebDriver): Selenium WebDriver instance.
        url (str): URL of the movie detail page.
        users_reviews (list): User reviews for the movie.

    Returns:
        namedtuple: Movie data containing detailed information.
    """
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        # Extract the title
        title = soup.find('h1').text.strip()
        
        # Extract the year and certification
        year, certification = extract_year_and_certification(soup)

        # Extract genres
        try:
            genre_div = soup.find('div', class_='ipc-chip-list__scroller')
            genres = ', '.join([genre.text.strip() for genre in genre_div.find_all('span',  class_='ipc-chip__text')])
        except AttributeError as e:
            genres = 'N/A'
            print(f'Error extracting genres: {e}')
        
        # Extract user score
        users_score = soup.find('span', class_='sc-bde20123-1 cMEQkK').text.strip() if soup.find('span', class_='sc-bde20123-1 cMEQkK') else 'N/A'
        
        # Extract metascore
        metascore = soup.find('span', class_='sc-b0901df4-0 bcQdDJ metacritic-score-box').text.strip() if soup.find('span', class_='sc-b0901df4-0 bcQdDJ metacritic-score-box') else 'N/A'
        
        # Extract director
        director = soup.find('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link').text.strip() if soup.find('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link') else 'N/A'
        
        # Extract top cast
        try:
            cast_items = soup.find_all('div', {'data-testid': 'title-cast-item'})
            top_cast = ', '.join([item.find('a', {'data-testid': 'title-cast-item__actor'}).text.strip() for item in cast_items])
        except (AttributeError, IndexError) as e:
            top_cast = 'N/A'
            print(f'Error extracting top cast: {e}')
        
        # Extract plot summary
        try:
            plot_summary_element = soup.find('span', {'role': 'presentation', 'data-testid': 'plot-xs_to_m'})
            if plot_summary_element:
                plot_summary = plot_summary_element.text.strip()
            else:
                plot_summary = 'N/A'
        except Exception as e:
            plot_summary = 'N/A'
            print(f'Error extracting plot summary: {e}')

        return Movie(title, year, genres, users_score, certification, metascore, director, top_cast, plot_summary, users_reviews)
    except Exception as e:
        print(f"An error occurred while extracting movie details: {e}")
        return None
        
def genre_movie_url(driver, genre, clicks):
    """
    Retrieve BeautifulSoup instance for a specific genre page.

    Args:
        driver (WebDriver): Selenium WebDriver instance.
        genre (str): The genre of movies to retrieve.

    Returns:
        BeautifulSoup: The parsed HTML content of the genre page, or None if the genre is not found.
    """
    try:
        specific_genre_url = f'https://www.imdb.com/search/title/?genres={genre.lower()}&explore=genres&title_type=feature'
        driver.get(specific_genre_url)

        # Handle cookie consent message
        try:
            # Check if either the accept or decline button is present
            accept_button = driver.find_element(By.XPATH, "//button[contains(., 'Accept')]")
            decline_button = driver.find_element(By.XPATH, "//button[contains(., 'Decline')]")
            # Click the decline button to accept the cookie consent message
            accept_button.click()
            print("Cookie consent message accepted by accepting cookies")
        except NoSuchElementException:
            # If the accept button is not found, check for the decline button
            try:
                # Click the decline button to dismiss the cookie consent message
                decline_button()
                print("Cookie consent message dismissed declining cookies")
            except NoSuchElementException:
                # If neither accept nor decline button is found, continue without dismissing the message
                print("Cookie consent message not found")

        # Click the "Load More" button to load more films using JavaScript
        for _ in range(clicks): # times clicked on load more
            try:
                load_more_button = driver.find_element(By.XPATH, "//button[contains(., '50 more')]")
                driver.execute_script("arguments[0].click();", load_more_button)
                print("Clicked 'Load More' button")
                time.sleep(3)  # You can adjust this sleep time if needed
            except NoSuchElementException:
                print("No more 'Load More' button or an error occurred")
                break
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def initialize_driver(driver_path):
    chrome_options = Options()
    # Add the Accept-Language header to the Chrome options
    chrome_options.add_argument('--lang=en-US')
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def main():
    genre = 'Action'
    driver_path = r"C:\Users\Valentina\Desktop\Proyectos\chromedriver-win64\chromedriver.exe"
    csv_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'movies.csv')
    max_movies = 5000
    total_movies_scraped = 0
    save_interval = 200  # Save every 200 movies

    driver = initialize_driver(driver_path)
    try:
        soup = genre_movie_url(driver, genre, clicks=100)
        if soup:
            while total_movies_scraped < max_movies:
                movies_list = find_movies(soup, driver, max_movies - total_movies_scraped)
                if not movies_list:
                    break
                
                movie_data = []
                for link, movie_soup in movies_list:
                    reviews_link = extract_reviews_link(movie_soup)
                    user_reviews = extract_reviews(driver, reviews_link) if reviews_link else 'N/A'
                    movie_details = extract_movie_details(driver, link, users_reviews=user_reviews)
                    if movie_details:
                        movie_data.append(movie_details)
                        total_movies_scraped += 1

                    if total_movies_scraped % save_interval == 0:
                        export_to_csv(movie_data, csv_file_path)
                        movie_data = []  # Clear the batch after saving

                    if total_movies_scraped >= max_movies:
                        break

                    time.sleep(1)
                
                export_to_csv(movie_data, csv_file_path)  # Save any remaining movies at the end

        else:
            print(f"Genre '{genre}' not found.")
    except WebDriverException as e:
        print(f"WebDriver exception occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
