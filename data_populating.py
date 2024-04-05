import requests
import streamlit as st
import json
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
    forecast_api = "http://35.202.58.239:8000/forecast?disease=Diabetes&target=HbA1c&n=24"
    payload = payload
    # Make a POST request
    result = request_api_endpoint(forecast_api, payload)
    return result

def get_data(payload):
    # Example API endpoint and data
    api_endpoint = "http://35.202.58.239:8000/data-generator?samples=100&disease=Diabetes"
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
    selected_tab = st.sidebar.radio('Go to', ['Data Extractor', 'Data Synthesizer', 'Forecasting','Diabetes Panel'])

    if selected_tab == 'Data Extractor':
        st.subheader('Data Extractor')

        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])

        if uploaded_file is not None:
            # Process the uploaded PDF file
            # response = upload_pdf(uploaded_file)
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

    elif selected_tab == 'Data Synthesizer':
        st.subheader('Data Synthesizer')

        input_dict_extraction = st.session_state.extracted_data
        print(" st.session_state.extracted_data" ,  st.session_state.extracted_data)
        if st.button('Extract Data'):
            output_json_extraction = get_data(input_dict_extraction)
            # Serialize the extracted data with double quotes
            output_json_extraction_str = json.dumps(output_json_extraction)
            st.session_state.populated_data = output_json_extraction_str
            st.subheader('Extracted Data:')
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
            
            #   # Kidney Health Score Forecast
            # st.subheader("Kidney Health Score Forecast")
            # actual = df['Actual'].tolist()
            # forecasted = df['Forcasted'].tolist()
            # dates = df['Date'].tolist()

            # fig = go.Figure()
            # fig.add_trace(go.Scatter(x=dates, y=actual, mode='lines', name='Actual'))
            # fig.add_trace(go.Scatter(x=dates, y=forecasted, mode='lines', name='Forcasted'))

            # fig.update_layout(
            #     xaxis_title="Date",
            #     yaxis_title="Kidney Health Score (%)",
            #     xaxis_tickangle=-45,
            #     xaxis_tickfont_size=8,
            #     yaxis_range=[0, 100]
            # )
            
            data_list = [v for k, v in input_dict_forecasting.items()]

            # Create DataFrame from list of dictionaries
            df = pd.DataFrame(data_list)

            # Select only the 'Date' and 'Data' columns
            df = df[['Date', 'Data']]

            print(df)
            st.line_chart(data = df , x='Date' , y = 'Data')

if __name__ == "__main__":
    main()
