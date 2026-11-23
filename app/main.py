import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(
    page_title="OELP Customer Intelligence",
    page_icon=":material/query_stats:",
    layout="wide",
)

pages = [
    st.Page(
        str(APP_DIR / "pages" / "1_Business_Overview.py"),
        title="Business Overview",
        icon=":material/dashboard:",
        default=True,
    ),
    st.Page(
        str(APP_DIR / "pages" / "2_Customer_Segmentation.py"),
        title="Customer Segmentation",
        icon=":material/groups:",
    ),
    st.Page(
        str(APP_DIR / "pages" / "3_Customer_Intelligence.py"),
        title="Customer Intelligence",
        icon=":material/person_search:",
    ),
    st.Page(
        str(APP_DIR / "pages" / "4_Purchase_Forecasting.py"),
        title="Purchase Forecasting",
        icon=":material/timeline:",
    ),
    st.Page(
        str(APP_DIR / "pages" / "5_Data_Upload.py"),
        title="Data Upload & Validation",
        icon=":material/upload_file:",
    ),
    st.Page(
        str(APP_DIR / "pages" / "6_Model_Performance.py"),
        title="Model Performance",
        icon=":material/monitoring:",
    ),
]

st.sidebar.caption("OELP · Customer Intelligence · Year 1")
st.navigation(pages, position="sidebar", expanded=True).run()
