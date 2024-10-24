import pandas as pd
import streamlit as st
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Page config
st.set_page_config(
    page_title="Smart Course Search Tool",
    layout="wide"
)


# Initialize the sentence transformer model
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')


# Load or create embeddings
@st.cache_data
def load_or_create_embeddings(df, _model):
    embedding_file = 'course_embeddings.pkl'
    try:
        with open(embedding_file, 'rb') as f:
            embeddings = pickle.load(f)
            st.success("Loaded existing embeddings")
    except FileNotFoundError:
        st.info("Creating new embeddings... This may take a few minutes.")
        # Combine title and description for better semantic understanding
        texts = df['Title'] + " " + df['Description']
        embeddings = _model.encode(texts.tolist(), show_progress_bar=True)
        with open(embedding_file, 'wb') as f:
            pickle.dump(embeddings, f)
        st.success("Created and saved new embeddings")
    return embeddings


# Load the course data
@st.cache_data
def load_data():
    try:
        with open('courses_data.pkl', 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()


# Perform semantic search using cosine similarity
def semantic_search(query, df, embeddings, _model, top_k=10):
    # Get query embedding
    query_embedding = _model.encode([query])

    # Calculate similarity scores
    similarity_scores = cosine_similarity(query_embedding, embeddings)[0]

    # Get top k matches
    top_indices = np.argsort(similarity_scores)[-top_k:][::-1]
    top_scores = similarity_scores[top_indices]

    return pd.DataFrame({
        'index': top_indices,
        'similarity_score': top_scores
    })


# Skip LLM enhancement if quota issues are present
def enhance_results_with_llm(query, results_df, df):
    return None  # Return None or a placeholder


def main():
    st.title("🎓 Smart Course Search Tool")
    st.write("Search through our course database using natural language queries.")

    # Load data and model
    df = load_data()
    model = load_model()

    if df.empty:
        st.error("No data available. Please check the data file.")
        return

    # Load or create embeddings
    embeddings = load_or_create_embeddings(df, model)

    # Search interface
    query = st.text_input("🔍 What would you like to learn?",
                          help="Try natural language queries like 'beginner friendly machine learning courses' or 'advanced web development with practical projects'")

    if query:
        with st.spinner("Searching for the most relevant courses..."):
            # Get semantic search results
            results_df = semantic_search(query, df, embeddings, model)

            # Skipping LLM due to quota issues
            llm_analysis = enhance_results_with_llm(query, results_df, df)

            if not results_df.empty:
                st.success(f"Found {len(results_df)} relevant courses")

                # Show LLM analysis if available (this will be None or skipped)
                if llm_analysis:
                    with st.expander("💡 AI Analysis of Results", expanded=True):
                        st.write(llm_analysis)

                # Display results
                for _, row in results_df.iterrows():
                    course = df.iloc[int(row['index'])]
                    similarity_score = row['similarity_score']

                    with st.expander(f"📘 {course['Title']} (Relevance: {similarity_score:.2%})", expanded=True):
                        cols = st.columns([2, 1])

                        with cols[0]:
                            st.markdown("### Description")
                            st.write(course['Description'])

                            if 'Curriculum' in course and pd.notna(course['Curriculum']):
                                st.markdown("### Curriculum")
                                st.write(course['Curriculum'])

                        with cols[1]:
                            st.markdown("### Course Details")
                            if 'Duration' in course and pd.notna(course['Duration']):
                                st.write(f"⏱️ **Duration:** {course['Duration']}")
                            if 'Level' in course and pd.notna(course['Level']):
                                st.write(f"📊 **Level:** {course['Level']}")
                            if 'Course Link' in course and pd.notna(course['Course Link']):
                                st.markdown(f"🔗 [Go to Course]({course['Course Link']})")
            else:
                st.warning("No courses found matching your query. Try different keywords.")

    with st.sidebar:
        st.header("Search Settings")
        st.markdown("""
        This search tool uses:
        - Semantic embeddings for understanding context
        - Relevance scoring
        """)


if __name__ == "__main__":
    main()
