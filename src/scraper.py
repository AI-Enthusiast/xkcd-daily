"""
XKCD Comic Scraper

This module provides functionality to scrape XKCD comics, including the comic image,
title, and transcript. It can fetch either a specific comic by index or the current
latest comic from the XKCD website.

Usage:
    python scraper.py
"""

import datetime
import os
from typing import Optional, Dict
from bs4 import BeautifulSoup
import requests


# Constants
XKCD_BASE_URL = "https://xkcd.com/"
INVALID_FILENAME_CHARS = ['/', '\\', '?', '%', '*', ':', '|', '"', '<', '>', '.']


def sanitize_filename(filename: str) -> str:
    """
    Remove characters from a string that are invalid in filenames.

    Args:
        filename: The original filename string to sanitize

    Returns:
        A sanitized filename string with invalid characters removed
    """
    return ''.join(char for char in filename if char not in INVALID_FILENAME_CHARS)


def fetch_webpage(url: str) -> Optional[BeautifulSoup]:
    """
    Fetch and parse a webpage into a BeautifulSoup object.

    Args:
        url: The URL of the webpage to fetch

    Returns:
        BeautifulSoup object if successful, None if request fails
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_comic_data(soup: BeautifulSoup) -> Optional[Dict[str, str]]:
    """
    Extract comic data (image URL, title, transcript) from parsed HTML.

    Args:
        soup: BeautifulSoup object containing the parsed XKCD page

    Returns:
        Dictionary containing 'image_url', 'title', and 'transcript' keys,
        or None if extraction fails
    """
    try:
        # Extract image URL
        comic_img = soup.find(id="comic").find("img")
        image_url = comic_img["src"]

        # Extract title
        title = soup.find(id="ctitle").get_text()

        # Extract transcript
        transcript = soup.find(id="transcript").get_text()

        return {
            'image_url': image_url,
            'title': title,
            'transcript': transcript
        }
    except (AttributeError, KeyError, TypeError) as e:
        print(f"Error extracting comic data: {e}")
        return None


def download_image(image_url: str) -> Optional[bytes]:
    """
    Download image data from a URL.

    Args:
        image_url: The URL of the image to download

    Returns:
        Image data as bytes if successful, None if download fails
    """
    # Add https: prefix if not present
    if image_url.startswith("//"):
        image_url = "https:" + image_url

    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Error downloading image from {image_url}: {e}")
        return None


def save_image(image_data: bytes, filepath: str) -> bool:
    """
    Save image data to a file.

    Args:
        image_data: The image data as bytes
        filepath: The path where the image should be saved

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filepath, 'wb') as handler:
            handler.write(image_data)
        return True
    except IOError as e:
        print(f"Error saving image to {filepath}: {e}")
        return False


def save_transcript(transcript: str, filepath: str) -> bool:
    """
    Save comic transcript to a text file.

    Args:
        transcript: The transcript text to save
        filepath: The path where the transcript should be saved

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(transcript)
        return True
    except IOError as e:
        print(f"Error saving transcript to {filepath}: {e}")
        return False


def get_file_extension(url: str) -> str:
    """
    Extract file extension from a URL.

    Args:
        url: The URL to extract extension from

    Returns:
        File extension (e.g., 'png', 'jpg')
    """
    return url.split('.')[-1]


def get_comic(comic_index: int) -> bool:
    """
    Download a specific XKCD comic by index number.

    This function fetches the comic page, extracts the image, title, and transcript,
    and saves them to the current working directory.

    Args:
        comic_index: The index number of the comic to download

    Returns:
        True if successful, False otherwise
    """
    # Construct URL for specific comic
    url = f"{XKCD_BASE_URL}{comic_index}"

    # Fetch and parse the webpage
    soup = fetch_webpage(url)
    if soup is None:
        return False

    # Extract comic data
    comic_data = extract_comic_data(soup)
    if comic_data is None:
        return False

    # Sanitize the title for use as filename
    sanitized_title = sanitize_filename(comic_data['title'])

    # Download the image
    image_data = download_image(comic_data['image_url'])
    if image_data is None:
        return False

    # Save the image
    file_extension = get_file_extension(comic_data['image_url'])
    image_path = f"{sanitized_title}.{file_extension}"
    if not save_image(image_data, image_path):
        return False

    # Save the transcript
    transcript_path = f"{sanitized_title}_transcript.txt"
    if not save_transcript(comic_data['transcript'], transcript_path):
        return False

    print(f"Successfully downloaded comic {comic_index}: {comic_data['title']}")
    return True


def get_current_comic() -> bool:
    """
    Download the current latest XKCD comic.

    This function fetches the XKCD homepage to get the latest comic,
    then downloads the image and transcript to the current working directory.

    Returns:
        True if successful, False otherwise
    """
    # Fetch the main XKCD page
    soup = fetch_webpage(XKCD_BASE_URL)
    if soup is None:
        return False

    # Extract comic data
    comic_data = extract_comic_data(soup)
    if comic_data is None:
        return False

    # Sanitize the title for use as filename
    sanitized_title = sanitize_filename(comic_data['title'])

    # Download the image
    image_data = download_image(comic_data['image_url'])
    if image_data is None:
        return False

    # Save the image
    file_extension = get_file_extension(comic_data['image_url'])
    image_path = f"{sanitized_title}.{file_extension}"
    if not save_image(image_data, image_path):
        return False

    # Optionally save the transcript (not saved in original code, but available)
    # transcript_path = f"{sanitized_title}_transcript.txt"
    # save_transcript(comic_data['transcript'], transcript_path)

    print(f"Successfully downloaded current comic: {comic_data['title']}")
    return True


def setup_daily_directory() -> str:
    """
    Create and return the path to today's data directory.

    Creates a directory structure: data/YYYY-MM-DD/ relative to the project root.

    Returns:
        The absolute path to the created directory
    """
    # Get current date
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Construct path to data directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, 'data', date)

    # Create directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)

    return data_dir


def main():
    """
    Main function to run the daily comic scraper.

    Sets up the daily directory and downloads the current XKCD comic.
    """
    # Create and change to today's data directory
    data_dir = setup_daily_directory()
    os.chdir(data_dir)

    print(f"Saving comic to: {data_dir}")

    # Download the current comic
    success = get_current_comic()

    if success:
        print("Comic download completed successfully!")
    else:
        print("Failed to download comic.")


if __name__ == "__main__":
    main()

