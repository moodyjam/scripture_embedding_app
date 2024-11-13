import streamlit as st
import pandas as pd
import numpy as np
import openai
import os

# Set OpenAI API key
# openai.api_key = os.getenv("OPENAI_API_KEY")

# ========================================
# Main Application UI
# ========================================
def main_app():
    """
    Render the main application content for logged-in users.
    """
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_embedding(text, model="text-embedding-3-small"):
        """
        Generate embeddings for the provided text using the specified OpenAI model.

        Parameters:
        - text (str): The input text to generate embeddings for.
        - model (str): The OpenAI model to use for embeddings.

        Returns:
        - list: The embedding vector for the input text.
        """
        try:
            # Clean the input text
            clean_text = text.replace("\n", " ").strip()
            
            # Generate embeddings
            response = client.embeddings.create(input=[clean_text], model=model)
            
            # Extract the embedding
            embedding = response.data[0].embedding
            return embedding
        except openai.error.InvalidRequestError as e:
            print(f"Invalid request: {e}")
        except openai.error.AuthenticationError:
            print("Authentication failed. Please check your OpenAI API key.")
        except openai.error.RateLimitError:
            print("Rate limit exceeded. Please try again later.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
    # Load custom CSS
    def local_css():
        st.markdown("""
        <style>
        /* Add your custom CSS here */
        body {
            background-color: #f5f5f5;
        }
        .stButton button {
            background-color: #4B3832;
            color: white;
        }
        .stMarkdown h3 {
            color: #854442;
        }
        </style>
        """, unsafe_allow_html=True)
        
    local_css()

    # Title and Description
    st.title("📖 Scripture Embedding Search")
    st.markdown("""
    Enter a query to find the most similar verses in the selected scriptures. Adjust the number of verses you want to see.
    """)

    # Select Books
    st.markdown("### Select books to include in the search")
    include_bom = st.checkbox("Book of Mormon", value=True, key="include_bom")
    include_nt = st.checkbox("New Testament", value=False, key="include_nt")
    include_ot = st.checkbox("Old Testament", value=False, key="include_ot")

    # User Inputs
    input_text = st.text_input("Enter your query:", key="input_text")
    top_n = st.slider("Number of verses to display:", min_value=1, max_value=50, value=10, key="top_n")

    # Load Data and Embeddings
    @st.cache_data
    def load_bom_data():
        df_bom = pd.read_csv("book_of_mormon.csv")
        embeddings_bom = np.load("normed_small_embeddings_bom.npy")
        return df_bom, embeddings_bom

    @st.cache_data
    def load_nt_data():
        df_nt = pd.read_csv("new_testament.csv")
        embeddings_nt = np.load("normed_small_embeddings_nt.npy")
        embeddings_nt = embeddings_nt / np.linalg.norm(embeddings_nt, axis=1, keepdims=True)
        return df_nt, embeddings_nt

    @st.cache_data
    def load_ot_data():
        df_ot = pd.read_csv("old_testament.csv")
        embeddings_ot = np.load("normed_small_embeddings_ot.npy")
        embeddings_ot = embeddings_ot / np.linalg.norm(embeddings_ot, axis=1, keepdims=True)
        return df_ot, embeddings_ot

    # Function to find similar verses
    def find_most_similar_verses(input_text, topk, comparison_embeddings, df):
        new_embedding = get_embedding(input_text)
        if new_embedding is None:
            return pd.DataFrame()  # Return empty DataFrame if embedding failed
        
        similarities = comparison_embeddings @ (np.array(new_embedding) / np.linalg.norm(new_embedding))
        sorted_indices = np.argsort(similarities)[::-1][:topk]
        results = df.iloc[sorted_indices].copy()
        results['Similarity Score'] = similarities[sorted_indices]
        return results

    # Process Input and Display Results
    if st.button("Find Similar Verses", key="find_similar_button"):
        if input_text.strip() == "":
            st.warning("Please enter a query to proceed.")
        else:
            dfs = []
            embeddings_list = []
            if include_bom:
                df_bom, embeddings_bom = load_bom_data()
                dfs.append(df_bom)
                embeddings_list.append(embeddings_bom)
            if include_nt:
                df_nt, embeddings_nt = load_nt_data()
                dfs.append(df_nt)
                embeddings_list.append(embeddings_nt)
            if include_ot:
                df_ot, embeddings_ot = load_ot_data()
                dfs.append(df_ot)
                embeddings_list.append(embeddings_ot)
            
            if not dfs:
                st.warning("Please select at least one book to proceed.")
            else:
                # Combine dataframes and embeddings
                df_combined = pd.concat(dfs, ignore_index=True)
                embeddings_combined = np.vstack(embeddings_list)

                with st.spinner("Finding similar verses..."):
                    results = find_most_similar_verses(input_text, top_n, embeddings_combined, df_combined)
                if results.empty:
                    st.error("Failed to retrieve embeddings. Please try again.")
                else:
                    st.success(f"Top {top_n} verses similar to your query:")
                    
                    for idx, row in results.iterrows():
                        book = row['Book']
                        chapter = row['Chapter']
                        verse_number = row['Verse Number']
                        verse_text = row['Verse Text']
                        similarity = row['Similarity Score']
                        
                        # Use columns for layout
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"### {book} {chapter}:{verse_number}")
                        with col2:
                            st.markdown(f"**Similarity:** `{similarity:.4f}`")
                        st.markdown(f"_{verse_text}_")
                        st.markdown("---")
                    
if __name__ == '__main__':
    main_app()