import pandas as pd
import streamlit as st
import plotly.express as px
from utils import time_it, one_hot_encode_authors, st_dataset_selector, load_dataset

st.header("Data Exploration")
# Wrap methods with timer:
load_dataset = time_it(
    lambda df: "Loading dataset ({} docs)".format((len(df))),
    load_dataset,
)
one_hot_encode_authors = time_it("One-hot encoding authors", one_hot_encode_authors)

docs_limit = st.number_input(
    "Max limit of docs to parse (more than 10000 items will be slow)",
    value=1000,
    step=50,
)
selected_dataset = st_dataset_selector()

raw_docs = load_dataset(selected_dataset, docs_limit)

st.subheader("Raw docs shape")
raw_docs.shape

st.subheader("First 10 papers")
st.write(raw_docs.head(10))

from correlation_study import run_correlation_study

run_correlation_study(raw_docs)

st.markdown(
    """
    ## Distribution of papers
    """
)

st.markdown(
    """
    ### Rank
    """
)
f = px.histogram(raw_docs, x="Rank", title="Rank distribution", nbins=50)
f.update_yaxes(title="Count")
st.plotly_chart(f)

st.markdown(
    """
    ### Field of study
    """
)


st.markdown(
    """
    ## One-hot encoding authors
    **Warning:** This is slow on large datasets
    """
)
if st.button("Run one-hot encoding"):
    one_hot_encoded = one_hot_encode_authors(raw_docs)
    st.subheader("One-hot-encoded authors shape")
    one_hot_encoded.shape
