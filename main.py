from flask import Flask, render_template, redirect, request
from pinterest import ReferenceShuffle as Pinterest

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/username', methods=['GET', 'POST'])
def username_search():
    args = request.form
    print(args)
    if request.method == 'POST':
        username, amount_boards, amount_pins = args.values()
        amount_boards = int(amount_boards) if amount_boards else -1
        amount_pins = int(amount_pins) if amount_pins else 12
        # if 'amount_boards' in args.keys():
        #     amount_boards = request.form['amount_boards']
        # if 'amount_pins' in args.keys():
        #     amount_pins = request.form['amount_pins']
        p = Pinterest(username=username)
        boards = p.get_boards_data(username)
        
        data = p.get_random_pins(boards, amount_boards, amount_pins)
        from json import dump
        with open('data.json', 'w') as f:
            dump(data, f, indent=4)
        return render_template('feedpage.html', title=username, shake=data, amount_pins=amount_pins)

@app.route('/board', methods=['GET', 'POST'])
def board_search():
    args = request.form
    print(args)
    if request.method == 'POST':
        from re import search, findall
        username, board_url, amount_pins = args.values()
        amount_pins = int(amount_pins) if amount_pins else 12
        p = Pinterest()
        boards = p.boards(username)
        temp_indexor = {b['url']:b['id'] for b in boards}
        board_path = search(r'(?!(https://([\w]{2,3})?\.pinterest\.com))((/[\w\d\-\_]+){2}/?)', board_url)[0]
        print(board_path)
        if board_path in temp_indexor.keys():
            pins = p.get_board_random_feed(temp_indexor[board_path], amount_pins)
            labels = findall(r'[\w\-\_]+', board_path)
            labels = [l.capitalize() for l in labels]
            labels = [l.replace('-', ' ') for l in labels]
            data = {labels[1]:pins}

            return render_template('feedpage.html', title=':'.join(labels), shake=data, amount_pins=amount_pins)                   
    
@app.route('/keyword', methods=['GET', 'POST'])
def keyword_search():
    args = request.form
    print(args)
    if request.method == 'POST':
        keywords, amount_pins = args.values()
        amount_pins = int(amount_pins) if amount_pins else 12
        p = Pinterest()
        data = p.get_keywords_pins(keywords, amount_pins)
        return render_template('feedpage.html', title=keywords, shake=data, amount_pins=amount_pins)
    

if __name__ == '__main__':
    app.run('localhost', 25565, debug=True)