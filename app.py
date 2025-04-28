
import streamlit as st
from database import *
from utils import *
import run_tests
import test_functions

st.set_page_config(page_title="Girl Math App", layout="centered")

def main():
    st.title("Girl Math App")

    # Directly run the original app.py content
    import app as original_app

if __name__ == "__main__":
    main()
