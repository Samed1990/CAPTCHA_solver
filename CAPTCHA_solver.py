import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Filepath for persistent text file
TEXT_FILE_PATH = "solutions.txt"

# CAPTCHA image path (provide your image URL here)
captcha_image_path = "https://hkdirektoratet-my.sharepoint.com/personal/samad_ismayilov_hkdir_no/_layouts/15/download.aspx?share=EZc76tfE0odNhZW8FMRU0WAB8THtdPx90vRnQlK2rTaUwg&download=1"


# Function to load solutions from the text file
def load_solutions():
    if os.path.exists(TEXT_FILE_PATH):
        with open(TEXT_FILE_PATH, "r") as file:
            lines = file.readlines()
            solutions = [
                {"Solution": line.split(" - ")[0], "Date & Time": line.split(" - ")[1].strip()}
                for line in lines if " - " in line
            ]
            df = pd.DataFrame(solutions)
            if not df.empty:
                # Ensure "Date & Time" is parsed as datetime
                df["Date & Time"] = pd.to_datetime(df["Date & Time"])
                
                # Delete rows older than 24 hours
                current_time = datetime.now()
                time_threshold = current_time - timedelta(hours=24)
                df = df[df["Date & Time"] > time_threshold]
                
                # Sort by "Date & Time" in descending order
                df = df.sort_values(by="Date & Time", ascending=False, ignore_index=True)
            
            with open(TEXT_FILE_PATH, "w") as file:
                for _, row in df.iterrows():
                    file.write(f'{row["Solution"]} - {row["Date & Time"]}\n')
                    
            return df
    else:
        # Create an empty file if it doesn't exist
        with open(TEXT_FILE_PATH, "w") as file:
            pass
        return pd.DataFrame(columns=["Solution", "Date & Time"])

# Function to save a new solution to the text file
def save_solution_to_file(solution, timestamp):
    with open(TEXT_FILE_PATH, "a") as file:
        file.write(f"{solution} - {timestamp}\n")

# Load existing solutions
solutions_df = load_solutions()

# Set up the Streamlit app
st.set_page_config(layout="wide")  # Use wide layout
st.title("CAPTCHA Solver")
st.write("Please solve the CAPTCHA displayed below and submit your answer.")

# Initialize the input field value in session state
if "captcha_input" not in st.session_state:
    st.session_state["captcha_input"] = ""

# Function to handle solution submission
def submit_solution():
    if st.session_state["captcha_input"].strip():
        # Add the solution to the DataFrame with the current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_solution = {"Solution": st.session_state["captcha_input"].strip(), "Date & Time": timestamp}
        
        # Append the new solution to the DataFrame
        global solutions_df
        solutions_df = pd.concat([pd.DataFrame([new_solution]), solutions_df], ignore_index=True)
        
        # Convert "Date & Time" column to datetime to ensure proper sorting
        solutions_df["Date & Time"] = pd.to_datetime(solutions_df["Date & Time"])
        
        # Sort the DataFrame by "Date & Time" in descending order
        solutions_df = solutions_df.sort_values(by="Date & Time", ascending=False, ignore_index=True)
        
        # Save the solution to the text file
        save_solution_to_file(new_solution["Solution"], new_solution["Date & Time"])
        
        # Clear the input field
        st.session_state["captcha_input"] = ""
        st.success("Solution submitted successfully!")

# Layout: Split the page into three sections (image, table, input)
image_col, table_col, input_col = st.columns([1, 2, 1])

# Left column: Display the CAPTCHA image
with image_col:
    st.image(captcha_image_path, caption="CAPTCHA Image", width=550)  # Adjusted width for 20% increase


# Middle column: Display the table of submitted solutions
with table_col:
    if not solutions_df.empty:
        # Add a styled header for "Submitted Solutions" and move it to the right
        st.markdown(
            """
            <div style="text-align: right; margin-right: 300px;">
                <h3>Submitted Solutions</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Apply CSS styling for the table
        st.markdown(
            """
            <style>
            .styled-table {
                border-collapse: collapse;
                margin: auto; /* Center the table horizontally */
                font-size: 18px; /* Larger font for solutions */
                font-family: Arial, sans-serif;
                width: 80%; /* Full width of middle column */
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
                padding: 12px 15px;
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

        # Add pagination
        # Initialize session state for pagination
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = 0

        # Define pagination logic
        items_per_page = 10
        total_pages = (len(solutions_df) - 1) // items_per_page + 1
        start_index = st.session_state["current_page"] * items_per_page
        end_index = start_index + items_per_page

        # Display paginated rows
        paginated_df = solutions_df.iloc[start_index:end_index]

        # Render the paginated table
        st.markdown(
            paginated_df.to_html(
                classes="styled-table",
                index=False,
                escape=False
            ),
            unsafe_allow_html=True
        )

        # Pagination controls
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.markdown(
                """
                <div style="margin-left: -100px;">
                """, 
                unsafe_allow_html=True
            )
            if st.session_state["current_page"] > 0:
                if st.button("Previous"):
                    st.session_state["current_page"] -= 1
            st.markdown(
                """
                </div>
                """, 
                unsafe_allow_html=True
            )
        with col3:
            if st.session_state["current_page"] < total_pages - 1:
                if st.button("Next"):
                    st.session_state["current_page"] += 1
    else:
        st.write("No solutions submitted yet.")




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

# Add copyright footer
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        text-align: center;
        padding: 10px 0;
        font-size: 14px;
        color: #555;
        font-family: Arial, sans-serif;
    }
    </style>
    <div class="footer">
        © Samad Ismayilov, 2025. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
