from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import tkinter as tk
import pandas as pd
import re

class RecommendationMovie:
    def __init__(self):
        self.movies = pd.read_csv("movies.csv")
        self.root = tk.Tk()
        self.root.geometry("800x900")
        self.root.title("Movie Recommendation")
        self.root.configure(bg='lightblue')

        self.label = tk.Label(self.root, text="Type Movie", font=('Arial', 30, 'bold'), bg='lightblue')
        self.label.pack(padx=20, pady=30)

        self.textBox = tk.Text(self.root, height=2, font=('Arial', 15, 'bold'))
        self.textBox.pack(padx=50, pady=30)

        self.button = tk.Button(self.root, text="Find Recommended Movie", font=('Arial', 20, 'bold'), command=self.show_recommended_movie)
        self.button.pack()

        self.recommended_label = tk.Label(self.root, text="", font=('Arial', 15, 'bold'), bg='lightblue')
        self.recommended_label.pack(pady=20)

        self.movies["clean_title"] = self.movies["title"].apply(self.clean_title)
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2))
        self.tfidf = self.vectorizer.fit_transform(self.movies["clean_title"])

        self.root.mainloop()

    def clean_title(self, title):
        return re.sub("[^a-zA-Z0-9 ]", "", title)

    def search(self):
        movie_title = self.textBox.get('1.0', tk.END)
        title = self.clean_title(movie_title)
        query_vec = self.vectorizer.transform([title])
        similarity = cosine_similarity(query_vec, self.tfidf).flatten()
        indices = np.argpartition(similarity, -5)[-5:]
        result = self.movies.iloc[indices][::-1]
        return result

    def show_recommended_movie(self):
        recommended_movies = self.search()
        recommended_movie = "Recommended Movies:\n"
        
        for movie in recommended_movies['title']:
            recommended_movie += f"• {movie}\n"
        
        self.recommended_label.config(text=recommended_movie)


# Instantiate the class and run the Tkinter application
app = RecommendationMovie()








