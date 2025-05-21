from flask import Flask, render_template, request, redirect, url_for, flash
import os
from clustering import segment_customers

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            return redirect(url_for('analyze', filename=file.filename))
    return render_template('index.html')

@app.route('/analyze')
def analyze():
    filename = request.args.get('filename')
    if not filename:
        flash('Archivo no especificado para análisis.')
        return redirect(url_for('index'))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        flash('Archivo no encontrado.')
        return redirect(url_for('index'))

    df, graph_html, descriptions = segment_customers(filepath)

    return render_template('result.html', graph_html=graph_html, descriptions=descriptions)

if __name__ == '__main__':
    app.run(debug=True)
