from flask import Flask, render_template, request, jsonify, make_response
import requests
from bs4 import BeautifulSoup
import datetime

app = Flask(__name__)

def get_drive_files(folder_link):
    """ Scrapes MP3 file links from the given Google Drive folder link """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(folder_link, headers=headers)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    files = []

    for link in soup.find_all("a"):
        href = link.get("href")
        if "drive.google.com/file/d/" in href:  # Extract MP3 file links
            file_id = href.split("/d/")[1].split("/")[0]
            direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            files.append({"name": link.text, "url": direct_url})

    return files

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/set_folder", methods=["POST"])
def set_folder():
    """ Store the user's Google Drive folder link in a cookie """
    data = request.get_json()
    folder_link = data.get("folder_link")

    if not folder_link:
        return jsonify({"error": "No folder link provided"}), 400

    # Create a response object to set a cookie
    response = make_response(jsonify({"message": "Folder link saved!"}))
    expires = datetime.datetime.now() + datetime.timedelta(days=1)
    response.set_cookie("drive_folder", folder_link, expires=expires, httponly=True)

    return response

@app.route("/songs")
def songs():
    """ Get songs from the user's stored Google Drive link """
    folder_link = request.cookies.get("drive_folder")
    
    if not folder_link:
        return jsonify({"error": "No folder link found. Please enter your Drive link."}), 400

    return jsonify(get_drive_files(folder_link))

if __name__ == "__main__":
    app.run(debug=True)
