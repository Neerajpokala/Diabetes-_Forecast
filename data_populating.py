import requests
import streamlit as st
import json
import time
import pandas as pd
import plotly.graph_objects as go

def request_api_endpoint(url, data):
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raises exception for 4XX and 5XX status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

def get_forecast(disease, target, n):
    forecast_api = f"http://34.93.125.48:8000/forecast?disease={disease}&target={target}&n={n}"
    payload = st.session_state.populated_data 
    # Make a POST request
    result = request_api_endpoint(forecast_api, payload)
    return result

def get_data(samples, disease):
    # Example API endpoint and data
    api_endpoint = f"http://34.93.125.48:8000/data-generator?samples={samples}&disease={disease}"
    payload = st.session_state.extracted_data
    try:
        # Make a POST request
        result = request_api_endpoint(api_endpoint, json.dumps(payload))
        return result
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        st.error("An error occurred while fetching the synthetic data. Please try again later or contact the API provider for assistance.")
        return None

def upload_pdf(file):
    files = {'files': file}
    url = "http://35.202.58.239:8000/upload_and_extract"
    try:
        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

def main():
    st.title('Data Extraction and Forecasting App')

    # Initialize session state
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = {}
    if 'populated_data' not in st.session_state:
        st.session_state.populated_data = {}
    if 'forecast_data' not in st.session_state:
        st.session_state.forecast_data = {}

    # Add a left panel
    st.sidebar.title('Navigation')
    selected_tab = st.sidebar.radio('Go to', ['Data Extractor', 'Synthetic Data Generator', 'Forecasting', 'Diabetes Panel'])

    if selected_tab == 'Data Extractor':
        st.subheader('Data Extractor')

        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])

        if uploaded_file is not None:
            with st.spinner("Data extracting from PDF..."):
                # Process the uploaded PDF file
                time.sleep(20)  # Simulating data extraction process
                response = {
                    "Date": "2023-10-03",
                    "Age": 49,
                    "Urea": 19,
                    "Cr": 0.68,
                    "HbA1c": 6.7,
                    "BGL": 100,
                    "Chol": 169,
                    "TG": 121.61,
                    "HDL": 50.9,
                    "LDL": 93.77,
                    "VLDL": 24.32,
                    "IR": 4.35,
                    "Health_Status": "Diabetes"
                }
                st.session_state.extracted_data = response
                st.write("PDF uploaded successfully!")
                st.json(response)

    elif selected_tab == 'Synthetic Data Generator':
        st.subheader('Synthetic Data Generator')

        samples = st.number_input('Number of Samples', min_value=1, max_value=1000, value=100, step=1)
        disease = st.selectbox('Select Disease', ['Diabetes'])

        if st.button('Generate Synthetic Data'):
            with st.spinner("Generating Synthetic Data..."):
                output_json_extraction = get_data(samples, disease)
                if output_json_extraction:
                    # Serialize the extracted data with double quotes
                    output_json_extraction_str = json.dumps(output_json_extraction)
                    st.session_state.populated_data = output_json_extraction_str
                    st.subheader('Synthetic Data Generated:')
                    st.json(output_json_extraction_str)

    elif selected_tab == 'Forecasting':
        st.subheader('Forecasting')

        # Get user inputs for disease, target, and number of days
        disease = st.selectbox('Select Disease', ['Diabetes'])
        target = st.selectbox('Select Target', ['HbA1c'])
        n = st.number_input('Number of Months to Forecast', min_value=1, max_value=100, value=60, step=1)

        if st.button('Perform Forecasting'):
            with st.spinner("Performing Forecasting..."):
                output_json_forecasting = get_forecast(disease, target, n)
                st.subheader('Forecasted Data:')
                st.session_state.forecast_data = output_json_forecasting
                st.json(output_json_forecasting)
    
    elif selected_tab == 'Diabetes Panel':
        # st.subheader('Diabetes Panel')
        
        input_dict_forecasting = st.session_state.forecast_data

        if input_dict_forecasting:
            data_list = [v for k, v in input_dict_forecasting.items()]

            # Create DataFrame from list of dictionaries
            df = pd.DataFrame(data_list)

            # Select only the 'Date' and 'Data' columns
            df = df[['Date', 'y']]
                
            # Kidney Health Score Forecast
            # Assuming 'df' is the DataFrame created earlier
            # Select the last 12 points for forecasting
            forecast_df = df.tail(12)

            st.subheader("Diabetes - HbA1c Forecast")
            actual = df['y'].tolist()
            forecasted = forecast_df['y'].tolist()  # Using the 'Data' column for forecasted values
            dates = df['Date'].tolist()

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=actual, mode='lines', name='Actual'))
            fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecasted, mode='lines', name='Forecasted'))  # Using forecast_df for x-axis

            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Diabetes - HbA1c(%)",
                xaxis_tickangle=-45,
                xaxis_tickfont_size=8,
                yaxis=dict(
                    dtick=0.5,  # Set the increment to 0.5
                    tickvals=[4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8,8.5,9,9.5,10,10.5,11]  # Specify the tick values to display
                )
            )

            st.plotly_chart(fig)

if __name__ == "__main__":
    main()
