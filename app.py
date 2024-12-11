import streamlit as st
import pandas as pd
import altair as alt
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(
    page_title="TPM Training Need Assessment Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load your data
data = pd.read_excel('Pre-Training_Need_Assessment_TPM.xlsx')
df = data.iloc[:, 3:121].copy()

# Define filter, exclude, and wordcloud columns
filter_columns = [
    'Q1. Select your employer Name (TPM)',
    'Q2. Select your Gender.'
]

exclude_from_bar = [
    'Q1. Which of the following checklists have you used so far in your monitoring visits?',
    'Q2. From the following, select three checklists where you require follow-up training',
    'Q6: What type of training or resources would help you perform your job better?'
]

wordcloud_questions = [
    'Q6: Could you provide a list of additional topics (maximum 3 topics) you would like WFP to cover for Resilience activity in the upcoming TPM training?',
    'Q4: Could you provide a list of additional topics (maximum 3 topics) you would like WFP to cover for Emergencies activity in the upcoming TPM training?',
    'Q5: Could you provide a list of additional topics (maximum 3 topics) you would like WFP to cover for Emergencies activity in the upcoming TPM training?',
    'Q5: Could you provide a list of additional topics (maximum 3 topics) you would like WFP to cover for Nutrition activity in the upcoming TPM training?',
    'Q6: Could you provide a list of additional topics (maximum 3 topics) you would like WFP to cover for MCBP activity in the upcoming TPM training?',
    'Q5: Could you provide a list of additional topics (maximum 3 topics) you would like WFP to cover for TPM activity in the upcoming TPM training?'
]

# ----------------------------------------
# Title and Description
# ----------------------------------------
st.title("TPM Training Need Assessment Analysis")
st.markdown("""
This dashboard provides insights into training needs and preferences gathered from a TPM pre-training assessment. 
Use the filters on the left to refine the data and explore visualizations including frequency-based bar charts and word clouds for open-ended responses.
""")

# ----------------------------------------
# Sidebar Filters
# ----------------------------------------
st.sidebar.title("Filters")
st.sidebar.markdown("Use the dropdown menus below to filter the dataset.")

selected_filters = {}
for col in filter_columns:
    unique_vals = df[col].unique().tolist()
    selection = st.sidebar.selectbox(f"{col}", options=["All"] + unique_vals, key=col)
    selected_filters[col] = selection

filtered_df = df.copy()
for col, val in selected_filters.items():
    if val != "All":
        filtered_df = filtered_df[filtered_df[col] == val]

# ----------------------------------------
# Filter Summary and Data Preview
# ----------------------------------------
st.markdown("---")
st.subheader("Current Filters Applied")
for k, v in selected_filters.items():
    st.write(f"**{k}:** {v}")

st.markdown("**Number of records after filtering:** {}".format(len(filtered_df)))

st.markdown("---")
st.subheader("Filtered Data Preview")
st.markdown("Below is a subset of the dataset after applying the selected filters:")
st.dataframe(filtered_df)

# ----------------------------------------
# Visualizations
# ----------------------------------------
st.markdown("---")
st.subheader("Visualizations")

metrics = [col for col in df.columns if col not in filter_columns]

for metric in metrics:
    # Skip columns we do not want to visualize
    if metric in exclude_from_bar:
        continue

    st.markdown(f"### {metric}")

    if metric in wordcloud_questions:
        # Word Cloud Visualization
        texts = filtered_df[metric].dropna().astype(str).tolist()
        words = []
        for t in texts:
            words.extend(t.split())
        combined_text = " ".join(words)

        if combined_text.strip():
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(combined_text)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.info("No topics available to generate a word cloud.")
    else:
        # Bar Chart Visualization
        value_counts = filtered_df[metric].value_counts().reset_index()
        category_col = "category_col"
        value_counts.columns = [category_col, 'count']

        if len(value_counts) == 0:
            st.info("No data available for this metric after filtering.")
        else:
            chart = (
                alt.Chart(value_counts)
                .mark_bar(color="#4E79A7")
                .encode(
                    x=alt.X(f"{category_col}:O", sort='-y', title="Responses"),
                    y=alt.Y('count:Q', title="Count")
                )
                .properties(width=600, height=400)
                .configure_axis(
                    labelFontSize=12,
                    titleFontSize=14
                )
                .configure_title(fontSize=16)
            )
            st.altair_chart(chart, use_container_width=True)
