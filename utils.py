import time
import streamlit as st
import pandas as pd
import os
import json


def time_it(label, fn):
    """
    Wrap a function with a timer

    label: string label or method that creates a label from the result of calling fn
    fn: the function to wrap
    """

    def wrapper(*args):
        start_time = time.perf_counter()
        result = fn(*args)
        end_time = time.perf_counter()
        label_str = str(label(result)) if callable(label) else str(label)

        print("[Timer]: {} took {:.3f}s".format(label_str, end_time - start_time))
        return result

    return wrapper


def one_hot_encode_authors(df):
    author_cols = [col for col in df if col.startswith("Author_")]
    df = pd.get_dummies(df, columns=author_cols, sparse=True, prefix="Author")
    return df


def st_dataset_selector():
    # Enables streamlit to read data from mounted disk in GCP
    dataset_location = "./"
    if "STREAMLIT_DATA_LOCATION" in os.environ:
        dataset_location = os.environ["STREAMLIT_DATA_LOCATION"]

    datasets = {
        dataset_location + "sample_data.jsonl": "Small sample (50 rows)",
        dataset_location + "250k.docs.jsonl": "Large sample (250k rows)",
        dataset_location + "mag5.docs.jsonl": "Full dataset (5m rows, slooow)",
    }

    return st.selectbox(
        "Selected Dataset",
        list(datasets.keys()),
        format_func=lambda x: datasets[x],
    )


@st.cache(suppress_st_warning=True)
def load_dataset(dataset_filename, limit):
    loading_bar = st.progress(0)
    json_data = []
    i = 0
    print("Loading dataset")
    with open(dataset_filename) as file:
        for json_line in file:
            doc = json.loads(json_line)

            # Extract author id (we don't care about AuthorName and SequenceNumber for now)
            for k, author in enumerate(doc["Authors"]):
                doc["Author_" + str(k + 1)] = author["AuthorId"]
            del doc["Authors"]

            # Map fields of study
            for field_of_study in doc["FieldsOfStudy"]:
                doc["FieldOfStudy_" + str(field_of_study["Level"])] = field_of_study[
                    "Name"
                ]
            del doc["FieldsOfStudy"]

            # Extract JournalName from Journal (also contains JournalId, Website)
            if doc["Journal"]:
                doc["JournalName"] = doc["Journal"]["JournalName"]
            del doc["Journal"]

            # For now we don't care about these columns
            del doc["Urls"]
            del doc["PdfUrl"]
            del doc["Doi"]
            del doc["BookTitle"]
            del doc["Volume"]
            del doc["Issue"]
            del doc["FirstPage"]
            del doc["LastPage"]

            json_data.append(doc)
            i += 1

            if i % 50 == 0:
                loading_bar.progress(i / limit)

            if i >= limit:
                loading_bar.progress(100)
                loading_bar.empty()
                break

    print("Finished loading the data")
    dataframe_loader = st.spinner("Loading dataframe")
    df = pd.DataFrame(json_data)
    print("Created DataFrame")

    loading_bar.empty()
    return df