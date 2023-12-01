# Import necessary libraries and modules
from sklearn.feature_extraction.text import TfidfVectorizer # need for both algorithms
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel 
from PIL import ImageTk, Image 
from tkinter import ttk
import numpy as np
import tkinter as tk
import pandas as pd # needed for both algorithms
import re
import io
import urllib.parse
import urllib.request
import requests


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

        self.recommended_label = tk.Label(self.frame, text="", font=('Arial', 15, 'bold'), fg='black')
        self.recommended_label.pack(side=tk.TOP, pady=20)

        # Create labels for regular movie posters.
        self.r_movie_poster_label_0 = tk.Label(self.frame, image="", bg='WHITE')
        self.r_movie_poster_label_0.pack()

        # Add a separator frame with a background color as a line
        separator_frame = tk.Frame(self.frame, height=2, bg='white')
        separator_frame.pack(side=tk.TOP, fill=tk.X)

        self.recommended_label2 = tk.Label(self.frame, text="", font=('Arial', 15, 'bold'), fg='black')
        self.recommended_label2.pack(side=tk.BOTTOM, pady=20)

        # Create labels for displaying the netflix movie posters.
        self.n_movie_poster_label_0 = tk.Label(self.frame, image="", bg='WHITE')
        self.n_movie_poster_label_0.pack()

        # Preprocess movie titles for text similarity
        self.movies["clean_title"] = self.movies["title"].apply(self.clean_title)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.tfidf = self.vectorizer.fit_transform(self.movies["clean_title"])

        self.movie_title = self.textBox.get('1.0', tk.END)
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
        #movie_title = self.textBox.get('1.0', tk.END)
        self.movie_title = self.textBox.get('1.0', tk.END).strip()  # Strip to remove leading/trailing whitespaces
      
        title = self.clean_title(self.movie_title)
        query_vec = self.vectorizer.transform([title])
        similarity = cosine_similarity(query_vec, self.tfidf).flatten()
        indices = np.argpartition(similarity, -5)[-5:]
        result = self.movies.iloc[indices][::-1]
        return result


    def get_movie_poster(self, search_movie):
        # Get movie id from searching a movie
        #movie_id = 343611
        #search_movie = "Jack Reacher: Never Go Back"
        get_movie_info = requests.get('https://api.themoviedb.org/3/search/movie?query={}&api_key=0445e86644dc5e6dde39ce605f795cd5&language=en-US'.format(search_movie))
        movie_info = get_movie_info.json()
        #print(movie_info)
        if movie_info['total_results'] == 0:
            #Image.new('RGB', (250, 375), color = (0,0,0)).save('Img.jpg')
            blank_image = ImageTk.PhotoImage(Image.open('Img.jpg'))
            return blank_image
        # A list of dictionary, results is a list that holds a dictionary. 
        # So get data in first index (0) of key 'id'
        movie_id = movie_info['results'][0]['id']
        #print(movie_id)

        # Get movie poster path from it's id with the tmdb api.
        response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=0445e86644dc5e6dde39ce605f795cd5&language=en-US'.format(movie_id))
        data = response.json()
        movie_poster = "https://image.tmdb.org/t/p/w500/" + data['poster_path']

        raw_data = urllib.request.urlopen(movie_poster).read()

        #image_obj = ImageTk.PhotoImage(Image.open(io.BytesIO(raw_data)))
        # Original movie poster size is 500x750 pixels, so just halved it.
        image_obj = ImageTk.PhotoImage(Image.open(io.BytesIO(raw_data)).resize((250,375)))

        return image_obj


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
        input_title = self.movie_title
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
            #search_movie = re.sub("\(.*?\)","",search_movie)
            #image_obj_0 = self.get_movie_poster(netflix_movies[0])

            # label_img_0 = tk.Label(
            #     self.frame,
            #     image=image_obj_0,
            #     bg='WHITE',
            #     padx=2,
            # )

            #label_img_0.grid(row=0)

            return netflix_movies
# ... (previous code)


    def show_recommended_movie(self):
        # Display recommended movies in the Tkinter label
        recommended_movies = self.search()
        recommended_movie = "Recommended by system using collaboraHve:\n"

        movie_id = recommended_movies.iloc[0]["movieId"]
        
        clean_recommended_movies_list = []

        # Iterate through similar movies and display titles and genres
        for _, movie in self.find_similar_movies(movie_id).iterrows():
            recommended_movie += f"• {movie['title']} - Genre: {movie['genres']}\n"
            clean_recommended_movies_list.append(re.sub("\(.*?\)","", movie['title']))

        self.recommended_label.config(text=recommended_movie)

        if clean_recommended_movies_list is not None:
            rmc_image_obj_0 = self.get_movie_poster(clean_recommended_movies_list[0])
            self.r_movie_poster_label_0.image = rmc_image_obj_0 # Anchor the image object into the widget.
            self.r_movie_poster_label_0.config(image=rmc_image_obj_0)
        else:
            blank_image = ImageTk.PhotoImage(Image.open('Img.jpg'))
            self.r_movie_poster_label_0.image = blank_image
            self.r_movie_poster_label_0.config(image=blank_image)

        netflix_movies = "Recommended by content-based filtering:\n"
        netflix_list = self.reccomend_movie()
        if netflix_list is not None:
            for i in netflix_list:
                netflix_movies += i + "\n"
                
        self.recommended_label2.config(text=netflix_movies)
        
        #print(netflix_list[0])
        if netflix_list is not None:
            image_obj_0 = self.get_movie_poster(netflix_list[0])
            self.n_movie_poster_label_0.image = image_obj_0 # Anchor the image object into the widget.
            self.n_movie_poster_label_0.config(image=image_obj_0)
        else:
            blank_image = ImageTk.PhotoImage(Image.open('Img.jpg'))
            self.n_movie_poster_label_0.image = blank_image
            self.n_movie_poster_label_0.config(image=blank_image)
# ... (rest of the code)
        #netflix_movies = " "
        #netflix_list = self.reccomend_movie()
        #for i in netflix_list:
        #    netflix_movies += i
        
       # self.recommended_label2.config(text=netflix_movies)


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
    

if __name__ == "__main__":
    # Instantiate the class and run the Tkinter application
    app = RecommendationMovie()


