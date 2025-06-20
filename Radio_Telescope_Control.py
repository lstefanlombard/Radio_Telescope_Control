import tkinter as tk
from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename
import sys, traceback, time, re, os, csv ,requests

#############
####SETUP####
#############

global My_Mount
My_Mount="ASCOM.OnStep.Telescope" # Change for your mount
IF_Avarage_Path= r'C:\Users\lstef\OneDrive\Desktop\Radiotelescope' # Change this to the path that if avarage outputs the data to

#############

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Error: watchdog module not found. Please install it using 'pip install watchdog'.")
    exit(1)
#constants
SettelTime=5
logra=0
logdec=0
WATCH_FOLDER = IF_Avarage_Path  # Update with the correct folder path
CSV_PATH = 'output.csv'  # Update with your desired output CSV file path

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, observer):
        super().__init__()
        self.file_count = 0                     
        self.observer = observer
        
    def on_created(self, event):
        if not event.is_directory:
            self.file_count += 1
            print(f'File detected: {event.src_path} (Count: {self.file_count})')
            # Check if it is the second file after movement
            if self.file_count == 2:
                print(f'Saving file: {event.src_path}')
                save_to_csv(event.src_path, logra, logdec)  # Pass ra and dec values here
                self.observer.stop()  # Stop the observer to allow the mount to move again

# Function to save file content to CSV
def save_to_csv(file_path, logra, logdec):
    # Read the file and extract data
    print(logra)
    print(logdec)
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Extract frequency and intensity from the lines (skip the header line)
    freq_intensity = [
        line.split() for line in lines if line.strip() and 'Counts' not in line
    ]

    # Get the frequencies as column headers (first column from each line)
    frequencies = [row[0] for row in freq_intensity]

    # Get the intensities as data (second column from each line)
    intensities = [row[1] for row in freq_intensity]

    # Check if the file already exists and needs a header
    header_needed = not os.path.isfile(CSV_PATH)

    # Open the CSV file for appending
    with open(CSV_PATH, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # Write the header if the file is new
        if header_needed:
            writer.writerow(['ra', 'dec'] + frequencies)

        # Write the data row with ra and dec values
        writer.writerow([logra, logdec] + intensities)

    print(f'Saved to {CSV_PATH}')

# Function to start monitoring the folder
def start_monitoring():
    observer = Observer()
    event_handler = NewFileHandler(observer)  # Create handler with the observer
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()
    print('Monitoring started...')
    try:
        while observer.is_alive():
            time.sleep(1)
            root.update()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print("Monitoring stopped.")

# Function to initiate the process after movement
def wait_for_files():
    print('Movement completed. Starting to watch for files...')
    start_monitoring()
    
def wait_for_setteling(): #setteling time animation instead of just a normal time.sleep
    for i in range(SettelTime):
        print(f"\rSetteling{'.' * (i % 4)}", end="\n")
        time.sleep(0.3)
        root.update()
# Show Save As dialog when
# Global variable
path = ""

def Save_As():
    global path  # Declare the global variable to update it

    root = Tk()
    root.withdraw()  # Hide the root window

    file_path = asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        title="Save log file as"
    )

    # Check if the user selected a file
    if not file_path:
        print("No file selected. Exiting.")
        exit()

    path = file_path  # Update the global variable
    print(f"Selected file path: {path}")

# Use this function throughout your script
def log_message(message):
    with open(path, "a") as f:
        f.write(datetime.now().strftime("%H:%M:%S") + " " + message + "\n")
        root.update()

def convert_ra_dec_to_decimal(ra, dec):
    #"""Convert RA and Dec from string formats to decimal values."""
    def hms_to_decimal(ra_hms):
        #"""Convert RA in hms format (e.g., '12h27m56.15s') to decimal hours."""
        matches = re.findall(r'(\d+\.?\d*)', ra_hms)
        if len(matches) == 3:
            h, m, s = map(float, matches)
        elif len(matches) == 2:  # If seconds are missing
            h, m = map(float, matches)
            s = 0.0
        elif len(matches) == 1:  # If only hours are provided
            h = float(matches[0])
            m = s = 0.0
        else:
            raise ValueError("Invalid RA format")
        return h + m / 60 + s / 3600

    def dms_to_decimal(dec_dms):
        """Convert Dec in dms format (e.g., '-63°13'00.0"') to decimal degrees."""
        sign = -1 if '-' in dec_dms else 1
        matches = re.findall(r'(\d+\.?\d*)', dec_dms)
        if len(matches) == 3:  # Degrees, minutes, and seconds
            degrees, minutes, seconds = map(float, matches)
        elif len(matches) == 2:  # Degrees and minutes, seconds default to 0
            degrees, minutes = map(float, matches)
            seconds = 0.0
        elif len(matches) == 1:  # Only degrees are provided
            degrees = float(matches[0])
            minutes = seconds = 0.0
        else:
            raise ValueError("Invalid Dec format")
        return sign * (degrees + minutes / 60 + seconds / 3600)

    try:
        ra_decimal = hms_to_decimal(ra)
        dec_decimal = dms_to_decimal(dec)
        return ra_decimal, dec_decimal
    except Exception as e:
        print(f"Error converting RA/Dec: {e}")
        return None, None

def Start_Scan():
    print(path)
    ra = ra_entry.get()  # get ra from entry
    dec = dec_entry.get()  # get dec from entry
    ra_decimal, dec_decimal = convert_ra_dec_to_decimal(ra, dec)  # convert to desimal
    ra_scan_size = float(ra_scan_size_entry.get())  # get from entry
    ra_scan_size = ra_scan_size / 15 # experimental convert degrres to hours
    dec_scan_size = float(dec_scan_size_entry.get())  # get from entry
    ra_step = float(ra_steps_entry.get())  # get from entry
    ra_step = ra_step/15 # experimental convert degrres to hour
    dec_step = float(dec_steps_entry.get())  # get from entry
    ra_start = ra_decimal - (ra_scan_size / 2)  # take calculate the scan start and scan end
    ra_end = ra_decimal + (ra_scan_size / 2)  # take calculate the scan start and scan end
    dec_start = dec_decimal - (dec_scan_size / 2)  # take calculate the scan start and scan end
    dec_end = dec_decimal + (dec_scan_size / 2)  # take calculate the scan start and scan end
    Scantime_delay = float(scan_time_entry.get())# get scantime from entry
    total=int(Scantime_delay)
    import win32com.client
    import time

    #ra_step = 1  # 15 Increment for RA in degrees # for debug perpouses
    #dec_step = 15  # Increment for Dec in degrees # for debug perpouses

    # Connect to the ASCOM Telescope Driver
    telescope = win32com.client.Dispatch(My_Mount)
    telescope.Connected = True
    print("Telescope connected successfully")

    # Define helper functions
    def setteling():
        log_message(" Settling Start") #writes movement and timestamp to a file for later prosesing
        wait_for_setteling() # wait for scope to settle amination
        log_message(" Settling Complete")
        print("settelingcomplete")
        root.update()
        wait_for_files()
        log_message(" Recording Complete")
        root.update()

    def slewing():
        log_message(" Slewing to "" ra= "+str(current_ra)+" dec= "+str(current_dec))
        print(datetime.now().strftime("%H:%M:%S")+" Slewing to "" ra= "+str(current_ra)+" dec= "+str(current_dec))
        while telescope.Slewing:
            time.sleep(1)
        setteling()
        root.update()
        global logra
        logra= current_ra
        global logdec
        logdec= current_dec

    # Main loop to move the telescope in increments
    current_ra = ra_start
    while current_ra <= ra_end:
        current_dec = dec_start  # Reset Dec for each RA position
        telescope.SlewToCoordinates(current_ra, current_dec)  # Move to the current RA and start Dec
        slewing()  # Wait for telescope to settle
        
        while current_dec <= dec_end:
            # Move to the current Dec position
            telescope.SlewToCoordinates(current_ra, current_dec)
            slewing()  # Wait until the telescope stops slewing

            # Increment Dec for the next position
            current_dec += dec_step

        # After finishing Dec movements, increment RA for the next scan
        current_ra += ra_step

    # Disconnect
    telescope.Connected = False
    print("Telescope disconnected")
    print("scan completet")
    
def Get_From_Stellaruim():
    ra_entry.delete(0,tk.END)
    dec_entry.delete(0,tk.END)
    # URL of the local API
    url = 'http://localhost:8090/api/main/status?actionId=6&propId=51'

    # Fetch the JSON data from the API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()
        
        # Get selection info
        selection_info = data.get('selectioninfo', 'No selection info available')
        
        # Extract the object name
        object_name_match = re.search(r'(\w+)\s*\(.*?\)\s*-\s*.*?<br', selection_info)
        name = object_name_match.group(1).strip() if object_name_match else 'Unknown Object'
        
        # Extract RA and Dec values for "on date"
        ra_dec_on_date_match = re.search(r'RA/Dec \(on date\):\s*([0-9hms\s°.\-"]+)/\s*([0-9°\s.\-"]+)', selection_info)
        if ra_dec_on_date_match:
            ra = ra_dec_on_date_match.group(1).strip()
            dec = ra_dec_on_date_match.group(2).strip()
        else:
            ra = 'N/A' #Error Message
            dec = 'N/A' #Error Message

        #Print the results in the desired format
        #print(f"Object: {name}, RA: {ra}, Dec: {dec}")
        #print(ra)
        #print(dec)

    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

    ra_entry.insert(0,ra)
    dec_entry.insert(0,dec)
    # Add further processing logic here...

# Create a custom shell class
class Shell(tk.Text):
    def write(self, text):
        self.insert(tk.END, text)
        self.see(tk.END)  # Auto-scroll to the end

    def flush(self):
        pass  # Required for compatibility with sys.stdout and sys.stderr

# Redirect standard error to the shell
class RedirectStderr:
    def __init__(self, shell):
        self.shell = shell

    def write(self, text):
        self.shell.write("Error: " + text)
        self.shell.see(tk.END)

    def flush(self):
        pass


# Create the main window
root = tk.Tk()
root.title("Telescope Control GUI")

# Create and place labels and entry fields
tk.Label(root, text="RA :").grid(row=0, column=0, sticky="w")
ra_entry = tk.Entry(root)
ra_entry.grid(row=0, column=1)

tk.Label(root, text="Dec :").grid(row=1, column=0, sticky="w")
dec_entry = tk.Entry(root)
dec_entry.grid(row=1, column=1)


tk.Label(root, text="RA Scan Size(°):").grid(row=2, column=0, sticky="w")
ra_scan_size_entry = tk.Entry(root)
ra_scan_size_entry.grid(row=2, column=1)

tk.Label(root, text="Dec Scan Size(°):").grid(row=3, column=0, sticky="w")
dec_scan_size_entry = tk.Entry(root)
dec_scan_size_entry.grid(row=3, column=1)

tk.Label(root, text="RA Steps Size (°):").grid(row=4, column=0, sticky="w")
ra_steps_entry = tk.Entry(root)
ra_steps_entry.grid(row=4, column=1)

tk.Label(root, text="Dec Steps Size (°):").grid(row=5, column=0, sticky="w")
dec_steps_entry = tk.Entry(root)
dec_steps_entry.grid(row=5, column=1)

tk.Label(root, text="Scan time:").grid(row=6, column=0, sticky="w")
scan_time_entry = tk.Entry(root)
scan_time_entry.grid(row=6, column=1)

# Create buttons
button_frame = tk.Frame(root)
button_frame.grid(row=7, column=0, columnspan=2, pady=5)

start_button = tk.Button(button_frame, text="Start Scan", command=Start_Scan)
start_button.grid(row=0, column=0,padx=5 ,pady=5)


stellarium_button = tk.Button(button_frame, text="Get RA and Dec", command=Get_From_Stellaruim)
stellarium_button.grid(row=0, column=1,padx=5, pady=5, )

Save_as_button = tk.Button(button_frame, text="Save Data As", command=Save_As)
Save_as_button.grid(row=0, column=2,padx=5, pady=5, )

# Add a frame for the shell output
shell_frame = tk.Frame(root)
shell_frame.grid(row=8, column=0, columnspan= 3, padx=5, pady=5, sticky="nsew")

# Create the shell-like output area
shell = Shell(shell_frame, wrap="word", height=10, width=50, bg="black", fg="white", font=("Consolas", 10))
shell.pack(fill="both", expand=True)

# Redirect stdout and stderr to the shell
sys.stdout = shell
sys.stderr = RedirectStderr(shell)

# Make the window resizable and configure grid weights
root.grid_rowconfigure(8, weight=1)
root.grid_columnconfigure(1, weight=1)

# Run the GUI event loop
root.mainloop()

