# import httpagentparser
from flask import Flask, request, abort, render_template, send_from_directory, jsonify, session
import Jedol_Answer as ds
import jedol2ChatDbFun as chatDB
import datetime
import os
app = Flask(__name__)

app.secret_key = 'GTalkStory'
# loader = WebBaseLoader(web_path="https://jeju-s.jje.hs.kr/jeju-s/0102/history")
# chat_story=TextLoader("data\story.txt", encoding='utf-8').load()[0].page_content

@app.route('/')
def home():
    if 'token' not in session:
        session['token'] = ds.rnd_str(n=20, type="s")
    return render_template("/html/index.html", token=session['token'])

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('templates/files', filename, as_attachment=True)

@app.errorhandler(404)
def not_found(e):
    return render_template('/html/404.html'), 404

@app.route('/<path:page>')
def page(page):
    if 'token' not in session:
        session['token'] = ds.rnd_str(n=20, type="s")

    if ".html" in page:
       return render_template(page, token=session['token'])
    else:
       return send_from_directory("templates", page)

# AI 쿼리 경로
@app.route("/query", methods=["POST"])
def query():
    
    #return jsonify({"answer": '제돌이 공부 중입니다. 14시 ~ 15시까지'})
    query = request.json.get("query")
    
    with open("C:\\V-STEAM\\texts\\chat.txt", "w", encoding="utf-8") as outfile:
        try:
            outfile.write(query)
        except:
            print("Error writing to chat.txt")


# if __name__ == '__main__':
#     app.run(debug=True, host="0.0.0.0", port=5001)
if __name__ == '__main__':
    app.run(ssl_context=('openSSL/cert.pem', 'openSSL/key.pem'),debug=True,  port=5001)  