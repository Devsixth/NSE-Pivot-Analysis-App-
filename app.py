import streamlit as st
import os
import pandas as pd
from datetime import datetime, timedelta
from datatab import get_nse_trading_days, save_trading_days_to_csv, find_file_in_zip, process_date, count_rows_until_null, process_file, process_data
from Classicpivot import classicpivot
from camarillapivot import camarillapivot
from woodiepivot import woodiepivot
from fibonaccipivot import fibonaccipivot
from summary import summary

# Page Configuration
st.set_page_config(page_title="Pivot Analysis App", layout="wide")

# Custom CSS to Fix Footer at Bottom
st.markdown("""
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# Title of the App
st.markdown("""
    <h1 style='text-align: center;'>NSE EOD: Pivot Analysis App</h1>
""", unsafe_allow_html=True)

# Creating Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Data",
    "Summary",
    "Classic Pivot",
    "Camarilla Pivot",
    "Woodie Pivot",
    "Fibonacci Pivot"
])

# Summary Tab
with tab1:
    # Streamlit app
    st.title("EOD DATA")

    start_date = st.date_input("Select the starting date", value=(datetime.now() - timedelta(days=30)).date())
    end_date = st.date_input("Select the ending date", value=(datetime.now() - timedelta(days=1)).date(),
                             max_value=(datetime.now() - timedelta(days=1)).date())

    if st.button("Process Data"):
        # Check if start date and end date are the same
        if start_date == end_date:
            st.error("Start date and end date must be different.")
        # Check if end date is before start date
        elif end_date < start_date:
            st.error("The end date cannot be earlier than the start date.")
        else:
            with st.spinner('In Process....'):

                start_date_formatted = pd.to_datetime(start_date).strftime('%Y-%m-%d')
                end_date_formatted = pd.to_datetime(end_date).strftime('%Y-%m-%d')

                nse_trading_days = get_nse_trading_days(start_date_formatted, end_date_formatted)
                print(nse_trading_days)
                save_trading_days_to_csv(nse_trading_days)

                cue_read = pd.read_csv("CUE_DATE.csv")
                i = 0

                while i < len(cue_read):
                    Tdate = cue_read['details'].iat[i]
                    result = process_date(Tdate, start_date.year)

                    if result is None:
                        cue_read = cue_read.drop(index=i).reset_index(drop=True)
                        cue_read.to_csv("CUE_DATE.csv", index=False)
                        print(f"Removed unavailable date: {Tdate} from CUE_DATE.csv")
                    else:
                        print(f"Data processed successfully for date: {Tdate}")
                        i += 1

                directory = "nse_eod_data_files"
                if not os.path.exists(directory):
                    os.makedirs(directory)
                all_data = []
                for filename in os.listdir(directory):
                    if filename.startswith("Pd"):
                        file_path = os.path.join(directory, filename)
                        df = process_file(file_path)
                        all_data.append(df)

                final_df = pd.concat(all_data)
                final_df.to_csv(f"EOD_DATA_FOR_ANALYSIS.csv", index=False)

                # Analysis part
                path = r'EOD_DATA_FOR_ANALYSIS.csv'  # Path to the original CSV file
                dfs = pd.read_csv(path)

                # Call the data processing function
                process_data(dfs)
                
# Classic Pivot Tab
with tab2:
    summary()

# Classic Pivot Tab
with tab3:
    classicpivot()

# Camarilla Pivot Tab
with tab4:
    camarillapivot()

# Woodie Pivot Tab
with tab5:
    woodiepivot()

# Fibonacci Pivot Tab
with tab6:
    fibonaccipivot()

# Footer (Fixed to Bottom)
st.markdown("""
    <div class="footer">
        © 2024 Pivot Analysis Tool - Powered by PAS
    </div>
""", unsafe_allow_html=True)
