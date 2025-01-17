import streamlit as st
import os
import wget
import zipfile
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
from pandas_market_calendars import get_calendar


# Function to get NSE trading days
def get_nse_trading_days(start_date, end_date):
    nse_cal = get_calendar('NSE')
    schedule = nse_cal.valid_days(start_date=start_date, end_date=end_date)
    return [session.strftime('%d-%m-%Y') for session in schedule]


# Function to save trading days to CSV
def save_trading_days_to_csv(trading_days):
    # Define the file path
    file_path = 'CUE_DATE.csv'

    # Check if the file already exists and delete it if so
    if os.path.exists(file_path):
        os.remove(file_path)

    # Create a DataFrame and save it to CSV
    df = pd.DataFrame({'details': trading_days})
    df.to_csv(file_path, index=False)


def find_file_in_zip(zip_file, target_filename):
    for file_info in zip_file.infolist():
        if file_info.filename.endswith(target_filename):
            return file_info.filename
    return None


# Function to process and extract data from files
def process_date(Tdate, target_year):
    T_d = Tdate[:2]
    T_month = Tdate[3:5]
    year = Tdate[8:]
    T_m = Tdate[3:5]
    T_y = Tdate[6:]

    month_dict = {'01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR', '05': 'MAY', '06': 'JUN',
                  '07': 'JUL', '08': 'AUG', '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}

    Tdate_1_pd = str(T_d) + str(T_month) + str(year)
    Tdate_nsei = str(T_d) + str(T_month) + str(T_y)
    fo_bhav = str(T_d) + month_dict[T_m.upper()] + str(T_y)

    pd_format = f'https://archives.nseindia.com/archives/equities/bhavcopy/pr/PR{Tdate_1_pd}.zip'
    nsei_format = f'https://archives.nseindia.com/archives/nsccl/mwpl/nseoi_{Tdate_nsei}.zip'
    fo_format = f'https://archives.nseindia.com/content/historical/DERIVATIVES/{target_year}/{month_dict[T_m.upper()]}/fo{fo_bhav}bhav.csv.zip'

    print(f"Processing date: {Tdate}")
    print("Download URLs:")
    print(pd_format)
    print(nsei_format)
    print(fo_format)

    pd_success, nsei_success, fo_success = False, False, False

    try:
        wget.download(pd_format, "nse_eod_data_files/pd.zip")
        pd_success = True
    except Exception as e:
        st.write(f"Unable to download pd.zip for {Tdate}: {e}")

    try:
        wget.download(nsei_format, "nse_eod_data_files/nsei.zip")
        nsei_success = True
    except Exception as e:
        print(f"Unable to download nsei.zip for {Tdate}: {e}")

    try:
        wget.download(fo_format, "nse_eod_data_files/fo.zip")
        fo_success = True
    except Exception as e:
        print(f"Unable to download fo.zip for {Tdate}: {e}")

    if not (pd_success or nsei_success or fo_success):
        print(f"No data available for this day: {Tdate}")
        return None

    try:

        if pd_success:
            with zipfile.ZipFile('nse_eod_data_files/pd.zip') as zf:
                pd_file = next((f for f in zf.namelist() if f.startswith('Pd')), None)
                if pd_file:
                    zf.extract(pd_file, 'nse_eod_data_files/')
                else:
                    print(f"No file starting with 'pd' found in pd.zip.")
                    return None

        if nsei_success:
            with zipfile.ZipFile('nse_eod_data_files/nsei.zip') as zf:
                nsei_file = next((f for f in zf.namelist() if nsei_format.split('/')[-1][6:] in f), None)
                if nsei_file:
                    zf.extract(nsei_file, 'nse_eod_data_files/')
                else:
                    print(f"File matching pattern not found in nsei.zip.")
                    return None

        if fo_success:
            with zipfile.ZipFile('nse_eod_data_files/fo.zip') as zf:
                fo_file = next((f for f in zf.namelist() if fo_format.split('/')[-1][2:] in f), None)
                if fo_file:
                    zf.extract(fo_file, 'nse_eod_data_files/')
                else:
                    print(f"File matching pattern not found in fo.zip.")
                    return None
    except KeyError as e:
        st.write(f"KeyError while extracting files for date {Tdate}: {e}")
        return None

    if pd_success:
        os.remove("nse_eod_data_files/pd.zip")
    if nsei_success:
        os.remove("nse_eod_data_files/nsei.zip")
    if fo_success:
        os.remove("nse_eod_data_files/fo.zip")

    return True


# Function to process files in directory
def process_file(file_path, symbol=None):
    df1 = pd.read_csv(file_path)
    df2 = df1.replace(r'^\s+$', np.nan, regex=True)
    df_dropped = df2.drop(columns=['IND_SEC', 'CORP_IND'])
    df_dropped.dropna(subset=['SECURITY'], inplace=True)
    df_dropped.reset_index(drop=True, inplace=True)

    category = []
    count1 = count_rows_until_null(df_dropped, 'MKT')
    for i in range(0, count1):
        category.append('NIFTY INDEX')

    total_rows = df_dropped.shape[0]
    list_category = []
    for i in range(count1, total_rows):
        mkt = df_dropped.at[i, 'MKT']
        security = df_dropped.at[i, 'SECURITY']
        if pd.isnull(mkt) and pd.notnull(security):
            list_category.append(security)

    list_index = []
    for i in range(count1, total_rows):
        string = df_dropped.at[i, 'SECURITY']
        for j in range(len(list_category)):
            if string == list_category[j]:
                list_index.append(i)

    heading = []
    for value in range(len(list_index) - 1):
        i = list_index[value]
        j = list_index[value + 1]
        count = j - i - 1
        for k in range(count):
            heading.append(list_category[value])

    list3 = []
    for value in range(list_index[len(list_index) - 1], df_dropped.shape[0] - 1):
        list3.append(list_category[len(list_index) - 1])

    heading.extend(list3)
    category.extend(heading)

    df_final = df_dropped.dropna(subset=['MKT'])
    df_final.reset_index(drop=True, inplace=True)
    df_final.loc[:, 'SYMBOL'] = symbol
    df_final['CATEGORY'] = category

    text = os.path.basename(file_path)
    date_pattern = r'(\d{2})(\d{2})(\d{2})'
    match = re.search(date_pattern, text)
    if match:
        year = int(match.group(3))
        month = int(match.group(2))
        day = int(match.group(1))
        if year < 100:
            year += 2000
        date_object = datetime(year, month, day)

    date = [date_object] * df_final.shape[0]
    df_final['DATE'] = date

    df_final.drop(columns=['MKT', 'SERIES'], inplace=True)

    symbol = df_final['SYMBOL'].tolist()
    security = df_final['SECURITY']
    for i in range(len(symbol)):
        if pd.isna(symbol[i]):
            symbol[i] = security[i]
    df_final['SYMBOL'] = symbol
    os.remove(file_path)
    return df_final


# Helper function to count rows until null
def count_rows_until_null(dataframe, column_name):
    count = 0
    for i in dataframe[column_name]:
        if pd.notnull(i):
            count += 1
        else:
            break
    return count


# Function to process the data
def process_data(dfs):

    # Convert 'DATE' column to datetime format
    dfs['DATE'] = pd.to_datetime(dfs['DATE'])

    # Convert 'DATE' column to 'dd/mm/yyyy' format
    dfs['DATE'] = dfs['DATE'].dt.strftime('%d/%m/%Y')

    # Sort by SYMBOL and DATE, and reset index
    dfs1 = dfs.sort_values(['SYMBOL', 'DATE'], ascending=True).reset_index(drop=True)

    # Calculate percentage change
    dfs1['Per_change_clo'] = round(100 * (dfs1['CLOSE_PRICE'] - dfs1['PREV_CL_PR']) / dfs1['PREV_CL_PR'], 2)

    # Categorize percentage change direction
    dfs1['Per_chg_clo_Dir'] = dfs1['Per_change_clo'].apply(lambda x: 'UP' if x >= 0 else 'DN')

    # Calculate the range (HI - LO)
    dfs1['Range'] = dfs1['HIGH_PRICE'] - dfs1['LOW_PRICE']

    # Calculate Close - Open
    dfs1['Clo_Open'] = dfs1['CLOSE_PRICE'] - dfs1['OPEN_PRICE']

    # Rate category based on CLOSE_PRICE
    dfs1['Rate_Cate'] = np.where((dfs1['CLOSE_PRICE'] < 150), 'Below150',
                                 np.where((dfs1['CLOSE_PRICE'].between(150, 1000, inclusive="left")), '150-1000',
                                          np.where((dfs1['CLOSE_PRICE'].between(1000, 5000, inclusive="left")),
                                                   '1000-5000',
                                                   'Above>5000')))

    # Drop 'SECURITY' column
    dfs1 = dfs1.drop('SECURITY', axis=1)

    # Additional columns for price differences
    dfs1['HI_OP'] = dfs1['HIGH_PRICE'] - dfs1['OPEN_PRICE']
    dfs1['HI_CL'] = dfs1['HIGH_PRICE'] - dfs1['CLOSE_PRICE']
    dfs1['OP_CL'] = dfs1['OPEN_PRICE'] - dfs1['CLOSE_PRICE']

    dfs1['OP_LO'] = dfs1['OPEN_PRICE'] - dfs1['LOW_PRICE']
    dfs1['CL_LO'] = dfs1['CLOSE_PRICE'] - dfs1['LOW_PRICE']
    dfs1['HI_LO'] = dfs1['HIGH_PRICE'] - dfs1['LOW_PRICE']

    dfs1['OP_CL_prday'] = dfs1['OPEN_PRICE'] - dfs1['PREV_CL_PR']

    # Categorize volatility based on HI_LO
    dfs1['Volat'] = np.select(
        [
            dfs1['HI_LO'] <= 10,
            (dfs1['HI_LO'] > 10) & (dfs1['HI_LO'] <= 50),
            (dfs1['HI_LO'] > 50) & (dfs1['HI_LO'] <= 100),
            (dfs1['HI_LO'] > 100) & (dfs1['HI_LO'] <= 150),
            (dfs1['HI_LO'] > 150) & (dfs1['HI_LO'] <= 200),
            dfs1['HI_LO'] > 200
        ],
        [
            'Extreme Low',
            'Very Low',
            'Low',
            'High',
            'Very High',
            'Extreme High'
        ],
        default=None
    )

    # Select only the necessary columns to save in the updated CSV (keeping the original ones and the calculated ones)
    columns_to_save = [
        'SYMBOL', 'PREV_CL_PR', 'OPEN_PRICE', 'HIGH_PRICE', 'LOW_PRICE', 'CLOSE_PRICE', 'NET_TRDVAL', 'NET_TRDQTY',
        'TRADES', 'HI_52_WK', 'LO_52_WK', 'CATEGORY', 'DATE', 'Rate_Cate', 'Per_change_clo', 'Per_chg_clo_Dir', 'Range',
        'Volat', 'HI_OP', 'HI_CL', 'OP_CL', 'OP_LO', 'CL_LO', 'OP_CL_prday']

    # Save as a new file to preserve the original
    dfs1[columns_to_save].to_csv('EOD_DATA_FOR_ANALYSIS_UPDATED.csv', index=False)

    # Columns to display
    columns_to_display = ['DATE', 'SYMBOL', 'Volat', 'Range', 'Per_change_clo', 'Per_chg_clo_Dir']
    table_to_display = dfs1[columns_to_display]
    # st.write("### Summary")
    # st.dataframe(table_to_display, height=800, use_container_width=True)
    st.success("Processing completed! Data is ready for analysis. Please proceed across the tabs to explore.")


'''
# Streamlit app
st.title("NSE EOD Presentation Tool")

start_date = st.date_input("Select the starting date", value=(datetime.now() - timedelta(days=30)).date())
end_date = st.date_input("Select the ending date", value=(datetime.now() - timedelta(days=1)).date(),
                         max_value=(datetime.now() - timedelta(days=1)).date())

if st.button("Process Data"):
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
    process_data(dfs)'''
