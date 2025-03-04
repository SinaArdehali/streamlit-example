from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
from annotated_text import annotated_text
import spacy


st.set_page_config(page_title="Document Anonymizer", page_icon="🔒")

st.image(
    "https://emojipedia-us.s3.amazonaws.com/source/skype/289/locked_1f512.png",
    width=125,
)

st.title("Document Anonymizer")

st.write(
    """
1. Paste some text
2. Select the entity types to detect (Person, Organization or Location)
3. Visualize/anonymize the detected entities
	    """
)

st.header("")

"""
# Welcome to Streamlit!

Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:

If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).

In the meantime, below is an example of what you can do with just a few lines of code:
"""


# with st.echo(code_location='below'):
#     total_points = st.slider("Number of points in spiral", 1, 5000, 2000)
#     num_turns = st.slider("Number of turns in spiral", 1, 100, 9)

#     Point = namedtuple('Point', 'x y')
#     data = []

#     points_per_turn = total_points / num_turns

#     for curr_point_num in range(total_points):
#         curr_turn, i = divmod(curr_point_num, points_per_turn)
#         angle = (curr_turn + 1) * 2 * math.pi * i / points_per_turn
#         radius = curr_point_num / total_points
#         x = radius * math.cos(angle)
#         y = radius * math.sin(angle)
#         data.append(Point(x, y))

#     st.altair_chart(alt.Chart(pd.DataFrame(data), height=500, width=500)
#         .mark_circle(color='#0068c9', opacity=0.5)
#         .encode(x='x:Q', y='y:Q'))


@st.cache(show_spinner=False, allow_output_mutation=True, suppress_st_warning=True)
def load_models():
    french_model = spacy.load("./models/fr/")
    english_model = spacy.load("./models/en/")
    # english_model = spacy.load("./models/en/")
    # models = {"en": english_model}
    models = {"en": english_model, "fr": french_model}
    return models


def process_text(doc, selected_entities, anonymize=False):
    tokens = []
    for token in doc:
        if (token.ent_type_ == "PERSON") & ("PER" in selected_entities):
            tokens.append((token.text, "Person", "#faa"))
        elif (token.ent_type_ in ["GPE", "LOC"]) & ("LOC" in selected_entities):
            tokens.append((token.text, "Location", "#fda"))
        elif (token.ent_type_ == "ORG") & ("ORG" in selected_entities):
            tokens.append((token.text, "Organization", "#afa"))
        else:
            tokens.append(" " + token.text + " ")

    if anonymize:
        anonmized_tokens = []
        for token in tokens:
            if type(token) == tuple:
                anonmized_tokens.append(("X" * len(token[0]), token[1], token[2]))
            else:
                anonmized_tokens.append(token)
        return anonmized_tokens

    return tokens


models = load_models()

selected_language = st.sidebar.selectbox("Select a language", options=["en", "fr"])
selected_entities = st.sidebar.multiselect(
    "Select the entities you want to detect",
    options=["LOC", "PER", "ORG"],
    default=["LOC", "PER", "ORG"],
)
selected_model = models[selected_language]

text_input = st.text_area(
    "Type a text to anonymize",
    height=400,
    value="""
Miles Dewey Davis (May 26, 1926 – September 28, 1991) was an American trumpeter, bandleader, and composer.
Born in Alton, Illinois, and raised in East St. Louis, Davis left to study at Juilliard in New York City, before dropping out and making his professional debut as a member of saxophonist Charlie Parker's bebop quintet from 1944 to 1948. Shortly after, he recorded the Birth of the Cool sessions for Capitol Records, which were instrumental to the development of cool jazz. In the early 1950s.
""",
)

uploaded_file = st.file_uploader("or Upload a file", type=["doc", "docx", "pdf", "txt"])
if uploaded_file is not None:
    text_input = uploaded_file.getvalue()
    text_input = text_input.decode("utf-8")

anonymize = st.checkbox("Anonymize")
doc = selected_model(text_input)
tokens = process_text(doc, selected_entities)

annotated_text(*tokens)

if anonymize:
    st.markdown("**Anonymized text**")
    st.markdown("---")
    st.subheader(" Check anonymized text below 👇")
    anonymized_tokens = process_text(doc, selected_entities, anonymize=anonymize)
    downloadableText = annotated_text(*anonymized_tokens)
    # st.download_button(downloadableText, "Download anonymized text", filename="anonymized_text.txt")
    # st.download_button(label, data, file_name=None, mime=None, key=None, help=None, on_click=None, args=None, kwargs=None)