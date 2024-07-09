import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Function to load data from uploaded CSV file
def load_data(uploaded_file):
    data = pd.read_csv(uploaded_file, parse_dates=['Date'], dayfirst=True)
    return data

# Function to resample data based on selected interval
def resample_data(data, interval):
    if interval == "Hourly":
        return data.set_index('Date')  # No need to resample hourly data
    elif interval == "Daily":
        return data.set_index('Date').resample('D').mean()
    elif interval == "Monthly":
        return data.set_index('Date').resample('M').mean()

# Function to plot data based on selected chart type
def plot_data(ax, data, chart_type, interval, start_date=None, end_date=None):
    if chart_type == 'Line Plot':
        ax.plot(data.index, data['Price'], marker='o', linestyle='-', label=f'{interval} Prices')
    elif chart_type == 'Bar Plot':
        ax.bar(data.index, data['Price'], label=f'{interval} Prices', width=0.8)
    elif chart_type == 'Area Plot':
        ax.fill_between(data.index, data['Price'], alpha=0.5, label=f'{interval} Prices')
    elif chart_type == 'Scatter Plot':
        ax.scatter(data.index, data['Price'], marker='o', label=f'{interval} Prices')

    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title(f'{interval} {chart_type}')
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)

# Streamlit app title and description
st.set_page_config(page_title="Profiling", page_icon=":moneybag:")
st.title("Load Curve Analysis & Profiling")
st.markdown("---")

# File upload section
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    data = load_data(uploaded_file)

    # Sidebar for chart type selection
    st.sidebar.title('Chart Type')
    chart_type = st.sidebar.selectbox('Select Chart Type', ['Line Plot', 'Bar Plot', 'Area Plot', 'Scatter Plot'])

    # Sidebar for time intervals selection
    st.sidebar.title('Time Intervals')
    hourly = st.sidebar.checkbox("Hourly", value=False)
    daily = st.sidebar.checkbox("Daily", value=False)
    monthly = st.sidebar.checkbox("Monthly", value=False)

    selected_intervals = []
    if hourly:
        selected_intervals.append("Hourly")
    if daily:
        selected_intervals.append("Daily")
    if monthly:
        selected_intervals.append("Monthly")

    # Show button to display plots
    show_button = st.sidebar.button("Show Plots")

    if show_button and selected_intervals:
        st.sidebar.markdown("---")
        st.sidebar.write("Displaying plots for selected intervals...")
        fig, axes = plt.subplots(len(selected_intervals), 1, figsize=(10, 5 * len(selected_intervals)), sharex=True)
        if len(selected_intervals) == 1:
            axes = [axes]  # Ensure axes is a list even if there's only one plot
        
        for ax, interval in zip(axes, selected_intervals):
            resampled_data = resample_data(data, interval)
            plot_data(ax, resampled_data, chart_type, interval)

        plt.tight_layout()
        st.pyplot(fig)

    # Custom period plot section
    st.sidebar.markdown("---")
    st.sidebar.title('Custom Period Plot')

    period_interval = st.sidebar.selectbox(
        "Select time interval for custom period",
        ("Hourly", "Daily", "Monthly")
    )

    # Initialize start and end dates based on selected interval
    if period_interval == "Hourly":
        start_date = st.sidebar.text_input("Enter start date and time (DD/MM/YYYY HH:MM:SS)", value="01/07/2024 08:00:00")
        end_date = st.sidebar.text_input("Enter end date and time (DD/MM/YYYY HH:MM:SS)", value="02/07/2024 20:00:00")
        st.sidebar.write("Note: Times are set by default to 8 AM and 8 PM.")
    elif period_interval == "Daily":
        start_date = st.sidebar.text_input("Enter start date (DD/MM/YYYY)", value="01/07/2024")
        end_date = st.sidebar.text_input("Enter end date (DD/MM/YYYY)", value="02/07/2024")
    elif period_interval == "Monthly":
        start_date = st.sidebar.text_input("Enter start month (MM/YYYY)", value="01/2024")
        end_date = st.sidebar.text_input("Enter end month (MM/YYYY)", value="12/2024")
    
    if st.sidebar.button("Plot Custom Period"):
        if start_date and end_date:
            try:
                if period_interval == "Hourly":
                    start_date = pd.to_datetime(start_date, format='%d/%m/%Y %H:%M:%S')
                    end_date = pd.to_datetime(end_date, format='%d/%m/%Y %H:%M:%S')
                elif period_interval == "Daily":
                    start_date = pd.to_datetime(start_date, format='%d/%m/%Y')
                    end_date = pd.to_datetime(end_date, format='%d/%m/%Y')
                elif period_interval == "Monthly":
                    start_date = pd.to_datetime(start_date, format='%m/%Y')
                    end_date = pd.to_datetime(end_date, format='%m/%Y')
                
                mask = (data['Date'] >= start_date) & (data['Date'] <= end_date)
                custom_data = data.loc[mask]
                
                if not custom_data.empty:
                    resampled_custom_data = resample_data(custom_data, period_interval)
                    fig, ax = plt.subplots()
                    plot_data(ax, resampled_custom_data, chart_type, period_interval, start_date, end_date)
                    ax.set_title(f'{period_interval} {chart_type} from {start_date.date()} to {end_date.date()}')
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.sidebar.write("No data available for the selected period.")
            except ValueError as e:
                st.sidebar.write("Invalid date format. Please try again.")
        else:
            st.sidebar.write("Please enter both start and end dates.")

    # Show descriptive statistics section
    if st.sidebar.button("Show Descriptive Statistics"):
        st.sidebar.markdown("---")
        st.sidebar.write("Descriptive Statistics of Price Data:")
        st.sidebar.write(data['Price'].describe())

else:
    st.write("Please upload a CSV file.")

st.sidebar.markdown("---")
st.sidebar.title('About')
st.sidebar.info(
    "This app is designed to visualize and analyze energy time series data. "
    "Upload your CSV file to explore the data. You can select different chart types, "
    "time intervals, and customize the date range to analyze the data."
)

# Display app footer
st.sidebar.markdown("---")
st.sidebar.markdown("Powered by CRNS")
