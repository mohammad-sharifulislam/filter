from logging import DEBUG
from flask import Flask, render_template, request
from urllib.error import HTTPError
from flask.helpers import get_template_attribute
from googleapiclient.discovery import build
import urllib.request
from nudenet import NudeClassifier
from werkzeug.utils import redirect
from  datetime import date

app = Flask(__name__)


api_key = 'AIzaSyCpRx5d6i9wo2mRWN0FZDIDo6nYGkvY8o8'
classifier = NudeClassifier()

words = {"porn", "sex", 'sex,' "Sexy", "sexy", 'Amateur', 'Anal', 'Arab', 'Asian',
         'Ass', 'Babe', 'Bbw', 'Bdsm', 'Beauty', 'Boobs', 'BigCock', 'Bisexual', 'Black', 'seduction', 'porno'}


vid_list = []

youtube = build('youtube', 'v3', developerKey=api_key)


def listing(response, vid_list):

    vid_inf = []
    vid_list1 = response['items']
    listing.counter += 1

    for vid in vid_list1:
        image_url = vid['snippet']['thumbnails']['high']['url']
        description = vid['snippet']['description']
        description = set((description.lower()).split(' '))
        title = vid['snippet']['title']

        dc = {}
        title = title.lower()
        try:
            dc[title] = {
                "id": vid['id']['videoId'],
                "image_url": image_url,
                "description": description
            }
        except KeyError:
            continue
        vid_inf.append(dc)

    for vid in vid_inf:
        for title, inf in vid.items():
            title = title.lower()
            title2 = title
            title = set(title.split(' '))
            description = inf['description']

            if words.intersection(description) == set() and words.intersection(title) == set():

                try:
                    urllib.request.urlretrieve(inf['image_url'], "img.jpg")
                    image_rating = classifier.classify(
                        'img.jpg')['img.jpg']['unsafe']

                    if image_rating < 0.1:

                        dic = {}
                        dic[title2] = {
                            "id": inf['id'],
                            "img": inf['image_url']
                        }
                        vid_list.append(dic)

                except :
                    continue

listing.counter = 0


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        form = request.form
        word_s = form['requested']
        request_y = youtube.search().list(
            part="snippet",
            maxResults=5,
            q=word_s,
            order="rating",
            safeSearch="strict"
        )
        vid_list.clear()
        response = request_y.execute()

        listing(response, vid_list)
        while(len(vid_list) < 20):
            if listing.counter >= 1:
                try:
                    new_req = youtube.search().list_next(request_y, response)
                    new_res = new_req.execute()
                    listing(new_res, vid_list)
                    request_y = new_req
                    response = new_res
                except AttributeError:
                    continue

        return redirect('/list')

    return render_template("index.html")


@app.route('/list')
def listView():
    vids = vid_list
    return render_template("list.html", vids=vids)

@app.route('/view/<id>')
def view(id):
    return render_template('view.html',id=id)


@app.route("/take_note", methods=['POST', 'GET'])
def take_note():
    if request.is_json:
        req = request.get_json()
        notes = req['Note']
        time = date.today()
        time = time.strftime("%B %d, %Y")
        path = r"E:\programs\programing\Python\tube_app"
        note = open(f"{path}/notes.txt", "a+")
        note.write('\n')
        note.write(time)
        note.write('\n')
        note.write(notes)
        note.close()
        

    return "hello"


app.run(debug=True)
