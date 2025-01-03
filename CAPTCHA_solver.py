import streamlit as st
import pandas as pd
import time
import requests
from datetime import datetime

# Set up the Streamlit app
st.set_page_config(layout="wide")  # Use wide layout
st.title("CAPTCHA Solver")
st.write("Please solve the CAPTCHA displayed below and submit your answer.")

# OneDrive CAPTCHA image link
captcha_image_path = "https://hkdirektoratet-my.sharepoint.com/:i:/g/personal/samad_ismayilov_hkdir_no/EZc76tfE0odNhZW8FMRU0WAB8THtdPx90vRnQlK2rTaUwg?download=1"

# Add cache-buster to fetch the latest image
captcha_image_path_with_cache_buster = f"{captcha_image_path}&cache_buster={int(time.time())}"

# Display the CAPTCHA image in the Streamlit app
st.image(captcha_image_path_with_cache_buster, caption="Latest Screenshot", use_container_width=True)

# Shared "Can Edit" file link for solutions
solution_file_url = "https://hkdirektoratet-my.sharepoint.com/:t:/g/personal/samad_ismayilov_hkdir_no/EZIrJZViCExKmx-LsgGz9cMBhCNNsbYww9AC0D2BAs4Uiw?download=1"

# Function to fetch existing solutions from OneDrive
def fetch_existing_solutions():
    try:
        response = requests.get(solution_file_url)
        if response.status_code == 200:
            content = response.text
            solutions = [
                {"Solution": line.split(" - ")[0], "Date & Time": line.split(" - ")[1]}
                for line in content.splitlines() if " - " in line
            ]
            return pd.DataFrame(solutions)
        else:
            st.error("Unable to fetch existing solutions. Please check the file permissions.")
            return pd.DataFrame(columns=["Solution", "Date & Time"])
    except Exception as e:
        st.error(f"An error occurred while fetching solutions: {e}")
        return pd.DataFrame(columns=["Solution", "Date & Time"])

# Initialize or load the submitted answers DataFrame
if "submitted_answers" not in st.session_state:
    st.session_state["submitted_answers"] = fetch_existing_solutions()

# Initialize the input field value in session state
if "captcha_input" not in st.session_state:
    st.session_state["captcha_input"] = ""

# Function to append a new solution to the OneDrive file
def append_solution_to_onedrive(solution):
    try:
        # Fetch the existing content
        response = requests.get(solution_file_url)
        if response.status_code == 200:
            existing_content = response.text
        else:
            existing_content = ""

        # Prepare the new content
        new_content = existing_content + f"{solution} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        # Inform the user about limitations of appending to OneDrive directly
        st.error(
            "Currently, writing to OneDrive files directly is not supported via Streamlit. "
            "Consider using an API or backend for secure file updates."
        )
    except Exception as e:
        st.error(f"An error occurred while appending the solution: {e}")

# Function to handle submission
def submit_solution():
    if st.session_state["captcha_input"].strip():
        # Append the solution to the OneDrive file
        append_solution_to_onedrive(st.session_state["captcha_input"].strip())

        # Update the session state DataFrame
        new_row = pd.DataFrame({
            "Solution": [st.session_state["captcha_input"].strip()],
            "Date & Time": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        st.session_state["submitted_answers"] = pd.concat([st.session_state["submitted_answers"], new_row], ignore_index=True)

        # Clear the input field
        st.session_state["captcha_input"] = ""

# Layout: Split the page into three sections (image, table, input)
image_col, table_col, input_col = st.columns([1, 2, 1])

# Left column: Display the CAPTCHA image
with image_col:
    st.image(captcha_image_path_with_cache_buster, caption="CAPTCHA Image", use_container_width=True)

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
                font-size: 18px; /* Adjusted font size */
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
                padding: 10px 15px; /* Adjusted padding */
                border: 1px solid #dddddd;
            }
            .styled-table tbody tr {
                border-bottom: 1px solid #dddddd;
            }
            .styled-table tbody tr:nth-of-type(even) {
                background-color: #f3f3f3; /* Light gray for alternating rows */
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
    else:
        st.warning("No solutions submitted yet.")

# Right column: Input field and submit button
with input_col:
    st.write("Enter the CAPTCHA solution below:")
    st.text_input(
        "Enter CAPTCHA solution",
        key="captcha_input",
        help="Type the solution and press Enter or click Submit.",
        on_change=submit_solution  # Trigger submission on Enter
    )
    if st.button("Submit"):
        submit_solution()
