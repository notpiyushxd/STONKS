import requests
import random
from flask import Flask, render_template, session, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'stonks_secret_99'

def calculate_price(meme_id):
    random.seed(meme_id)
    base = random.randint(100, 2000)
    multiplier = random.choice([0.8, 1.2, 1.5, 2.0])
    return round(base * multiplier, 2)

@app.route('/')
def index():
    if 'balance' not in session:
        session['balance'] = 10000.0
        session['portfolio'] = {}

    try:
        response = requests.get('https://api.imgflip.com/get_memes')
        res_data = response.json()
        all_memes = res_data['data']['memes'][:16]
        
        for m in all_memes:
            m['price'] = calculate_price(m['id'])
            
        return render_template('index.html', memes=all_memes)
    except:
        return "Connection to Meme Market failed. Try refreshing."

@app.route('/trade/<meme_id>/<name>')
def trade(meme_id, name):
    current_price = calculate_price(meme_id)
    return render_template('trade.html', meme_id=meme_id, name=name, price=current_price)

@app.route('/buy/<meme_id>/<name>/<float:price>')
def buy(meme_id, name, price):
    if session['balance'] >= price:
        session['balance'] -= price
        user_assets = session.get('portfolio', {})
        user_assets[name] = user_assets.get(name, 0) + 1
        session['portfolio'] = user_assets
        flash(f'Successfully invested in {name}!')
    else:
        flash('Insufficient capital. Get more stonks.')
    return redirect(url_for('portfolio'))

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html', 
                           balance=round(session.get('balance', 0), 2), 
                           assets=session.get('portfolio', {}))

if __name__ == '__main__':
    app.run(debug=True)