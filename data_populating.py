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

def get_forecast(payload):
    forecast_api = "http://34.93.125.48:8000/forecast?disease=Diabetes&target=HbA1c&n=30"
    payload = payload
    # Make a POST request
    result = request_api_endpoint(forecast_api, payload)
    return result

def get_data(payload):
    # Example API endpoint and data
    api_endpoint = "http://34.93.125.48:8000/data-generator?samples=100&disease=Diabetes"
    payload = payload
    # Make a POST request
    result = request_api_endpoint(api_endpoint, json.dumps(payload))
    return result

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
    selected_tab = st.sidebar.radio('Go to', ['Upload PDF', 'Synthetic Data Generator', 'Forecasting', 'Diabetes Panel'])

    if selected_tab == 'Upload PDF':
        st.subheader('Upload PDF')

        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])

        if uploaded_file is not None:
            # Process the uploaded PDF file
            # response = upload_pdf(uploaded_file)
            response=time.sleep(20)
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

        input_dict_extraction = st.session_state.extracted_data
        print(" st.session_state.extracted_data" ,  st.session_state.extracted_data)
        if st.button('Generate Synthetic Data'):
            output_json_extraction = get_data(input_dict_extraction)
            # Serialize the extracted data with double quotes
            output_json_extraction_str = json.dumps(output_json_extraction)
            st.session_state.populated_data = output_json_extraction_str
            st.subheader('Synthetic Data Generated:')
            st.json(output_json_extraction_str)

    elif selected_tab == 'Forecasting':
        st.subheader('Forecasting')

        input_dict_forecasting = st.session_state.populated_data

        if st.button('Perform Forecasting'):
            output_json_forecasting = get_forecast(input_dict_forecasting)
            st.subheader('Forecasted Data:')
            st.session_state.forecast_data = output_json_forecasting
            st.json(output_json_forecasting)
    
    elif selected_tab == 'Diabetes Panel':
        st.subheader('Diabetes Panel')
        
        input_dict_forecasting = st.session_state.forecast_data

        if input_dict_forecasting:
            data_list = [v for k, v in input_dict_forecasting.items()]

            # Create DataFrame from list of dictionaries
            df = pd.DataFrame(data_list)

            # Select only the 'Date' and 'Data' columns
            df = df[['Date', 'y']]
            
            print(df)
                
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
                    dtick=0.1  # Set the increment to 0.1
                )
            )

            st.plotly_chart(fig)

if __name__ == "__main__":
    main()
