import time
import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor

def gen_random_user_agent() -> str:
    """
    Generates a random user agent using the fake_useragent library.
    
    Output:
        str: Random user agent string.
    """
    return UserAgent().random

def extract_data_from_row(row) -> dict|None:
    """
    Extracts data from a single row (tr element) and returns it as a dictionary.
    
    Input:
        row: BeautifulSoup element representing a single row in the HTML table
        
    Output:
        dict: Dictionary containing extracted data from the row
        None: If no data is found
    """
    try:
        columns = row.find_all('td')
        data = {}
        if len(columns) >= 6:
            data['Name'] = columns[0].text.strip()
            data['Link'] = columns[0].find('a')['href'] if columns[0].find('a') else None
            data['Type'] = columns[2].text.strip()
            data['Program(s)'] = columns[3].text.strip()
            data['List'] = columns[4].text.strip()
            data['Score'] = columns[5].text.strip()
        return data
    except Exception as ae:
        print("No Entity Found for this country", ae)
        return None

def scrape_information_from_page(driver) -> tuple:
    """
    Extracts information from the current page and returns it as a tuple.
    
    Input:
        driver: Selenium WebDriver object
        
    Output:
        tuple: Tuple containing details, aliases, and addresses extracted from the page
    """
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    details_table = soup.find('table', class_="MainTable")
    aliases_table = soup.find('table', id="ctl00_MainContent_gvAliases")
    addresses_table = soup.find('div', id="ctl00_MainContent_pnlAddress").find('table')

    # Extract details
    details = {}
    try:
        for row in details_table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) == 2:
                key = columns[0].text.strip().replace(':', '')
                value = columns[1].text.strip()
                details[key] = value
    except AttributeError as ae:
        print("Details table not found. Moving on to next.", ae)

    # Extract aliases
    aliases = []
    try:
        for row in aliases_table.find_all('tr')[1:]:
            columns = row.find_all('td')
            if len(columns) == 3:
                alias = {'Alias_Category': columns[1].text.strip(), 'Alias': columns[2].text.strip()}
                aliases.append(alias)
    except AttributeError as ae:
        print("Aliases table not found. Moving on to next.", ae)          

    # Extract addresses
    addresses = []
    try:
        for row in addresses_table.find_all('tr')[1:]:
            columns = row.find_all('td')
            if len(columns) == 5:
                address = {
                    'Address': columns[0].text.strip(),
                    'City': columns[1].text.strip(),
                    'State/Province': columns[2].text.strip(),
                    'Postal Code': columns[3].text.strip(),
                    'Country': columns[4].text.strip()
                }
                addresses.append(address)

    except AttributeError as ae:
        print("Address table not found. Moving on to next.", ae)

    return details, aliases, addresses

def scrape_data_for_country(country: str) -> list:
    """
    Scrapes data for a given country.
    
    Input:
        country: Name of the country to scrape data for
    
    Output:
        list: List of dictionaries containing scraped data for the country
    """
    print(country)
    try:
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={gen_random_user_agent()}")
        driver = webdriver.Chrome(options=options)
        driver.get("https://sanctionssearch.ofac.treas.gov/")
        time.sleep(5)

        country_field = driver.find_element(by=By.ID, value="ctl00_MainContent_ddlCountry")
        type_field = driver.find_element(by=By.NAME, value="ctl00$MainContent$ddlType")
        Select(type_field).select_by_value(value="Entity")
        search_btn = driver.find_element(by=By.ID, value="ctl00_MainContent_btnSearch")

        Select(country_field).select_by_visible_text(country)
        time.sleep(2)
        search_btn.click()
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.find('table', id="gvSearchResults").find_all('tr')

        all_data = []

        for row in rows:
            try:
                row_data = extract_data_from_row(row)
                if row_data and row_data['Link']:
                    link = row_data['Link']
                    driver.find_element(by=By.XPATH, value=f"//a[@href='{link}']").click()
                    time.sleep(3)

                    details, aliases, addresses = scrape_information_from_page(driver)

                    row_data.update(details)

                    aliases_str = '; '.join([f"{alias['Alias_Category']}: {alias['Alias']}" for alias in aliases]) if len(aliases) != 0 else ''
                    addresses_str = '; '.join([f"{address['Address']}, {address['City']}, {address['State/Province']}, {address['Postal Code']}, {address['Country']}" for address in addresses]) if len(addresses) != 0 else ''

                    row_data['Aliases'] = aliases_str
                    row_data['Addresses'] = addresses_str
                    row_data['Country'] = country

                    all_data.append(row_data)

                    driver.back()
                    time.sleep(2)
            except WebDriverException as wde:
                print(f"Network error occurred: {wde}. Retrying...")
                time.sleep(5)
                driver.refresh()
                continue
            except Exception as e:
                print(f"Error processing row: {e}")
                driver.back()
                time.sleep(2)
                continue

        driver.quit()
        return all_data
    except Exception as e:
        print(f"An error occurred for {country}: {e}")
        return []

def scrape_data():
    """
    Main function to initiate scraping for all countries in parallel.
    """
    try:
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={gen_random_user_agent()}")
        driver = webdriver.Chrome(options=options)
        driver.get("https://sanctionssearch.ofac.treas.gov/")
        time.sleep(5)

        country_field = driver.find_element(by=By.ID, value="ctl00_MainContent_ddlCountry")
        # Select(country_field).select_by_value(value="Entity")

        countries = [option.text for option in Select(country_field).options if option.text != 'All']

        all_data = []
        driver.quit()

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(scrape_data_for_country, countries)

            for result in results:
                all_data.extend(result)

        df = pd.DataFrame(all_data)
        df.Link = df.Link.apply(lambda link: f'https://sanctionssearch.ofac.treas.gov/{link}')
        df.Addresses = df.Addresses.str.replace(pat=" ,", repl="")
        df.Addresses = df.Addresses.str.strip()
        df.Addresses = df.Addresses.str.strip(',')
        df.Addresses = df.Addresses.str.replace(pat=" ;", repl="")
        df.Addresses = df.Addresses.str.strip(';')
        if not os.path.exists('data'):
            os.makedirs('data')
        df.to_csv('data/sanctions_data.csv', index = False)

    except Exception as e:
        print(f"An error occurred during scraping: {e}")

if __name__ == "__main__":
    scrape_data()

