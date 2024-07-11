# Analysis-tool
The File Analysis Tool is a command-line application designed to analyze various file types, such as images, PDFs, and email files (.msg and .eml), for malicious content. The tool extracts text, identifies URLs, and provides insights into email headers, allowing security analysts to quickly assess potential threats. The application also supports opening URLs in a browser and performing WHOIS lookups on IP addresses.

### Required Libraries

Install the required Python libraries using pip:

```
pip install PyMuPDF pytesseract Pillow extract-msg mail-parser requests colorama dnspython python-whois
```

### Inslling dependencies (install_dependencies.sh)

Make the Script Executable:
```
chmod +x install_dependencies.sh
```

Run the Script:

```
./install_dependencies.sh
```


### Example Usage
To run the script from the terminal, navigate to the directory where you saved analyze_file.py and use the following command:

```
python analyze_file.py
```

For example, if you have a file named email.eml in your current directory, you would run:
```
email.eml
```
### Command Options:
-o : Open links in the browser.
-w : Perform WHOIS lookup.
-h : Analyze email header.
