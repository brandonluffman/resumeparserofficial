import requests
from bs4 import BeautifulSoup

# URL to scrape
url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3822588358&eBP=CwEAAAGNvxVUgYV7zDi_T0A1bs47u2ue9M8BK1fhbJTgXvaPkT8N4S-UenC4I4Z1LwPUvXs4ZMSvjHmiOAjpBi6lucRBH1LAI3ZOIvjERx9lh_99uGWAxTkcw2H0NHB6nxdrU8czH7tp0Dl4VNZzgTvx8xcoiB8Ac1FiAci_oNvLxavCfmZmbek86twGQY7Mr4-IyjpekT9xYnTIR1mhDVEw9ignE9uMNec-hA6JLmNp3_hQjKP6IGpLcQu_ynt6CpmSW_yDa3Tt_ePtlEzD-tGIhuuQDF_BEBLBYKsn462Mbzdj6kKRXGzs2Sg3O3IJaHkg6mRdM1Kbw6eceyCkXId97BgMmJugauhRMRAAJuh1w9p9YTYRgVEbnmWM_Q&refId=rx8GlrbnmyPAipc1Ah71Bw%3D%3D&trackingId=IsBng7m7IyVKsUzLl90YQA%3D%3D"

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Print the title of the page
    print(soup.title.string)
    
    # You can add more code here to extract other elements from the page
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
