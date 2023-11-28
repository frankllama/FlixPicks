# Import necessary libraries and modules
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PIL import ImageTk, Image 
from tkinter import ttk
import numpy as np
import tkinter as tk
import pandas as pd
import re


# Define a class for movie recommendations
class RecommendationMovie:
    def __init__(self):
        # Initialize the class by reading movie and ratings data, and creating the Tkinter window
        self.movies = pd.read_csv("movies.csv")
        self.root = tk.Tk()
        self.root.geometry("1200x1200")
        self.root.title("Movie Recommendation")

        # Set dark gray background color
        self.root.configure(bg='#222222')

        # Create and pack Tkinter widgets (Canvas, Frame, Label, Text, Button, Scrollbar)
        self.canvas = tk.Canvas(self.root, bg='#222222', highlightthickness=0)
        self.frame = ttk.Frame(self.canvas)  # Use ttk for themed widgets

        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        path = "disney.jpg"
        img = Image.open(path)
        self.img = ImageTk.PhotoImage(img)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)

        # Set title label in the middle with transparent background
        self.label = tk.Label(self.frame, text="FlixPicks", font=('Arial', 60, 'bold', 'italic'), fg='Gold', bg='#222222', bd=0, highlightthickness=0)
        self.label.pack(side=tk.TOP, pady=(100, 0))

        # Set search box in the middle with no background
        self.textBox = tk.Text(self.frame, height=2, font=('Arial', 15, 'bold'), bg='#aaaaaa', fg='black')
        self.textBox.pack(side=tk.TOP, pady=10)
        self.textBox.config(highlightbackground='#aaaaaa', bd=0, insertbackground='gray')

        self.button = tk.Button(self.frame, text="Recommend Movie", font=('Arial', 20, 'bold'), command=self.show_recommended_movie, bg='#555555', fg='white')
        self.button.pack(side=tk.TOP, pady=10)

        self.recommended_label = tk.Label(self.frame, text="", font=('Arial', 15, 'bold'), fg='white')
        self.recommended_label.pack(pady=20)

        # Preprocess movie titles for text similarity
        self.movies["clean_title"] = self.movies["title"].apply(self.clean_title)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.tfidf = self.vectorizer.fit_transform(self.movies["clean_title"])

        # Configure the canvas to update scroll region
        self.frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Start Tkinter main event loop
        self.root.mainloop()

    def clean_title(self, title):
        # Clean movie titles by removing non-alphanumeric characters
        return re.sub("[^a-zA-Z0-9 ]", "", title)

    def on_configure(self, event):
        # Update scroll region when canvas size changes
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        # Handle mouse wheel scrolling
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")


    def search(self):
        # Perform movie search based on user input
        movie_title = self.textBox.get('1.0', tk.END)
        title = self.clean_title(movie_title)
        query_vec = self.vectorizer.transform([title])
        similarity = cosine_similarity(query_vec, self.tfidf).flatten()
        indices = np.argpartition(similarity, -5)[-5:]
        result = self.movies.iloc[indices][::-1]
        return result

    def show_recommended_movie(self):
        # Display recommended movies in the Tkinter label
        recommended_movies = self.search()
        recommended_movie = "Recommended Movies:\n"

        movie_id = recommended_movies.iloc[0]["movieId"]

        # Iterate through similar movies and display titles and genres
        for _, movie in self.find_similar_movies(movie_id).iterrows():
            recommended_movie += f"• {movie['title']} - Genre: {movie['genres']}\n"

        self.recommended_label.config(text=recommended_movie)

    def find_similar_movies(self, movie_id):
        # Calculate movie recommendations based on user ratings and return a DataFrame with scores, titles, and genres
        similar_users = self.ratings[(self.ratings["movieId"] == movie_id) & (self.ratings["rating"] > 4)]["userId"].unique()
        similar_user_recs = self.ratings[(self.ratings["userId"].isin(similar_users)) & (self.ratings["rating"] > 4)]["movieId"]

        similar_user_recs = similar_user_recs.value_counts() / len(similar_users)
        similar_user_recs = similar_user_recs[similar_user_recs > 0.1]

        all_users = self.ratings[(self.ratings["movieId"].isin(similar_user_recs.index)) & (self.ratings["rating"] > 4)]
        all_user_recs = all_users["movieId"].value_counts() / len(all_users["userId"].unique())

        rec_percentages = pd.concat([similar_user_recs, all_user_recs], axis=1)
        rec_percentages.columns = ["similar", "all"]

        rec_percentages["score"] = rec_percentages["similar"] / rec_percentages["all"]

        rec_percentages = rec_percentages.sort_values("score", ascending=False)

        # Merge with movie data and return top 10 recommendations with scores, titles, and genres
        return rec_percentages.head(10).merge(self.movies, left_index=True, right_on="movieId")[["score","title","genres"]]

# Instantiate the class and run the Tkinter application
app = RecommendationMovie()












