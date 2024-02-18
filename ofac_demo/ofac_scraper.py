import os
import time

import tkinter as tk
from tkinter import ttk

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException


def extract_data_from_row(row):
    """
    Extracts data from a single row (tr element) and returns it as a dictionary.
    
    Input:
        row: BeautifulSoup element representing a single row in the HTML table
        
    Output:
        data: Dictionary containing extracted data from the row
    """
    try:
        columns = row.find_all('td')
        data = {}
        if len(columns) >= 6:
            data['Name'] = columns[0].text.strip()
            data['Link'] = columns[0].find('a')['href'] if columns[0].find('a') else None
            # data['Address'] = columns[1].text.strip()
            data['Type'] = columns[2].text.strip()
            data['Program(s)'] = columns[3].text.strip()
            data['List'] = columns[4].text.strip()
            data['Score'] = columns[5].text.strip()
        return data
    except AttributeError as ae:
        print("No Entinty Foudn for this country", ae)
        return None

def scrape_information_from_page(driver: webdriver):
    """
    Extracts information from the current page and returns it as a dictionary.
    
    Input:
        driver: Selenium WebDriver object
        
    Output:
        details: Dictionary containing details extracted from the page
        aliases: List of dictionaries containing aliases extracted from the page
        addresses: List of dictionaries containing addresses extracted from the page
    """
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    details_table = soup.find('table', class_="MainTable")
    aliases_table = soup.find('table', id="ctl00_MainContent_gvAliases")
    addresses_table = soup.find('div', id="ctl00_MainContent_pnlAddress").find('table')
    # identifications_table = soup.find('table', id="ctl00_MainContent_gvIdentification")

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

    # Extract identifications
    # identifications = []
    # if identifications_table:
    #     for row in identifications_table.find_all('tr')[1:]:
    #         columns = row.find_all('td')
    #         if len(columns) == 5:
    #             identification = {
    #                 'Type': columns[0].text.strip(),
    #                 'ID#': columns[1].text.strip(),
    #                 'Country': columns[2].text.strip(),
    #                 'Issue Date': columns[3].text.strip(),
    #                 'Expire Date': columns[4].text.strip()
    #             }
    #             identifications.append(identification)

    return details, aliases, addresses # , identifications

def update_data(root):
    """
    Updates the data by running the scraper function and then closes the root window.
    
    """
    # Run the scraping script to update the data
    scraper()
    root.destroy()
    

def display_data(root: tk.Tk):
    """
    Displays the data loaded from the CSV file in a new window.
    
    """
    # Load the data from the CSV file
    if os.path.exists("./data/demo.csv"):
        df = pd.read_csv("./data/demo.csv", index_col=0)

        # Create a new window for displaying the data
        display_window = tk.Toplevel(root)
        display_window.title("OFAC Entity List Data")
        display_window.geometry("800x600")  # Set a fixed size for the window

        # Create a canvas for the main window to make it scrollable
        canvas = tk.Canvas(display_window)
        canvas.pack(side="left", fill="both", expand=True)

        # Add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(display_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame inside the canvas to hold the widgets
        scrollable_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="center")

        # Display text above the country dropdown
        select_country_label = tk.Label(scrollable_frame, text="Select country from the dropdown")
        select_country_label.grid(row=0, column=0, padx=10, pady=5)

        # Create a dropdown menu to select countries
        selected_country = tk.StringVar()
        countries = df['Country'].unique().tolist()
        country_dropdown = ttk.Combobox(scrollable_frame, textvariable=selected_country, values=countries)
        country_dropdown.grid(row=1, column=0, padx=10, pady=5)

        # Main Table Heading
        main_table_heading = tk.Label(scrollable_frame, text="Main Table", anchor="center", font=('TkDefaultFont', 10, 'bold'))
        main_table_heading.grid(row=2, column=0, padx=10, pady=5)

        main_frame = tk.Frame(scrollable_frame)
        main_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_table = ttk.Treeview(main_frame, columns=['Name', 'Link', 'Type', 'Program(s)', 'List', 'Score'], show='headings')
        main_table.heading('Name', text='Name')
        main_table.heading('Link', text='Link')
        main_table.heading('Type', text='Type')
        main_table.heading('Program(s)', text='Program(s)')
        main_table.heading('List', text='List')
        main_table.heading('Score', text='Score')
        main_table.grid(row=0, column=0, sticky="nsew")
        main_scroll = ttk.Scrollbar(main_frame, orient="vertical", command=main_table.yview)
        main_scroll.grid(row=0, column=1, sticky="ns")
        main_table.configure(yscrollcommand=main_scroll.set)

        # Instructional label
        instruction_label = tk.Label(scrollable_frame, text="Please select an entry from the main table to show aliases and addresses associated.", anchor="center")
        instruction_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        # Frame for Aliases Table and Addresses Table
        aliases_addresses_frame = tk.Frame(scrollable_frame)
        aliases_addresses_frame.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")
        aliases_addresses_frame.grid_rowconfigure(0, weight=1)
        aliases_addresses_frame.grid_columnconfigure(0, weight=1)

        # Aliases Table Heading
        aliases_table_heading = tk.Label(aliases_addresses_frame, text="Aliases Table", anchor="center", font=('TkDefaultFont', 10, 'bold'))
        aliases_table_heading.grid(row=0, column=0, padx=10, pady=5)

        aliases_frame = tk.Frame(aliases_addresses_frame)
        aliases_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        aliases_frame.grid_rowconfigure(0, weight=1)
        aliases_frame.grid_columnconfigure(0, weight=1)
        aliases_table = ttk.Treeview(aliases_frame, columns=['Type', 'Alias'], show='headings')
        aliases_table.heading('Type', text='Type')
        aliases_table.heading('Alias', text='Alias')
        aliases_table.grid(row=0, column=0, sticky="nsew")
        aliases_scroll = ttk.Scrollbar(aliases_frame, orient="vertical", command=aliases_table.yview)
        aliases_scroll.grid(row=0, column=1, sticky="ns")
        aliases_table.configure(yscrollcommand=aliases_scroll.set)

        # Addresses Table Heading
        addresses_table_heading = tk.Label(aliases_addresses_frame, text="Addresses Table", anchor="center", font=('TkDefaultFont', 10, 'bold'))
        addresses_table_heading.grid(row=0, column=1, padx=10, pady=5)

        addresses_frame = tk.Frame(aliases_addresses_frame)
        addresses_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        addresses_frame.grid_rowconfigure(0, weight=1)
        addresses_frame.grid_columnconfigure(0, weight=1)
        addresses_table = ttk.Treeview(addresses_frame, columns=['Address', 'City', 'State/Province', 'Postal Code', 'Country'], show='headings')
        addresses_table.heading('Address', text='Address')
        addresses_table.heading('City', text='City')
        addresses_table.heading('State/Province', text='State/Province')
        addresses_table.heading('Postal Code', text='Postal Code')
        addresses_table.heading('Country', text='Country')
        addresses_table.grid(row=0, column=0, sticky="nsew")
        addresses_scroll = ttk.Scrollbar(addresses_frame, orient="vertical", command=addresses_table.yview)
        addresses_scroll.grid(row=0, column=1, sticky="ns")
        addresses_table.configure(yscrollcommand=addresses_scroll.set)

        # Update the width of the columns to fit the content
        for col in ['Name', 'Link', 'Type', 'Program(s)', 'List', 'Score']:
            main_table.column(col, width=100, stretch=True)
        for col in ['Type', 'Alias']:
            aliases_table.column(col, width=100, stretch=True)
        for col in ['Address', 'City', 'State/Province', 'Postal Code', 'Country']:
            addresses_table.column(col, width=100, stretch=True)

        def display_selected_country_data(event):
            selected = selected_country.get()
            if selected:
                selected_df = df[df['Country'] == selected]
                main_table.delete(*main_table.get_children())
                for index, row in selected_df.iterrows():
                    main_table.insert('', 'end', values=(row['Name'], row['Link'], row['Type'], row['Program(s)'], row['List'], row['Score']))

        def display_selected_row(event):
            selected_items = main_table.selection()
            if selected_items:
                selected_row = main_table.item(selected_items[0], 'values')
                if selected_row:
                    selected_name = selected_row[0]
                    selected_country = country_dropdown.get()
                    if selected_country:
                        selected_df = df[(df['Country'] == selected_country) & (df['Name'] == selected_name)]
                        aliases_table.delete(*aliases_table.get_children())
                        addresses_table.delete(*addresses_table.get_children())
                        for index, row in selected_df.iterrows():
                            print(row)
                            if type(row['Aliases']) != float:
                                for alias in row['Aliases'].split('; '):
                                    alias_type, alias_name = alias.split(': ')
                                    aliases_table.insert('', 'end', values=(alias_type, alias_name))
                            if type(row['Addresses']) != float:
                                for address in row['Addresses'].split('; '):
                                    parts = address.split(', ')
                                    if len(parts) == 1:
                                        parts = ['', '', '', '', parts[-1].strip()]
                                    if len(parts) == 2:
                                        parts = ['', '', '', parts[-2], parts[-1]]
                                    if len(parts) == 3:
                                        parts = ['', '', parts[-3], parts[-2], parts[-1]]
                                    if len(parts) == 4:
                                        parts = ['', parts[-4], parts[-3], parts[-2], parts[-1]]
                                    addresses_table.insert('', 'end', values=tuple(parts))

        country_dropdown.bind("<<ComboboxSelected>>", display_selected_country_data)
        main_table.bind("<ButtonRelease-1>", display_selected_row)

    else:
        tk.messagebox.showinfo("Info", "No data available. Please click on update data.")

def scraper():
    """
    This function scrapes data from a website and handles exceptions such as network errors and missing data.
    
    It navigates through the OFAC website, extracts data from each row, clicks on the link in each row to get more details,
    extracts information from the new page, and saves the collected data to a CSV file.
    
    """
    try:
        # Initialize the Chrome webdriver
        driver = webdriver.Chrome()
        driver.get("https://sanctionssearch.ofac.treas.gov/")
        time.sleep(5)

        # Find and select the appropriate search options
        country_field = driver.find_element(by=By.ID, value="ctl00_MainContent_ddlCountry")
        type_field = driver.find_element(by=By.NAME, value="ctl00$MainContent$ddlType")
        Select(type_field).select_by_value(value="Entity")
        search_btn = driver.find_element(by=By.ID, value="ctl00_MainContent_btnSearch")

        # Extract countries for search
        countries = [option.text for option in Select(country_field).options if option.text != 'All'][6:8]

        all_data = []

        for country in countries:
    
            country_field = driver.find_element(by=By.ID, value="ctl00_MainContent_ddlCountry")
            search_btn = driver.find_element(by=By.ID, value="ctl00_MainContent_btnSearch")
            Select(country_field).select_by_visible_text(country)
            time.sleep(2)
            search_btn.click()
            time.sleep(3)

            # Parse the page source using BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find all tr elements
            try: 
                rows = soup.find('table', id="gvSearchResults").find_all('tr')

                # Extract data from each row and append to all_data
                for row in rows:
                    try:
                        row_data = extract_data_from_row(row)
                        if row_data and row_data['Link']:
                            # Click on the link
                            link = row_data['Link']
                            driver.find_element(by=By.XPATH, value=f"//a[@href='{link}']").click()
                            time.sleep(5)

                            # Extract information from the new page
                            details, aliases, addresses = scrape_information_from_page(driver)

                            # Update row_data with the extracted details
                            row_data.update(details)

                            # Convert aliases and addresses to a single string
                            aliases_str = '; '.join([f"{alias['Alias_Category']}: {alias['Alias']}" for alias in aliases]) if len(aliases) != 0 else ''
                            addresses_str = '; '.join([f"{address['Address']}, {address['City']}, {address['State/Province']}, {address['Postal Code']}, {address['Country']}" for address in addresses]) \
                                                if len(addresses) != 0 else ''

                            # Add the concatenated strings as new columns to row_data
                            row_data['Aliases'] = aliases_str
                            row_data['Addresses'] = addresses_str
                            row_data['Country'] = country

                            # Append row_data to all_data
                            all_data.append(row_data)

                            # Go back to the previous page
                            driver.back()
                            time.sleep(2)
                    except WebDriverException:
                        # If a network error occurs, retry the current row after a delay
                        print("Network error occurred. Retrying...")
                        time.sleep(5)
                        continue
                    except Exception as e:
                        print(f"Error processing row: {e}")
                        # If an error occurs, go back to the previous page and continue with the next row
                        driver.back()
                        time.sleep(2)
                        continue
                    print(country)
            except AttributeError:
                print("No entinty for", country)
                continue


        driver.quit()

        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(all_data)
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.Addresses = df.Addresses.str.replace(pat=" ,", repl="")
        df.Addresses = df.Addresses.str.strip()
        df.Addresses = df.Addresses.str.strip(',')
        df.Addresses = df.Addresses.str.replace(pat=" ;", repl="")
        df.Addresses = df.Addresses.str.strip(';')
        df.Link = 'https://sanctionssearch.ofac.treas.gov/' + df.Link.astype(str)


        print(df)
        # Save the data to a CSV file
        if not os.path.exists('data'):
            os.makedirs('data')
        df.to_csv('data/demo.csv')

    except Exception as e:
        print(f"An error occurred: {e}")
        
def update_gui(
        update_label: ttk.Label,
        update_button: ttk.Button,
        display_button: ttk.Button,
        root: tk.Tk
):
    """
    Updates the GUI based on the existence of data.
    
    If data exists, it prompts the user to either update or display the data.
    If data doesn't exist, it prompts the user to scrape the data.
    """
    data_exists = os.path.exists("data/demo.csv")
    if data_exists:

        update_label.config(text="Data exists. Do you want to update it or display it?")
        update_button.config(text="Update Data", command=lambda: update_data(root))
        display_button.config(command=lambda: display_data(root))
    else:
        update_label.config(text="Data doesn't exist. Do you want to scrape it?")
        update_button.config(text="Scrape Data", command= lambda: update_data(root))
        display_button.config(state=tk.DISABLED)


def driver_func():
    # Create the main window
    root = tk.Tk()
    root.title("OFAC List GUI")

    # Create variables to track the state of data existence
    data_exists_var = tk.BooleanVar()
    data_exists_var.set(os.path.exists("data/demo.csv"))

    # Create and pack the widgets
    update_label = ttk.Label(root)
    update_label.pack()

    update_button = ttk.Button(root)
    update_button.pack()

    if data_exists_var:
        display_button = ttk.Button(root, text="Display Data", command=lambda: display_data(root), state=tk.ACTIVE)
        display_button.pack()
    else:
        display_button = ttk.Button(root, text="Display Data", command=lambda: display_data(root), state=tk.DISABLED)
        display_button.pack()

    # Update the GUI based on the existence of data
    update_gui(update_label, update_button, display_button, root)

    root.mainloop()

driver_func()