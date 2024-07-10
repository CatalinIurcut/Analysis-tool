import subprocess
import re
import requests
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import extract_msg
from mailparser import mailparser
import sys
from urllib.parse import unquote
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

def identify_file_type(file_path):
    result = subprocess.run(['file', '--mime-type', file_path], stdout=subprocess.PIPE)
    mime_type = result.stdout.decode().split(': ')[1].strip()
    return mime_type

def extract_text_from_image(file_path):
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_pdf(file_path):
    text = ""
    urls = []
    with fitz.open(file_path) as pdf_document:
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text += page.get_text()
            links = page.get_links()
            for link in links:
                if link["uri"]:
                    urls.append(link["uri"])
    return text, urls

def extract_text_from_msg(file_path):
    msg = extract_msg.Message(file_path)
    text = msg.body
    urls = extract_links_from_text(text)
    return text, urls

def extract_text_from_eml(file_path):
    parsed_mail = mailparser.parse_from_file(file_path)
    text = parsed_mail.body
    urls = extract_links_from_text(text)
    return text, urls

def extract_links_from_text(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    urls = url_pattern.findall(text)
    return urls

def check_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        final_url = response.url
        return final_url, response.status_code
    except requests.RequestException as e:
        return None, None

def decode_safelink(url):
    if "safelinks.protection.outlook.com" in url:
        url_pattern = re.compile(r"url=(http.+?)&")
        match = url_pattern.search(url)
        if match:
            return unquote(match.group(1))
    return url

def analyze_file(file_path):
    file_type = identify_file_type(file_path)
    print(f"{Fore.YELLOW}File Type: {Fore.GREEN}{file_type}")
    
    text = ""
    urls = []
    
    if file_type.startswith('image'):
        text = extract_text_from_image(file_path)
    elif file_type == 'application/pdf':
        text, urls = extract_text_from_pdf(file_path)
    elif file_type == 'application/vnd.ms-outlook':
        text, urls = extract_text_from_msg(file_path)
    elif file_type == 'message/rfc822':
        text, urls = extract_text_from_eml(file_path)
    
    if not urls:
        urls = extract_links_from_text(text)
    
    print(f"{Fore.YELLOW}Extracted Text:{Style.RESET_ALL} {text[:1000]}")  # Print first 1000 characters of text
    print(f"{Fore.YELLOW}Found URLs:{Style.RESET_ALL} {urls}")
    
    url_details = []
    for url in urls:
        decoded_url = decode_safelink(url)
        final_url, status_code = check_url(decoded_url)
        url_details.append((url, decoded_url, final_url, status_code))
    
    print(f"{Fore.YELLOW}{'-'*40}\nURL Analysis:\n{'-'*40}{Style.RESET_ALL}")
    for original_url, decoded_url, final_url, status_code in url_details:
        print(f"{Fore.YELLOW}Original URL: {Fore.CYAN}{original_url}")
        if original_url != decoded_url:
            print(f"{Fore.YELLOW}Decoded URL: {Fore.CYAN}{decoded_url}")
        print(f"{Fore.YELLOW}Final URL: {Fore.CYAN}{final_url}")
        print(f"{Fore.YELLOW}HTTP Status Code: {Fore.CYAN}{status_code}")
        # Check for tracing pixels
        if "open?" in original_url or "track" in original_url:
            print(f"{Fore.RED}Potential Tracing Pixel Detected: {Fore.CYAN}{original_url}")
        print(f"{Fore.YELLOW}{'-'*40}{Style.RESET_ALL}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"{Fore.RED}Usage: python analyze_file.py <file_path>{Style.RESET_ALL}")
        sys.exit(1)
    file_path = sys.argv[1]
    analyze_file(file_path)
