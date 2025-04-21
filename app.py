import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder

# Load data
ratings = pd.read_csv("ml-latest-small/ratings.csv")
movies = pd.read_csv("ml-latest-small/movies.csv")

# Encode user and movie IDs
user_encoder = LabelEncoder()
item_encoder = LabelEncoder()
ratings['user'] = user_encoder.fit_transform(ratings['userId'])
ratings['item'] = item_encoder.fit_transform(ratings['movieId'])

# Create user-item matrix
user_item_matrix = ratings.pivot_table(index='user', columns='item', values='rating').fillna(0)
user_similarity = cosine_similarity(user_item_matrix)
user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

# Recommendation functions
def get_similar_users(user_id, top_n=5):
    similar_users = list(user_similarity_df[user_id].sort_values(ascending=False).index[1:top_n+1])
    return similar_users

def recommend_movies(user_id, top_n=5):
    similar_users = get_similar_users(user_id, top_n=10)
    user_rated_items = set(ratings[ratings['user'] == user_id]['item'])
    recommended_items = {}

    for sim_user in similar_users:
        sim_user_ratings = ratings[ratings['user'] == sim_user]
        for _, row in sim_user_ratings.iterrows():
            if row['item'] not in user_rated_items:
                if row['item'] not in recommended_items:
                    recommended_items[row['item']] = []
                recommended_items[row['item']].append(row['rating'])

    avg_ratings = {item: np.mean(ratings) for item, ratings in recommended_items.items()}
    sorted_items = sorted(avg_ratings.items(), key=lambda x: x[1], reverse=True)
    top_items = [int(item) for item, rating in sorted_items[:top_n]]
    movie_ids = item_encoder.inverse_transform(top_items)
    recommended_titles = movies[movies['movieId'].isin(movie_ids)]['title'].tolist()
    return recommended_titles

# Streamlit UI
st.title("🎯 Product/Movie Recommendation Engine")
user_input = st.selectbox("Select a user:", ratings['user'].unique())
top_n = st.slider("Number of recommendations:", 1, 10, 5)

if st.button("Recommend"):
    recs = recommend_movies(user_input, top_n)
    st.subheader("Recommended for you:")
    for movie in recs:
        st.write(f"✅ {movie}")
