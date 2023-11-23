import tkinter as tk
from PIL import Image, ImageTk
import io
import urllib.parse
import urllib.request
import requests
import re

root = tk.Tk()
root.geometry('800x800')
root.resizable(width=True, height=True)

main_frame = tk.Frame(root, bg='WHITE')
main_frame.pack(fill=tk.BOTH, expand=True)
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(0, weight=1)

#raw_data = urllib.request.urlopen('https://image.tmdb.org/t/p/w500/1E5baAaEse26fej7uHcjOgEE2t2.jpg').read()

def get_movie_poster(search_movie):
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


# Misspelled on purpose to test if movie is not found.
search_movie = "Toy Story (1995)"
search_movie = re.sub("\(.*?\)","",search_movie)
image_obj_1 = get_movie_poster(search_movie)

label_img_1 = tk.Label(
        main_frame,
        image=image_obj_1,
        bg='WHITE',
        padx=2,
        )

label_img_1.grid(column=0, row=0)

search_movie = "Fast X"
image_obj_2 = get_movie_poster(search_movie)

label_img_2 = tk.Label(
        main_frame,
        image=image_obj_2,
        bg='WHITE',
        padx=2
        )

label_img_2.grid(column=1, row=0)

root.mainloop()
