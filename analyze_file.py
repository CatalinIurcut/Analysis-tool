import subprocess
import re
import requests
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import extract_msg
from mailparser import mailparser
import sys
import webbrowser
from urllib.parse import unquote
from colorama import Fore, Style, init
from email import policy
from email.parser import BytesParser
import dns.resolver
import whois
import os
import readline
import glob

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

def open_links_in_browser(urls):
    for url in urls:
        webbrowser.open(url)

def perform_whois(ip):
    try:
        w = whois.whois(ip)
        return w
    except Exception as e:
        return f"WHOIS lookup failed: {e}"

def analyze_email_headers(file_path):
    with open(file_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    
    spf = dkim = dmarc = arc = "Not checked"
    try:
        spf = "pass" if "spf=pass" in msg['Authentication-Results'] else "fail"
    except TypeError:
        spf = "No SPF found"

    try:
        dkim = "pass" if "dkim=pass" in msg['Authentication-Results'] else "fail"
    except TypeError:
        dkim = "No DKIM found"

    try:
        dmarc = "pass" if "dmarc=pass" in msg['Authentication-Results'] else "fail"
    except TypeError:
        dmarc = "No DMARC found"
    
    try:
        arc = "signed" if "arc=pass" in msg['Authentication-Results'] else "not signed"
    except TypeError:
        arc = "No ARC found"

    return spf, dkim, dmarc, arc

def analyze_file(file_path, options):
    file_type = identify_file_type(file_path)
    print(f"{Fore.YELLOW}File Type: {Fore.GREEN}{file_type}")
    
    text = ""
    urls = []
    
    if file_type.startswith('image'):
        if '-a' in options:
            text = extract_text_from_image(file_path)
            urls = extract_links_from_text(text)
    elif file_type == 'application/pdf':
        if '-a' in options:
            text, urls = extract_text_from_pdf(file_path)
    elif file_type == 'application/vnd.ms-outlook':
        if '-a' in options:
            text, urls = extract_text_from_msg(file_path)
    elif file_type == 'message/rfc822':
        if '-a' in options:
            text, urls = extract_text_from_eml(file_path)
    
    # URL Analysis
    if '-a' in options or '-o' in options:
        print(f"{Fore.YELLOW}{'-'*40}\nURL Analysis:\n{'-'*40}{Style.RESET_ALL}")
        for url in urls:
            decoded_url = decode_safelink(url)
            final_url, status_code = check_url(decoded_url)
            print(f"{Fore.YELLOW}Original URL: {Fore.CYAN}{url}")
            if url != decoded_url:
                print(f"{Fore.YELLOW}Decoded URL: {Fore.CYAN}{decoded_url}")
            print(f"{Fore.YELLOW}Final URL: {Fore.CYAN}{final_url}")
            print(f"{Fore.YELLOW}HTTP Status Code: {Fore.CYAN}{status_code}")
            # Check for tracing pixels
            if "open?" in url or "track" in url:
                print(f"{Fore.RED}Potential Tracing Pixel Detected: {Fore.CYAN}{url}")
            print(f"{Fore.YELLOW}{'-'*40}{Style.RESET_ALL}")

    return urls

def print_grinch():
    grinch = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⢐⣒⣉⣉⣉⣉⣒⡲⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⢊⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣷⣌⡳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠤⠤⠤⠞⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡜⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⢖⣩⣴⣶⣾⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣈⣀⣒⡒⠢⢄⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜⣡⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣍⠢⡄⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⢰⣿⣿⣿⣿⣿⣿⣿⣇⠘⣿⣿⣿⣿⣿⣿⣿⣿⠇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡜⢆⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣈⠛⠿⣿⣿⣿⡿⠋⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡜⣆⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠤⠾⢡⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣦⣤⣬⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⢸⠀
⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⡠⢚⣡⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠈⡆
⠈⣟⠲⢄⡀⠀⠀⣀⠴⢋⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⣻⣶⣬⣽⣿⣿⣿⣿⣿⣿⣿⣿⠀⡇
⠀⠸⡄⣷⣬⣍⣭⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢸⠁
⠀⠀⢳⡸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⢿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢇⡎⠀
⠀⠀⠀⢣⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢟⣥⣶⣿⣿⣿⣶⣌⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢋⡞⠀⠀
⠀⠀⠀⠀⠳⡙⢿⣿⣿⣿⣿⣿⣿⣿⠃⣾⣿⣿⣿⣿⣿⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡙⢿⣿⣿⣿⣿⣿⣿⠿⢋⡵⠋⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠢⣙⠿⢿⣿⣿⣿⣿⡄⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⡮⣭⣉⡭⢭⠔⠚⠁⠀⡀⠀⢰⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠙⠒⠲⠭⠭⠕⢣⡘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⣱⠁⠀⠀⠀⠀⠐⠂⠀⡇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠀⠀⠂⠀⠳⡙⢿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢋⢧⡙⢿⣿⣿⣿⣿⣿⣿⣿⣿⠿⢋⠔⠁⠀⠀⠸⠀⠀⠘⠀⠀⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠢⣝⣛⠛⠛⠛⣛⣋⠥⠚⠁⠀⠉⠒⠬⢭⣛⣛⣛⣫⠭⠔⠊⠁⠀⢰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⢀⠀⠉⢉⠉⢁⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⢰⠀⠀⢀⠀⠀⡆⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠈⠀⠀⠈⠀⠈⠀⠀⠠⠆⠀⠆⠀⠀⠀⠀⠈⠀⠀⠘⠀⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    """
    print(grinch)

def completer(text, state):
    options = [x for x in glob.glob(text + '*')]
    if state < len(options):
        return options[state]
    else:
        return None

def main():
    print_grinch()
    print(f"{Fore.YELLOW}Welcome to the File Analysis Tool!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Commands:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}analyze [options] <file_path>{Style.RESET_ALL} - Analyze a file. Options: -a (all functions), -o (open links), -w (whois), -h (header)")
    print(f"{Fore.CYAN}exit{Style.RESET_ALL} - Exit the application.")
    
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    while True:
        command = input(f"{Fore.CYAN}Enter a command: {Style.RESET_ALL}").strip().lower().split()
        if not command:
            continue

        action = command[0]
        options = command[1:-1]
        file_path = command[-1] if command else None

        if action == "analyze":
            if file_path and not os.path.isabs(file_path):
                file_path = os.path.join(os.getcwd(), file_path)
            if not os.path.exists(file_path):
                print(f"{Fore.RED}File not found: {file_path}{Style.RESET_ALL}")
                continue

            # Perform specified analysis functions
            if '-a' in options or '-o' in options or '-h' in options:
                urls = analyze_file(file_path, options)

            if '-o' in options:
                open_links_in_browser(urls)
            if '-h' in options and (file_path.endswith('.eml') or file_path.endswith('.msg')):
                spf, dkim, dmarc, arc = analyze_email_headers(file_path)
                print(f"{Fore.YELLOW}SPF: {Fore.CYAN}{spf}")
                print(f"{Fore.YELLOW}DKIM: {Fore.CYAN}{dkim}")
                print(f"{Fore.YELLOW}DMARC: {Fore.CYAN}{dmarc}")
                print(f"{Fore.YELLOW}ARC: {Fore.CYAN}{arc}{Style.RESET_ALL}")
            if '-w' in options:
                sender_ip = input(f"{Fore.CYAN}Enter the sender's IP address: {Style.RESET_ALL}").strip()
                whois_info = perform_whois(sender_ip)
                print(f"{Fore.YELLOW}WHOIS Information:\n{whois_info}{Style.RESET_ALL}")

        elif action == "exit":
            break
        else:
            print(f"{Fore.RED}Unknown command: {action}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
