import streamlit as st
import pandas as pd
import plotly.express as px
from ollama import chat


# ==========================================================
# PAGE SETTINGS
# ==========================================================

st.set_page_config(
    page_title="Social Media Sentiment Dashboard",
    page_icon="📊",
    layout="wide"
)


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

.main-title {
    font-size: 40px;
    font-weight: bold;
}

.subtitle {
    font-size: 18px;
    color: gray;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# TITLE
# ==========================================================

st.markdown(
    '<div class="main-title">📊 Social Media Sentiment Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Analyze social media comments using AI and understand customer opinions.'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================================
# SESSION STATE
# ==========================================================

if "data" not in st.session_state:

    data = pd.read_csv("comments.csv")

    # Create Sentiment column
    data["Sentiment"] = "Not Analyzed"

    st.session_state.data = data


if "analysis_done" not in st.session_state:

    st.session_state.analysis_done = False


data = st.session_state.data


# ==========================================================
# ANALYZE ALL COMMENTS
# ==========================================================

st.subheader("🤖 AI Sentiment Analysis")

if st.button("🔍 Analyze All Comments", use_container_width=True):

    sentiments = []

    with st.spinner("🤖 AI is analyzing all comments..."):

        for comment in data["comment"]:

            prompt = f"""
            Analyze the sentiment of this social media comment.

            Classify it into ONLY ONE category:

            Positive
            Negative
            Neutral

            Comment:
            {comment}

            Return ONLY the category name.
            """

            response = chat(
                model="gemma3:1b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            sentiment = response["message"]["content"].strip()

            if "positive" in sentiment.lower():

                sentiments.append("Positive")

            elif "negative" in sentiment.lower():

                sentiments.append("Negative")

            else:

                sentiments.append("Neutral")


    data["Sentiment"] = sentiments

    st.session_state.data = data

    st.session_state.analysis_done = True

    st.success("✅ All comments analyzed successfully!")


# ==========================================================
# USER INPUT
# ==========================================================

st.divider()

st.subheader("💬 Analyze Your Own Comment")

st.write(
    "Enter any social media comment and let AI analyze its sentiment."
)

user_comment = st.text_area(
    "Your comment:",
    placeholder="Example: I really love this product!",
    height=100
)


if st.button("🤖 Analyze My Comment", use_container_width=True):

    if user_comment.strip() == "":

        st.warning("⚠️ Please enter a comment first.")

    else:

        with st.spinner("🤖 AI is analyzing your comment..."):

            prompt = f"""
            Analyze the sentiment of this social media comment.

            Classify it into ONLY ONE category:

            Positive
            Negative
            Neutral

            Comment:
            {user_comment}

            Return ONLY the category name.
            """

            response = chat(
                model="gemma3:1b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            sentiment = response["message"]["content"].strip()


        if "positive" in sentiment.lower():

            final_sentiment = "Positive"

        elif "negative" in sentiment.lower():

            final_sentiment = "Negative"

        else:

            final_sentiment = "Neutral"


        # Create new row

        new_row = pd.DataFrame({
            "comment": [user_comment],
            "Sentiment": [final_sentiment]
        })


        # Add to existing data

        st.session_state.data = pd.concat(
            [
                st.session_state.data,
                new_row
            ],
            ignore_index=True
        )


        st.session_state.analysis_done = True


        # Show result

        if final_sentiment == "Positive":

            st.success("😊 Your comment is **Positive**")

        elif final_sentiment == "Negative":

            st.error("😡 Your comment is **Negative**")

        else:

            st.info("😐 Your comment is **Neutral**")


        st.write("**Your comment:**")

        st.write(user_comment)


# ==========================================================
# GET UPDATED DATA
# ==========================================================

data = st.session_state.data


# ==========================================================
# DASHBOARD
# ==========================================================

if st.session_state.analysis_done:

    st.divider()

    st.subheader("📊 Dashboard Overview")


    # ------------------------------------------------------
    # SENTIMENT COUNTS
    # ------------------------------------------------------

    positive = (
        data["Sentiment"] == "Positive"
    ).sum()

    negative = (
        data["Sentiment"] == "Negative"
    ).sum()

    neutral = (
        data["Sentiment"] == "Neutral"
    ).sum()

    total = len(data)


    # ------------------------------------------------------
    # OVERALL SENTIMENT
    # ------------------------------------------------------

    if positive > negative and positive > neutral:

        overall = "😊 Positive"

    elif negative > positive and negative > neutral:

        overall = "😡 Negative"

    else:

        overall = "😐 Neutral"


    # ------------------------------------------------------
    # METRICS
    # ------------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "💬 Total Comments",
            total
        )

    with col2:

        st.metric(
            "😊 Positive",
            positive
        )

    with col3:

        st.metric(
            "😐 Neutral",
            neutral
        )

    with col4:

        st.metric(
            "😡 Negative",
            negative
        )

    with col5:

        st.metric(
            "🎯 Overall",
            overall
        )


    # ======================================================
    # PERCENTAGES
    # ======================================================

    if total > 0:

        positive_percent = (
            positive / total
        ) * 100

        neutral_percent = (
            neutral / total
        ) * 100

        negative_percent = (
            negative / total
        ) * 100


        st.subheader("📈 Sentiment Percentages")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "😊 Positive",
                f"{positive_percent:.1f}%"
            )

        with col2:

            st.metric(
                "😐 Neutral",
                f"{neutral_percent:.1f}%"
            )

        with col3:

            st.metric(
                "😡 Negative",
                f"{negative_percent:.1f}%"
            )


    # ======================================================
    # CHART DATA
    # ======================================================

    chart_data = pd.DataFrame({

        "Sentiment": [
            "Positive",
            "Neutral",
            "Negative"
        ],

        "Count": [
            positive,
            neutral,
            negative
        ]

    })


    # ======================================================
    # CHARTS
    # ======================================================

    st.subheader("📊 Sentiment Visualization")

    col1, col2 = st.columns(2)


    # ------------------------------------------------------
    # BAR CHART
    # ------------------------------------------------------

    with col1:

        fig_bar = px.bar(
            chart_data,
            x="Sentiment",
            y="Count",
            text="Count",
            title="Sentiment Distribution"
        )

        fig_bar.update_layout(
            xaxis_title="Sentiment",
            yaxis_title="Number of Comments"
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )


    # ------------------------------------------------------
    # DONUT CHART
    # ------------------------------------------------------

    with col2:

        fig_pie = px.pie(
            chart_data,
            names="Sentiment",
            values="Count",
            hole=0.45,
            title="Sentiment Percentage"
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )


    # ======================================================
    # SEARCH AND FILTER
    # ======================================================

    st.divider()

    st.subheader("🔎 Search & Filter Comments")

    col1, col2 = st.columns([2, 1])


    with col1:

        search_text = st.text_input(
            "🔎 Search comments",
            placeholder="Type a word or phrase..."
        )


    with col2:

        sentiment_filter = st.selectbox(
            "Filter by sentiment",
            [
                "All",
                "Positive",
                "Neutral",
                "Negative"
            ]
        )


    filtered_data = data.copy()


    # Search

    if search_text.strip() != "":

        filtered_data = filtered_data[
            filtered_data["comment"]
            .str.contains(
                search_text,
                case=False,
                na=False
            )
        ]


    # Sentiment filter

    if sentiment_filter != "All":

        filtered_data = filtered_data[
            filtered_data["Sentiment"]
            == sentiment_filter
        ]


    st.write(
        f"Showing **{len(filtered_data)}** comments"
    )


    # ======================================================
    # DETAILED RESULTS
    # ======================================================

    st.subheader("📝 Detailed Results")

    st.dataframe(
        filtered_data,
        use_container_width=True,
        hide_index=True
    )


    # ======================================================
    # SENTIMENT INSIGHTS
    # ======================================================

    st.divider()

    st.subheader("💡 Sentiment Insights")


    if positive > negative:

        st.success(
            f"😊 Positive sentiment is currently dominant "
            f"with {positive} comments."
        )

    elif negative > positive:

        st.error(
            f"😡 Negative sentiment is currently dominant "
            f"with {negative} comments."
        )

    else:

        st.info(
            "😐 Positive and negative sentiments are balanced."
        )


    # Negative percentage warning

    if negative_percent >= 50:

        st.warning(
            "⚠️ More than half of the comments are negative. "
            "This may indicate customer dissatisfaction."
        )

    elif negative_percent >= 30:

        st.warning(
            "⚠️ A significant number of comments are negative. "
            "It may be useful to review the negative feedback."
        )

    else:

        st.success(
            "✅ The overall negative sentiment level is relatively low."
        )


    # ======================================================
    # POSITIVE COMMENTS
    # ======================================================

    st.subheader("😊 Positive Comments")

    positive_comments = data[
        data["Sentiment"] == "Positive"
    ]


    if len(positive_comments) > 0:

        st.dataframe(
            positive_comments[["comment", "Sentiment"]],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No positive comments found.")


    # ======================================================
    # NEGATIVE COMMENTS
    # ======================================================

    st.subheader("😡 Negative Comments")

    negative_comments = data[
        data["Sentiment"] == "Negative"
    ]


    if len(negative_comments) > 0:

        st.dataframe(
            negative_comments[["comment", "Sentiment"]],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No negative comments found.")


    # ======================================================
    # DOWNLOAD RESULTS
    # ======================================================

    st.divider()

    st.subheader("⬇️ Download Results")

    csv_data = data.to_csv(
        index=False
    )


    st.download_button(
        label="📥 Download Sentiment Results",
        data=csv_data,
        file_name="sentiment_results.csv",
        mime="text/csv",
        use_container_width=True
    )


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "🤖 Powered by AI • Python • Pandas • Plotly • Streamlit • Ollama"
)