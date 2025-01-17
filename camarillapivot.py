import streamlit as st
import pandas as pd


def camarillapivot():
    # Read the CSV file
    file_path = "EOD_DATA_FOR_ANALYSIS_UPDATED.csv"  # Replace with the path to your CSV file
    df = pd.read_csv(file_path)

    # Convert the DATE column to datetime format
    df['DATE'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y')

    # Perform calculations and round to the nearest integer
    df['PP'] = ((df['HIGH_PRICE'] + df['LOW_PRICE'] + df['CLOSE_PRICE']) / 3).round().astype(int)

    df['CAMR_PR1'] = (df['CLOSE_PRICE'] + 1.0833 * (df['HIGH_PRICE'] - df['LOW_PRICE'])).round().astype(int)
    df['CAMR_PR2'] = (df['CLOSE_PRICE'] + 1.1666 * (df['HIGH_PRICE'] - df['LOW_PRICE'])).round().astype(int)
    df['CAMR_PR3'] = (df['CLOSE_PRICE'] + 1.25 * (df['HIGH_PRICE'] - df['LOW_PRICE'])).round().astype(int)
    df['CAMR_PR4'] = (df['CLOSE_PRICE'] + 1.5 * (df['HIGH_PRICE'] - df['LOW_PRICE'])).round().astype(int)

    df['CAMR_PS1'] = (df['CLOSE_PRICE'] - 1.0833 * (df['HIGH_PRICE'] - df['LOW_PRICE'])).round().astype(int)
    df['CAMR_PS2'] = (df['CLOSE_PRICE'] - 1.1666 * (df['HIGH_PRICE'] - df['LOW_PRICE'])).round().astype(int)
    df['CAMR_PS3'] = (df['CLOSE_PRICE'] - 1.25 * (df['HIGH_PRICE'] - df['LOW_PRICE'])).round().astype(int)
    df['CAMR_PS4'] = (df['CLOSE_PRICE'] - 1.5 * (df['HIGH_PRICE'] - df['LOW_PRICE'])).round().astype(int)

    # Filter columns for display
    filtered_df = df[['SYMBOL', 'CAMR_PR1', 'CAMR_PR2', 'CAMR_PR3', 'CAMR_PR4', 'PP', 'CAMR_PS1',
                      'CAMR_PS2', 'CAMR_PS3', 'CAMR_PS4', 'DATE', 'Rate_Cate',
                      'CATEGORY', 'Volat', 'Per_chg_clo_Dir']]

    # Streamlit app layout
    st.markdown("<h1 style='text-align: center;'>Camarilla Pivot</h1>", unsafe_allow_html=True)

    # Date Slider with unique key
    min_date = df['DATE'].min().date()
    max_date = df['DATE'].max().date()

    # Use columns for the top row layout
    col1, col2, col3 = st.columns([4, 4, 4])

    with col1:
        # Place the slider in the first column with a unique key
        selected_date = st.slider(
            "Select Date Range",
            min_date,
            max_date,
            value=(min_date, max_date),
            key="camarilla_top_date_slider"  # Unique key for the top slider
        )

    with col2:
        selected_categories = st.multiselect(
            "Choose your Category",
            options=filtered_df['CATEGORY'].unique(),
            key="camarilla_category_select"  # Unique key for categories
        )

    with col3:
        # Filter symbols based on selected categories
        if selected_categories:
            filtered_symbols = df[df['CATEGORY'].isin(selected_categories)]['SYMBOL'].unique()
        else:
            filtered_symbols = df['SYMBOL'].unique()

        selected_symbols = st.multiselect(
            "Choose your Symbol",
            options=filtered_symbols,  # Dynamically filtered symbols
            key="camarilla_symbol_select"  # Unique key for symbols
        )

    # Create two columns for the remaining filters and the table
    left_column, right_column = st.columns([1, 5])  # Right column takes more space (5), left column is narrower (1)

    with left_column:

        if selected_categories and selected_symbols:
            # Filter volatilities based on both selected categories and symbols
            filtered_volatilies = df[
                (df['CATEGORY'].isin(selected_categories)) &
                (df['SYMBOL'].isin(selected_symbols))]['Volat'].unique()
            filtered_ratecate = df[
                (df['CATEGORY'].isin(selected_categories)) &
                (df['SYMBOL'].isin(selected_symbols))]['Rate_Cate'].unique()
            filtered_direction = df[
                (df['CATEGORY'].isin(selected_categories)) &
                (df['SYMBOL'].isin(selected_symbols))]['Per_chg_clo_Dir'].unique()

        else:
            # If either categories or symbols are not selected, include all volatilities
            filtered_volatilies = df['Volat'].unique()
            filtered_ratecate = filtered_df['Rate_Cate'].unique()
            filtered_direction = filtered_df['Per_chg_clo_Dir'].unique()

        # Vertical layout for remaining filters
        selected_volatilities = st.multiselect(
            "Choose your Volatility",
            options=filtered_volatilies,
            key="camarilla_volatility_select"  # Unique key for volatility
        )

        selected_rate_cate = st.multiselect(
            "Choose your Stock Price Range",
            options=filtered_ratecate,
            key="camarilla_rate_cate_select"  # Unique key for rate categories
        )

        selected_directions = st.multiselect(
            "Choose your Change Direction",
            options=filtered_direction,
            key="camarilla_directions_select"  # Unique key for directions
        )

    with right_column:
        # Apply filters based on selections
        filtered_df = df[
            (df['DATE'] >= pd.Timestamp(selected_date[0])) &
            (df['DATE'] <= pd.Timestamp(selected_date[1]))
        ]

        if selected_categories:
            filtered_df = filtered_df[filtered_df['CATEGORY'].isin(selected_categories)]
        if selected_symbols:
            filtered_df = filtered_df[filtered_df['SYMBOL'].isin(selected_symbols)]
        if selected_volatilities:
            filtered_df = filtered_df[filtered_df['Volat'].isin(selected_volatilities)]
        if selected_rate_cate:
            filtered_df = filtered_df[filtered_df['Rate_Cate'].isin(selected_rate_cate)]
        if selected_directions:
            filtered_df = filtered_df[filtered_df['Per_chg_clo_Dir'].isin(selected_directions)]
        # Renaming columns for better readability
        filtered_df = filtered_df.rename(columns={
            'SYMBOL': 'Symbol',
            'CAMR_PS4': 'S4',
            'CAMR_PS3': 'S3',
            'CAMR_PS2': 'S2',
            'CAMR_PS1': 'S1',
            'PP': 'PP',
            'CAMR_PR1': 'R1',
            'CAMR_PR2': 'R2',
            'CAMR_PR3': 'R3',
            'CAMR_PR4': 'R4'
        })

        # Display the DataFrame with updated column names
        st.dataframe(filtered_df[['Symbol', 'S4', 'S3', 'S2', 'S1',
                                  'PP', 'R1', 'R2', 'R3', 'R4']],
                     height=800, use_container_width=True)
