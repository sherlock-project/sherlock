import tkinter as tk
from tkinter import ttk
import pandas as pd
import webbrowser


def opening_url(url):
    webbrowser.open(url, new=1)


def exists_filter():
    """Apply filter Available | Claimed

    This function will apply filter on exists column.
    It is binded with the Radiobuttons.
    """

    # get filter value
    filter = FILTER.get()
    filtered_data = []
 
    if filter == 'All':
        filtered_data = DATA.copy()
    else:
        for i in range(len(DATA)):
            # Comparing filter and exists value from data
            if filter == str(DATA[i][4]):
                filtered_data.append(DATA[i])

    # Clearing scrollable_frame 
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    # Placing filtered data in scrollable_frame
    for i in range(len(filtered_data)):
        create_row(scrollable_frame, 
                        i,
                        filtered_data[i][0], 
                        filtered_data[i][1], 
                        filtered_data[i][2], 
                        filtered_data[i][3], 
                        filtered_data[i][4], 
                        filtered_data[i][5])


def export_to_excel(data):
    # Export data to excel file
    usernames = []
    names = []
    url_main = []
    url_user = []
    exists = []
    http_status = []

    for i in range(len(data)):
        usernames.append(data[i][0])
        names.append(data[i][1])
        url_main.append(data[i][2])
        url_user.append(data[i][3])
        exists.append(data[i][4])
        http_status.append(data[i][5])

    DataFrame=pd.DataFrame({"username":usernames , "name":names , "url_main":url_main , "url_user":url_user , "exists" : exists , "http_status":http_status})
    DataFrame.to_excel(f'{data[0][0]}.xlsx', sheet_name='sheet1', index=False)


def export_to_csv(data):
    # Export data to csv file
    usernames = []
    names = []
    url_main = []
    url_user = []
    exists = []
    http_status = []

    for i in range(len(data)):
        usernames.append(data[i][0])
        names.append(data[i][1])
        url_main.append(data[i][2])
        url_user.append(data[i][3])
        exists.append(data[i][4])
        http_status.append(data[i][5])

    DataFrame=pd.DataFrame({"username":usernames , "name":names , "url_main":url_main , "url_user":url_user , "exists" : exists , "http_status":http_status})
    DataFrame.to_csv(f'{data[0][0]}.csv', sep='\t', encoding='utf-8')


def create_row(frame, row_index, username, name, url_name, url_user, exists, http_status):
    """Create row 

    Keyword Arguments:
    scrollable_frame       -- Frame where we will place our record.
    username               -- String indicating username that report
                              should be created against.
    url_name               -- URL of main site.
    url_user               -- URL of user on site (if account exists).

    Return Value:
    Frame which can be placed(Append) on scrollable_frame
    """

    label_setting = {
        'borderwidth':1, 
        'relief':"solid",
        'font': ('Helvetica bold', 9)
        }

    label_dimension_setting = {
        "row": row_index,
        "sticky": tk.W, 
        "padx": 5, 
        "pady": 5, 
        "ipadx": 5, 
        "ipady": 2        
    }
   
    username_label = tk.Label(frame, text=username, **label_setting)
    username_label.grid(column=0, **label_dimension_setting)

    name_label = tk.Label(frame, text=name, **label_setting)
    name_label.grid(column=1, **label_dimension_setting)
     
    site_label = tk.Label(frame, text=url_name, **label_setting)
    site_label.grid(column=2, **label_dimension_setting)
     
    url_label = tk.Label(frame, text=url_user, **label_setting)
    url_label.grid(column=3, **label_dimension_setting)

    exists_label = tk.Label(frame, text=exists, **label_setting)
    exists_label.grid(column=4, **label_dimension_setting)

    http_status_label = tk.Label(frame, text=http_status, **label_setting)
    http_status_label.grid(column=5, **label_dimension_setting)

    # Bind mouse click event on site_label and url_label with 
    # opening_url function. 
    site_label.bind('<Button>', lambda event, url=url_name: opening_url(url))
    url_label.bind('<Button>', lambda event, url=url_user: opening_url(url))


def run_gui(data):
    """Display data

    This function will display all data with the help of tkinter.
            
            root
      |-------------|
    header      container
            |--------------|
         canvas          scrollbar
            |
     scrollable_frame(contain main data)
     
    Keyword Arguments:
    data       -- list of list with all findinds.
    """

    # this DATA will be use in filter
    global DATA    
    DATA = data.copy()

    # Main window (root container)
    root = tk.Tk()
    root.title("Sherlok")
    root.geometry('1200x500+100+100')


    # Header
    header = tk.Frame(root, background="grey")
    header.columnconfigure(0, weight=3)
    header.columnconfigure(1, weight=6)
    header.columnconfigure(2, weight=1)
    header.columnconfigure(3, weight=1)
    
    # Title
    title = tk.Label(header, text="SEARCH RESULT", background='grey', fg="white", font=('Roboto bold', 13))
    title.grid(column=0, row=0, sticky=tk.W, ipadx=5, ipady=5)

    # Filter on exists
    global FILTER
    FILTER = tk.StringVar()
    radio_container = tk.Frame(header, background='grey')
    radio_container.columnconfigure(0, weight=3)
    radio_container.columnconfigure(1, weight=1)
    radio_container.columnconfigure(2, weight=1)
    radio_container.columnconfigure(3, weight=1)

    radio_button_settings = {
        "bg":'grey', 
        "fg":"black", 
        "variable":FILTER,
        "command":exists_filter
    }

    all_option = tk.Radiobutton(radio_container, 
                                text="All", 
                                value="All", 
                                **radio_button_settings)
    all_option.grid(column=1, row=0, sticky=tk.W, padx=20, pady=20)

    available_option = tk.Radiobutton(radio_container, 
                                      text="Available", 
                                      value="Available", 
                                      **radio_button_settings)
    available_option.grid(column=2, row=0, sticky=tk.E, padx=20, pady=20)

    claimed_option = tk.Radiobutton(radio_container, 
                                    text="Claimed", 
                                    value="Claimed", 
                                    **radio_button_settings)
    claimed_option.grid(column=3, row=0, sticky=tk.E, padx=20, pady=20)

    radio_container.grid(column=1, row=0)

    # Excel export button                                                                                            
    excel_button = tk.Button(header, text="Excel Export", 
                             background='grey', fg="white", 
                             command=(lambda : export_to_excel(data)) )
    excel_button.grid(column=2, row=0, sticky=tk.NS, padx=20, pady=20)

    # Csv export button
    csv_button = tk.Button(header, text="CSV Export", 
                           background='grey', fg="white", 
                           command=(lambda : export_to_csv(data)))
    csv_button.grid(column=3, row=0, sticky=tk.NS, padx=20, pady=20)

    
    # Data window (display data)
    container = ttk.Frame(root)
    canvas = tk.Canvas(container)

    # Vertical scrollbar
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

    # Frame contains scrolling area
    global scrollable_frame
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.columnconfigure(0, weight=1)
    scrollable_frame.columnconfigure(1, weight=1)
    scrollable_frame.columnconfigure(2, weight=1)
    scrollable_frame.columnconfigure(3, weight=1)
    scrollable_frame.columnconfigure(4, weight=1)
    scrollable_frame.columnconfigure(5, weight=1)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.CENTER, width=1180)
    canvas.configure(yscrollcommand=scrollbar.set)


    # Display all site findings
    for i in range(len(data)):
        create_row(scrollable_frame, 
                        i,
                        data[i][0], 
                        data[i][1], 
                        data[i][2], 
                        data[i][3], 
                        data[i][4], 
                        data[i][5])


    # Placing all the widgets on the root container
    scrollbar.pack(side="right", fill="y")
    header.pack(side=tk.TOP, fill="both")
    canvas.pack(side=tk.LEFT, fill="both", expand=True)
    container.pack(side=tk.BOTTOM, fill="both", expand=True)


    root.mainloop()