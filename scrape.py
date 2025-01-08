import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time



url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3822588358&eBP=CwEAAAGNvxVUgYV7zDi_T0A1bs47u2ue9M8BK1fhbJTgXvaPkT8N4S-UenC4I4Z1LwPUvXs4ZMSvjHmiOAjpBi6lucRBH1LAI3ZOIvjERx9lh_99uGWAxTkcw2H0NHB6nxdrU8czH7tp0Dl4VNZzgTvx8xcoiB8Ac1FiAci_oNvLxavCfmZmbek86twGQY7Mr4-IyjpekT9xYnTIR1mhDVEw9ignE9uMNec-hA6JLmNp3_hQjKP6IGpLcQu_ynt6CpmSW_yDa3Tt_ePtlEzD-tGIhuuQDF_BEBLBYKsn462Mbzdj6kKRXGzs2Sg3O3IJaHkg6mRdM1Kbw6eceyCkXId97BgMmJugauhRMRAAJuh1w9p9YTYRgVEbnmWM_Q&refId=rx8GlrbnmyPAipc1Ah71Bw%3D%3D&trackingId=IsBng7m7IyVKsUzLl90YQA%3D%3D"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
}

options = Options()
options.add_argument("--headless")  # Run in headless mode (optional)
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

# Open the URL
driver.get(url)

# Wait for the JavaScript to render
time.sleep(5)  # Adjust the sleep time as needed

# Get the page source and parse it with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

print(soup)
# Print the title of the page
print(soup.title.string)

# Close the browser
driver.quit()