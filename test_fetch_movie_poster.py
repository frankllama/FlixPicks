import tkinter as tk
from PIL import Image, ImageTk
import io
import urllib.parse
import urllib.request
import requests

root = tk.Tk()
root.geometry('800x800')
root.resizable(width=False, height=False)

main_frame = tk.Frame(root, bg='WHITE')
main_frame.pack(fill=tk.BOTH, expand=True)
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(0, weight=1)

#raw_data = urllib.request.urlopen('https://image.tmdb.org/t/p/w500/1E5baAaEse26fej7uHcjOgEE2t2.jpg').read()

# Get movie id from searching a movie
#movie_id = 343611
search_movie = "Jack Reacher: Never Go Back"
get_movie_info = requests.get('https://api.themoviedb.org/3/search/movie?query={}&api_key=0445e86644dc5e6dde39ce605f795cd5&language=en-US'.format(search_movie))
movie_info = get_movie_info.json()
# A list of dictionary, results is a list that holds a dictionary. 
# So get data in first index (0) of key 'id'
movie_id = movie_info['results'][0]['id']
#print(movie_id)

# Get movie poster path from it's id with the tmdb api.
response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=0445e86644dc5e6dde39ce605f795cd5&language=en-US'.format(movie_id))
data = response.json()
movie_poster = "https://image.tmdb.org/t/p/w500/" + data['poster_path']

raw_data = urllib.request.urlopen(movie_poster).read()

image_obj = ImageTk.PhotoImage(Image.open(io.BytesIO(raw_data)))

label_img = tk.Label(
        main_frame,
        image=image_obj,
        bg='WHITE'
        )

label_img.grid(column=0, row=0)

root.mainloop()
