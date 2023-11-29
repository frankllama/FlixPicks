# Import necessary libraries and modules
from sklearn.feature_extraction.text import TfidfVectorizer # need for both algorithms
from sklearn.metrics.pairwise import cosine_similarity
from PIL import ImageTk, Image 
from tkinter import ttk
import numpy as np
import tkinter as tk
import pandas as pd # needed for both algorithms
import re

from sklearn.metrics.pairwise import linear_kernel 

# Define a class for movie recommendations
class RecommendationMovie:
    def __init__(self):
        # Initialize the class by reading movie and ratings data, and creating the Tkinter window
        self.movies = pd.read_csv("movies.csv")
        self.root = tk.Tk()
        self.root.geometry("1200x1200")
        self.root.title("Movie Recommendation")
        self.ratings = pd.read_csv("ratings.csv")


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

        self.recommended_label2 = tk.Label(self.frame, text="", font=('Arial', 15, 'bold'), fg='white')
        self.recommended_label2.pack(pady=20)

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
        global movie_title 
        movie_title = self.textBox.get('1.0', tk.END)
        print(movie_title)
        title = self.clean_title(movie_title)
        query_vec = self.vectorizer.transform([title])
        similarity = cosine_similarity(query_vec, self.tfidf).flatten()
        indices = np.argpartition(similarity, -5)[-5:]
        result = self.movies.iloc[indices][::-1]
        return result

    def reccomend_movie(self):
        df = pd.read_csv("netflix.csv")
        # Fills in empty values with a space
        df = df.fillna('')

        # Combines all attributes into a single dataframe
        df['Combined_Info'] = (
            df['genres'] + ' ' +
            df['description'] + ' ' +
            df['director'] + ' ' +
            df['cast'] + ' ' +
            df['country'] + ' ' +
            df['rating']
        )

        # Create a TF-IDF vectorizer for genre 
        # Stop words are common words like: the or are (We don't want to count those bc they don't contribute to the plot comparison)
        genre_vectorizer = TfidfVectorizer(stop_words='english')
        genre_tfidf_matrix = genre_vectorizer.fit_transform(df['genres'])

        # Create a TF-IDF vectorizer for the combined info
        combined_info_vectorizer = TfidfVectorizer(stop_words='english')
        combined_info_tfidf_matrix = combined_info_vectorizer.fit_transform(df['Combined_Info'])


        # Prompt user for a movie title
        # input_title = self.textBox.get('1.0', tk.END)
        # input_title = "Breaking Bad"
        # print(input_title)
        # Check if the entered title is in the dataset
        input_title = movie_title
        if input_title not in df['title'].values:
            print("Movie title not found in the dataset.")
        else:
        
            # Get the genre and combined info of the input title
            input_genre = df[df['title'] == input_title]['genres'].iloc[0]
            input_combined_info = df[df['title'] == input_title]['Combined_Info'].iloc[0]

            # Transform the input genre and combined info using the respective TF-IDF vectorizers
            input_genre_tfidf = genre_vectorizer.transform([input_genre])
            input_combined_info_tfidf = combined_info_vectorizer.transform([input_combined_info])

            # Calculate the cosine similarities
            genre_cosine_similarities = linear_kernel(input_genre_tfidf, genre_tfidf_matrix).flatten()
            combined_info_cosine_similarities = linear_kernel(input_combined_info_tfidf, combined_info_tfidf_matrix).flatten()

            # Combine the similarities with a weight for the genre
            weight_genre = 0.7 
            weighted_cosine_similarities = weight_genre * genre_cosine_similarities + (1 - weight_genre) * combined_info_cosine_similarities

            # Get the indices of movies with the highest similarity
            similar_movies = weighted_cosine_similarities.argsort()[:-1][::-1]  # Exclude the input movie itself

            # creates empty list to put the reccomended movies in
            netflix_movies = []

            # Print recommended movies
            print("\nRecommended Movies:")
            for i in similar_movies[:5]:  # Print the top 5 recommended movies
                print(f"{df['title'].iloc[i]} - Genre: {df['genres'].iloc[i]} Similarity: {weighted_cosine_similarities[i]:.2f}")

                # puts movies in a list
                netflix_movies.append(df['title'].iloc[i])
                
            print(netflix_movies)
            return netflix_movies

    def show_recommended_movie(self):
        # Display recommended movies in the Tkinter label
        # movie_title = "Breaking Bad"
        recommended_movies = self.search()
        recommended_movie = "Recommended Movies:\n"

        movie_id = recommended_movies.iloc[0]["movieId"]

        # Iterate through similar movies and display titles and genres
        for _, movie in self.find_similar_movies(movie_id).iterrows():
            recommended_movie += f"• {movie['title']} - Genre: {movie['genres']}\n"

        self.recommended_label.config(text=recommended_movie)

        netflix_movies = " "
        netflix_list = self.reccomend_movie()
        for i in netflix_list:
            netflix_movies += i
        
        self.recommended_label2.config(text=netflix_movies)

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












