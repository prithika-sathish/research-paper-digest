import requests
from bs4 import BeautifulSoup

# Set up your Gemini API key
GEMINI_API_KEY = ""

def fetch_abstract(arxiv_url):
    # Fetch the arXiv page content using requests
    response = requests.get(arxiv_url)
    if response.status_code != 200:
        return f"Error: Unable to fetch {arxiv_url}, status code: {response.status_code}"

    # Parse the HTML content of the arXiv page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the abstract section
    abstract_tag = soup.find('blockquote', class_='abstract mathjax')
    if abstract_tag:
        # Get the content of the abstract and ensure a space after the "Abstract:" label
        abstract_text = abstract_tag.text.strip()
        # Ensure "Abstract:" has a space
        if abstract_text.startswith("Abstract:"):
            abstract_text = abstract_text.replace("Abstract:", "Abstract: ")
        return abstract_text
    else:
        return "Error: Abstract not found."

def summarize_with_gemini(abstract_text):
    # Set up the API endpoint for Gemini
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY
    
    headers = {
        "Content-Type": "application/json",
    }

    # Create the payload to send the abstract to Gemini with a more focused prompt
    data = {
        "contents": [{
            "parts": [{
                "text": f"Summarize the following abstract in 1-2 simple sentences. Focus on what the authors did, why, and the results: \n\n{abstract_text}"
            }]
        }]
    }

    # Make the POST request to the Gemini API
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        # Extract the summary from the response
        result = response.json()
        try:
            # Access the correct keys in the response structure
            summary = result['candidates'][0]['content']['parts'][0]['text']
            return summary
        except KeyError as e:
            return f"KeyError: {e}, check the response structure."
    else:
        return f"Error: Unable to get response, status code: {response.status_code}"

# Open the result file to store the summaries
with open("result.txt", "w") as result_file:
    # Prompt for user input
    print("Select an option:")
    print("1. Enter a single arXiv link")
    print("2. Provide a file with arXiv links (using 'links.txt')")

    option = input("Enter 1 or 2: ")

    if option == '1':
        # Single paper input
        arxiv_url = input("Enter the arXiv URL: ").strip()
        print(f"Fetching abstract for: {arxiv_url}")
        
        # Fetch the abstract
        abstract = fetch_abstract(arxiv_url)
        if not abstract.startswith("Error"):
            # Summarize the abstract using Gemini
            summary = summarize_with_gemini(abstract)
            result_file.write(f"arXiv URL: {arxiv_url}\nSummary: {summary}\n\n")
            print(f"Summary for {arxiv_url}:\n{summary}\n")
        else:
            print(f"Error fetching abstract for {arxiv_url}\n")

    elif option == '2':
        # Multiple papers from file (assuming links.txt)
        file_path = 'links.txt'
        try:
            with open(file_path, 'r') as file:
                links = file.readlines()

            for link in links:
                arxiv_url = link.strip()
                print(f"Fetching abstract for: {arxiv_url}")
                
                # Fetch the abstract
                abstract = fetch_abstract(arxiv_url)
                if not abstract.startswith("Error"):
                    # Summarize the abstract using Gemini
                    summary = summarize_with_gemini(abstract)
                    result_file.write(f"arXiv URL: {arxiv_url}\nSummary: {summary}\n\n")
                    print(f"Summary for {arxiv_url}:\n{summary}\n")
                else:
                    result_file.write(f"arXiv URL: {arxiv_url}\nSummary: Error fetching abstract\n\n")
                    print(f"Error fetching abstract for {arxiv_url}\n")

        except FileNotFoundError:
            print("Error: The file 'links.txt' with arXiv links was not found.")
            result_file.write("Error: The file 'links.txt' with arXiv links was not found.\n")

    else:
        print("Invalid option. Please run the script again and choose option 1 or 2.")