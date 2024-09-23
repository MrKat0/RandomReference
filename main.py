from flask import Flask, render_template, redirect, request
from pinterest import *

app = Flask(__name__)

def get_random_template(prev_url, data, boardname:str='', keyword:str=''):
    if prev_url == '/dashboard':
        data = {boardname:data}
    if prev_url == '/keyword':
        data = {keyword: data}
    

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/username', methods=['GET', 'POST'])
def username():
    username = request.form['username']
    print(username)
    return render_template('random_pins.html', data)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    url = request.form['dashboard']
    with Pinterest() as p:
        id = p.get_board_id(url)
        temp = [-1]
        pins = []
        while pins < 1000:
            temp = p.board_feed(id)
            if not temp:
                break
            pins += temp
        if len(pins) <= 12:
            data = {}
    return render_template('random_pins.html', data)
    
@app.route('/?keyword', methods=['GET'])
def keyword():
    data = get_random_template()
    return render_template('random_pins.html', data)
    

if __name__ == '__main__':
    app.run('localhost', 25565, debug=True)