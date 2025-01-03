from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Function to get the latest solution from the file
def get_latest_solution(file_path):
    try:
        # Open the file and read the last line
        with open(file_path, "r") as file:
            lines = file.readlines()
            if lines:
                # Get the last non-empty line and extract the solution part
                last_line = lines[-1].strip()  # Get the last line and strip extra spaces
                if " - " in last_line:
                    solution = last_line.split(" - ")[0]  # Split by " - " and get the solution part
                    return solution
                else:
                    print("Invalid format in last line.")
                    return None
            else:
                print("The file is empty.")
                return None
    except FileNotFoundError:
        print("Solution file not found.")
        return None

# Path to the solution file
solution_file_path = r"C:\Users\ismay\OneDrive\Desktop\Samad Utdanning IT\RPA_test\captcha_solution.txt"

# Step 1: Set up the WebDriver with Remote Debugging
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")  # Connect to remote debugging Chrome instance
driver = webdriver.Chrome(options=chrome_options)  # Use the debugging instance of Chrome

try:
    # Step 2: Open the EDBO page (if not already opened by PAD)
    edbo_url = "https://info.edbo.gov.ua/edu-documents/"
    driver.get(edbo_url)
    time.sleep(2)  # Wait for the page to load

    # Step 3: Get the latest solution from the file
    latest_solution = get_latest_solution(solution_file_path)

    if latest_solution:
        print(f"Latest solution fetched: {latest_solution}")

        # Step 4: Locate the CAPTCHA input field
        # Replace the following with the actual ID or other locator for the CAPTCHA input field
        captcha_input = driver.find_element(By.ID, "captcha")  # Replace with actual ID or selector

        # Step 5: Input the solution into the CAPTCHA field
        captcha_input.clear()  # Clear any pre-existing text
        captcha_input.send_keys(latest_solution)  # Type the solution
        print("Solution entered into CAPTCHA field.")

        # Step 6: Submit the CAPTCHA (if required)
        # Locate the Submit button
        #submit_button = driver.find_element(By.ID, "submit_button_id")  # Replace with actual ID or selector
        #submit_button.click()  # Click the Submit button
        #print("CAPTCHA solution submitted.")

        # Optional: Wait for success or failure
        time.sleep(5)  # Wait to observe the result
    else:
        print("No valid solution found in the file.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the browser only if necessary
    driver.quit()  # Use this if you want to close the browser after completing the process
import streamlit as st
import os
import pandas as pd
from datetime import datetime

# Set up the Streamlit app
st.set_page_config(layout="wide")  # Use wide layout
st.title("CAPTCHA Solver")
st.write("Please solve the CAPTCHA displayed below and submit your answer.")

# Filepath for the CAPTCHA image
captcha_image_path = r"C:\Users\ismay\OneDrive\Desktop\Samad Utdanning IT\RPA_test\Screenshot EDBO.png"

# Initialize or load the submitted answers DataFrame
if "submitted_answers" not in st.session_state:
    st.session_state["submitted_answers"] = pd.DataFrame(columns=["Solution"])

# Initialize the input field value in session state
if "captcha_input" not in st.session_state:
    st.session_state["captcha_input"] = ""

# Function to handle submission
def submit_solution():
    if st.session_state["captcha_input"].strip():
        # Add the solution to the DataFrame with the current date and time
        new_row = pd.DataFrame({
            "Solution": [st.session_state["captcha_input"].strip()],
            "Date & Time": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        st.session_state["submitted_answers"] = pd.concat([st.session_state["submitted_answers"], new_row], ignore_index=True)
        
        # Save the solution and timestamp to a file
        solution_file_path = r"C:\Users\ismay\OneDrive\Desktop\Samad Utdanning IT\RPA_test\captcha_solution.txt"
        with open(solution_file_path, "a") as file:  # Append mode to keep all solutions
            file.write(f'{st.session_state["captcha_input"].strip()} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        
        # Clear the input field
        st.session_state["captcha_input"] = ""


# Layout: Split the page into three sections (image, table, input)
image_col, table_col, input_col = st.columns([1, 2, 1])

# Left column: Display the CAPTCHA image
with image_col:
    if os.path.exists(captcha_image_path):
        # Check if the table has any solutions
        if not st.session_state["submitted_answers"].empty:
            st.image(captcha_image_path, caption="CAPTCHA Image (small view)", width=250)  # Slightly larger minimized image
        else:
            st.image(captcha_image_path, caption="CAPTCHA Image (extra-large view)", width=800)  # Larger initial image
    else:
        st.write("No CAPTCHA image found. Please check back later.")


# Middle column: Display the table of submitted solutions
with table_col:
    if not st.session_state["submitted_answers"].empty:
        st.write("### Submitted Solutions")
        # Apply CSS styling for the table
        st.markdown(
            """
            <style>
            .styled-table {
                border-collapse: collapse;
                margin: auto; /* Center the table horizontally */
                font-size: 22px; /* Larger font for solutions */
                font-family: Arial, sans-serif;
                width: 100%; /* Full width of middle column */
                max-width: 90%;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                border-radius: 8px; /* Rounded corners */
                overflow: hidden; /* Prevents corners from being cut off */
                text-align: center; /* Center-align text */
            }
            .styled-table thead tr {
                background-color: #add8e6; /* Light blue */
                color: white; /* White text for header */
            }
            .styled-table th, .styled-table td {
                padding: 15px 20px;
                border: 1px solid #dddddd;
            }
            .styled-table tbody tr {
                border-bottom: 1px solid #dddddd;
            }
            .styled-table tbody tr:nth-of-type(even) {
                background-color: #d3ecf8; /* Lighter blue for alternating rows */
            }
            .styled-table tbody tr:last-of-type {
                border-bottom: 2px solid #add8e6; /* Light blue footer */
            }
            </style>
            """, unsafe_allow_html=True
        )
        # Render the table using HTML for modern styling
        solutions_only = st.session_state["submitted_answers"]
        st.markdown(
            solutions_only.to_html(
                classes="styled-table",
                index=False,
                escape=False
            ),
            unsafe_allow_html=True
        )

# Right column: Input field and submit button
with input_col:
    st.write("Enter the CAPTCHA solution below:")
    # Input field for the CAPTCHA solution
    st.text_input(
        "Enter CAPTCHA solution",
        key="captcha_input",
        help="Type the solution and press Enter or click Submit.",
        on_change=submit_solution  # Trigger submission on Enter
    )
    # Submit button
    if st.button("Submit"):
        submit_solution()
