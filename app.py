
import requests, os, clipboard
from bs4 import BeautifulSoup as bs
from werkzeug.utils import secure_filename
from encrypt import encryptpdf as enc, imgtopdf as imf
from flask import Flask, flash, request, redirect, render_template, send_from_directory

UPLOAD_FOLDER = 'uploads'
try:
    import os
    os.mkdir('uploads')
except:
    pass

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/share")
def share():
    return render_template("share.html")

@app.route("/morse")
def morse():
    return render_template("morse.html")

@app.route('/converted_morse', methods=['POST'])
def convert_morse():

    decrypted = [' ', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', '5', '6',
                 '7', '8', '9', '0', ',', '?', '(', ')', '!']

    encrypted = ['/', '.-', '-...', '-.-.', '-..', '.', '..-.', '--.',
                 '....', '..', '.---', '-.-', '.-..', '--', '-.', '---',
                 '.--.', '--.-', '.-.', '...', '-', '..-', '...-', '.--',
                 '-..-', '-.--', '--..', '.----', '..---', '...--', '....-',
                 '.....', '-....', '--...', '---..', '----.', '-----', '--..--',
                 '..--..', '-.--.', '-.--.-', '-.-.--']

    morse_enc = dict(zip(decrypted, encrypted))
    morse_dec = dict([(encrypted, decrypted) for decrypted,
                      encrypted in morse_enc.items()])

    test = request.form['morse']
    # test = input('Enter Morse Code or, Simple Text (or, just Press Ok/Enter for default entry) : ')
    if test == '':
        test = '- .... . / -.. ..- .-. .- - .. --- -. / --- ..-. / .- / -.. .- ... .... / .. ... / - .... .-. . . / - .. -- . ... / - .... . / -.. ..- .-. .- - .. --- -. / --- ..-. / .- / -.. --- - --..-- / . .- -.-. .... / -.. --- - / --- .-. / -.. .- ... .... / .-- .. - .... .. -. / .- / -.-. .... .- .-. .- -.-. - . .-. / .. ... / ..-. --- .-.. .-.. --- .-- . -.. / -... -.-- / .--. . .-. .. --- -.. / --- ..-. / ... .. --. -. .- .-.. / .- -... ... . -. -.-. . --..-- / -.-. .- .-.. .-.. . -.. / .- / ... .--. .- -.-. . --..-- / . --.- ..- .- .-.. / - --- / - .... . / -.. --- - / -.. ..- .-. .- - .. --- -. --..-- / - .... . / .-.. . - - . .-. ... / --- ..-. / .- / .-- --- .-. -.. / .- .-. . / ... . .--. .- .-. .- - . -.. / -... -.-- / .- / ... .--. .- -.-. . / --- ..-. / -.. ..- .-. .- - .. --- -. / . --.- ..- .- .-.. / - --- / - .... .-. . . / -.. --- - ... --..-- / .- -. -.. / - .... . / .-- --- .-. -.. ... / .- .-. . / ... . .--. .- .-. .- - . -.. / -... -.-- / .- / ... .--. .- -.-. . / . --.- ..- .- .-.. / - --- / ... . ...- . -. / -.. --- - ... /'

    test = test.replace("_", "-").upper()
    test_list = test.split(' ')

    decrypt = []
    def convert(j):
        for i in j:
            try:
              decrypt.append((morse_enc[i]))
            except:
              try:
                decrypt.append((morse_dec[i]))
              except:
                pass

    if not any(ele in encrypted for ele in test_list):
        box=[]
        for i in test_list:
            box.append(i+' ')
        test_list = box

        for j in test_list:
            convert(j)
            text = ' '.join(decrypt)
    else:
        convert(test_list)
        text = ''.join(decrypt)

    clipboard.copy(text)
    flash(f'Note: Output of {test} is copied in clipboard !!!')
    return render_template('morse.html', text = text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the files part
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')
        password = request.form['unique']

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                loc = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(loc)

                try:
                    loc = enc(loc, password)
                except:
                    try:
                        loc = enc(imf(loc), password)
                    except:
                        pass
        # return render_template('complete.html', aloc=aloc)

        clipboard.copy(loc)
        flash(f'{loc} is copied in clipboard !!!')
        return redirect(f'/{loc}')

# def redirect(loc):
#     return redirect(f'/{loc}')

@app.route('/uploads/<filename>')
def send_image(filename):
    return send_from_directory("uploads", filename)

# @app.route('/gallery')
# def get_gallery():
#     image_names = os.listdir('./uploads')
#     return render_template("gallery.html", image_names=image_names)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/skills')
def skills():
    return render_template('skills.html')

@app.route('/news')
def news():

    link = 'https://inshorts.com/en/read'
    req = requests.get(link)

    soup = bs(req.content, 'html5lib')
    box = soup.findAll('div', attrs = {'class':'news-card z-depth-1'})

    ha,ia,ba,la = [],[],[],[]
    for i in range(len(box)):
        h = box[i].find('span', attrs = {'itemprop':'headline'}).text

        m = box[i].find('div', attrs = {'class':'news-card-image'})
        m = m['style'].split("'")[1]

        b = box[i].find('div', attrs = {'itemprop':'articleBody'}).text
        l='link not found'

        try:
            l = box[i].find('a', attrs = {'class':'source'})['href']
        except:
            pass

        ha.append(h)
        ia.append(m)
        ba.append(b)
        la.append(l)
    return render_template('news.html', ha=ha, ia=ia, ba=ba, la=la, len = len(ha))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
