import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz
from utils.data_processor import DataProcessor

# Page config
st.set_page_config(
    page_title="Stock News Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
with open('styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize data processor
@st.cache_resource
def get_processor():
    return DataProcessor()

processor = get_processor()

def format_table(df):
    try:
        # Make headlines clickable with separate link
        def make_clickable(row):
            return f'{row["Headline"]} <a href="{row["URL"]}" target="_blank">[Link]</a>'

        df['Headline'] = df.apply(make_clickable, axis=1)

        # Drop URL column and format score
        display_df = df.drop('URL', axis=1).copy()

        # Format the score
        display_df['Score'] = pd.to_numeric(display_df['Score'], errors='coerce')

        # Add color styling for both sentiment and technical columns
        def get_technical_color(signal):
            colors = {
                "Bullish": "#28a745",
                "Bearish": "#dc3545",
                "Neutral": "#ffc107"
            }
            return colors.get(signal, "#ffc107")

        styled_df = display_df.style.format({
            'Score': '{:,.2f}'
        }).apply(lambda x: [
            f'background-color: {processor.sentiment_analyzer.get_sentiment_color(x["Sentiment"])}'
            if col == 'Sentiment'
            else f'background-color: {get_technical_color(x["Technical"])}'
            if col == 'Technical'
            else ''
            for col in x.index
        ], axis=1)

        return styled_df
    except Exception as e:
        st.error(f"Error in format_table: {str(e)}")
        return df

# Main app
st.title('📈 Stock News Dashboard')
st.markdown('_Auto-refreshes every 60 seconds_')

# Initialize session state for data caching
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'news_data' not in st.session_state:
    st.session_state.news_data = None

try:
    # Check if we need to update data
    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
    if (st.session_state.last_update is None or 
        (current_time - st.session_state.last_update.replace(tzinfo=pytz.timezone('Asia/Kolkata'))).seconds >= 60):

        # Get data from cache
        st.session_state.news_data = processor.get_cached_data()
        st.session_state.last_update = current_time

        # Display last updated time
        st.markdown(
            f'<p class="last-updated">Last updated: {current_time.strftime("%Y-%m-%d %I:%M %p IST")}</p>',
            unsafe_allow_html=True
        )

        # Display the news table
        if not st.session_state.news_data.empty:
            st.dataframe(
                format_table(st.session_state.news_data),
                use_container_width=True,
                height=800
            )
        else:
            st.warning("No news data available yet. Please wait for the next update.")

except Exception as e:
    st.error(f"An error occurred in main loop: {str(e)}")
    if st.button('Retry'):
        st.experimental_rerun()

# Client-side auto-refresh
st.markdown(
    """
    <script>
        function reloadPage() {
            setTimeout(function() {
                window.location.reload();
            }, 60000);
        }
        reloadPage();
    </script>
    """,
    unsafe_allow_html=True
)