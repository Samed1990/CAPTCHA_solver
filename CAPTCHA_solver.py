import streamlit as st
import os
import pandas as pd
import time
from datetime import datetime


# Set up the Streamlit app
st.set_page_config(layout="wide")  # Use wide layout
st.title("CAPTCHA Solver")
st.write("Please solve the CAPTCHA displayed below and submit your answer.")

# Filepath for the CAPTCHA image
#captcha_image_path = "Screenshot EDBO.png"

# Update the variable to use the new OneDrive direct download link
captcha_image_path = "https://hkdirektoratet-my.sharepoint.com/:i:/g/personal/samad_ismayilov_hkdir_no/EZc76tfE0odNhZW8FMRU0WAB8THtdPx90vRnQlK2rTaUwg?download=1"

# Add cache-buster to always fetch the latest image
captcha_image_path_with_cache_buster = f"{captcha_image_path}&cache_buster={int(time.time())}"

# Display the updated CAPTCHA image in the Streamlit app
st.image(captcha_image_path_with_cache_buster, caption="Latest Screenshot", use_column_width=True)

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
        solution_file_path = r"C:\Users\SamadIsmayilov\OneDrive - HKdirektoratet\Skrivebord\RPA prosjekt\test_img_folder\captcha_solution.txt"
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
