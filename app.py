import tkinter as tk
import pandas as pd
import re

class RecommendationMovie:
    def __init__(self):

        self. movies = pd.read_csv("movies.csv")
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

        self.root.mainloop()

    def show_recommended_movie(self):
        movie_title = self.textBox.get('1.0', tk.END)
        recommended_movie = f"Recommended Movie: {movie_title.strip()}"
        self.recommended_label.config(text=recommended_movie)
    

    
    def clean_title_movie_from_dataset(self,title):
         return re.sub("[^a-zA-Z0-9]", "", title)
    
    def return_all_clean_movie(self):
        self.movies["title"] = self.movies["title"].apply(self.clean_title_movie_from_dataset)
        print(self.movies)


# Instantiate the class and run the Tkinter application
app = RecommendationMovie()

app.return_all_clean_movie()









