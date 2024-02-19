##################################
##################################
# Author: bakharia
# Date: 02/17/2024
# Name: gui.py
# Description: builds the graphical user interface using Tkinter.  
##################################
##################################
import tkinter as tk
from tkinter import ttk
import os
import pandas as pd
from .scraper import scrape_data

def update_data(root: tk.Tk):
    """
    Updates the data by running the scraper function and then closes the root window.
    
    """
    # Run the scraping script to update the data
    scrape_data()
    root.destroy()
    root = tk.Tk()
    root.title("Data Scraper GUI")

    # Create and place a label
    label = ttk.Label(root, text="Data Scraper GUI")
    label.pack()

    # Create variables to track the state of data existence
    data_exists_var = tk.BooleanVar()
    data_exists_var.set(os.path.exists("data/sanctions_data.csv"))

    # Create and pack the widgets
    update_label = ttk.Label(root)
    update_label.pack()

    # Create and place an "Update Data" button
    update_button = ttk.Button(root, text="Update Data", command=lambda: update_data(root))
    update_button.pack()

    # Create and place a "Display Data" button
    if data_exists_var:
        update_label.config(text="Data exists. Do you want to update it or display it?")
        display_button = ttk.Button(root, text="Display Data", command=lambda: display_data(root), state=tk.ACTIVE)
        display_button.pack()
    else:
        update_label.config(text="Data doesn't exist. Do you want to scrape it?")
        display_button = ttk.Button(root, text="Display Data", command=lambda: display_data(root), state=tk.DISABLED)
        display_button.pack()
    # Run the main event loop
    root.mainloop()

def display_data(root: tk.Tk):
    """
    Displays the data loaded from the CSV file in a new window.
    
    """
   # Load the data from the CSV file
    if os.path.exists("./data/sanctions_data.csv"):
        df = pd.read_csv("./data/sanctions_data.csv")

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

        # Record count label
        records_label = tk.Label(scrollable_frame, text="", anchor="center")
        records_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        # Function to update record count label
        def update_record_count(event):
            selected = selected_country.get()
            # print(selected)
            if selected:
                records_count = len(df[df['Country'] == selected])
                records_label.config(text=f"Records for {selected}: {records_count}")

        main_frame = tk.Frame(scrollable_frame)
        main_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
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
        instruction_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        # Frame for Aliases Table and Addresses Table
        aliases_addresses_frame = tk.Frame(scrollable_frame)
        aliases_addresses_frame.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")
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
        addresses_table = ttk.Treeview(addresses_frame, columns=['Address'], show='headings')
        addresses_table.heading('Address', text='Address')
        addresses_table.grid(row=0, column=0, sticky="nsew")
        addresses_scroll = ttk.Scrollbar(addresses_frame, orient="vertical", command=addresses_table.yview)
        addresses_scroll.grid(row=0, column=1, sticky="ns")
        addresses_table.configure(yscrollcommand=addresses_scroll.set)

        # Update the width of the columns to fit the content
        for col in ['Name', 'Link', 'Type', 'Program(s)', 'List', 'Score']:
            main_table.column(col, width=100, stretch=True)
        for col in ['Type', 'Alias']:
            aliases_table.column(col, width=120, stretch=True)
        addresses_table.column('Address', width=450, stretch=True)  # Adjust width for 'Address' column

        def display_selected_country_data(event):
            selected = selected_country.get()
            if selected:
                update_record_count(event)
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
                            if type(row['Aliases']) != float:
                                for alias in row['Aliases'].split('; '):
                                    alias_type, alias_name = alias.split(': ')
                                    aliases_table.insert('', 'end', values=(alias_type, alias_name))
                            if not isinstance(row['Addresses'], float):
                                for address in row['Addresses'].split('; '):
                                    addresses_table.insert('', 'end', values=(address,))


        country_dropdown.bind("<<ComboboxSelected>>", display_selected_country_data)
        main_table.bind("<ButtonRelease-1>", display_selected_row)

    else:
        tk.messagebox.showinfo("Info", "No data available. Please click on update data.")

def create_gui():
    """
    Creates the GUI window.
    """
    # Create the main window
    root = tk.Tk()
    root.title("Data Scraper GUI")

    # Create and place a label
    # label = ttk.Label(root, text="Data Scraper GUI")
    # label.pack()

    # Create variables to track the state of data existence
    data_exists_var = tk.BooleanVar()
    data_exists_var.set(os.path.exists("data/sanctions_data.csv"))

    # Create and pack the widgets
    update_label = ttk.Label(root)
    update_label.pack()

    # Create and place a "Display Data" button
    # print(data_exists_var.get())
    if data_exists_var.get():
        update_label.config(text="Data exists. Do you want to update it or display it?")
        # Create and place an "Update Data" button
        update_button = ttk.Button(root, text="Update Data", command=lambda: update_data(root))
        # Create and place active Display button
        display_button = ttk.Button(root, text="Display Data", command=lambda: display_data(root), state=tk.ACTIVE)
    else:
        update_label.config(text="Data doesn't exist. Do you want to scrape it?")
        # Create and place an "Update Data" button
        update_button = ttk.Button(root, text="Scrape Data", command=lambda: update_data(root))
        # Create and place DISABLED Display button
        display_button = ttk.Button(root, text="Display Data", command=lambda: display_data(root), state=tk.DISABLED)

    update_button.pack()
    display_button.pack()
    # Run the main event loop
    root.mainloop()

if __name__ == "__main__":
    create_gui()
