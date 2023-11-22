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

movie_id = 343611 
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