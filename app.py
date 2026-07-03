import os
from datetime import datetime

import pymysql
import pymysql.cursors
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

# Configuration
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')


# Connexion base de données
def get_db():
    """Ouvre une connexion MySQL et la retourne."""
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'ufr_sta_db'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


# Fonctions pymysql réutilisables
def db_fetch_all(query, params=None):
    """Exécute une requête SELECT et retourne toutes les lignes."""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    finally:
        conn.close()


def db_fetch_one(query, params=None):
    """Exécute une requête SELECT et retourne une seule ligne."""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    finally:
        conn.close()


def db_execute(query, params=None):
    """Exécute INSERT, UPDATE ou DELETE. Retourne l'id de la dernière ligne insérée."""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


# Contexte global Jinja2 (disponible dans tous les templates)
@app.context_processor
def inject_globals():
    return {'now': datetime.now()}


# Route de test de la connexion DB
@app.route('/test-db')
def test_db():
    try:
        conn = get_db()
        conn.close()
        return 'Connexion à la base de données OK !', 200
    except Exception as e:
        return f'Erreur de connexion : {e}', 500


# Routes publiques
@app.route('/')
def index():
    # Dernières actualités (5 max) pour l'accueil
    actualites = db_fetch_all(
        "SELECT * FROM actualite ORDER BY date_publication DESC LIMIT 5"
    )
    # Dernières activités (3 max) pour l'accueil
    activites = db_fetch_all(
        "SELECT * FROM activite ORDER BY date_activite DESC LIMIT 3"
    )
    # Départements (3 max) pour l'accueil
    departements = db_fetch_all(
        "SELECT * FROM departement ORDER BY nom LIMIT 3"
    )
    return render_template('index.html',
                           actualites=actualites,
                           activites=activites,
                           departements=departements)


@app.route('/departements')
def departements():
    departements = db_fetch_all("SELECT * FROM departement ORDER BY nom")
    return render_template('departements.html', departements=departements)


@app.route('/departements/<int:id_departement>')
def departement_detail(id_departement):
    departement = db_fetch_one(
        "SELECT * FROM departement WHERE id_departement = %s",
        (id_departement,)
    )
    if not departement:
        flash('Département introuvable.', 'error')
        return redirect(url_for('departements'))
    formations = db_fetch_all(
        "SELECT * FROM formation WHERE departement_id = %s ORDER BY niveau, nom",
        (id_departement,)
    )
    enseignants = db_fetch_all(
        "SELECT * FROM enseignant WHERE departement_id = %s ORDER BY nom",
        (id_departement,)
    )
    return render_template('departement_detail.html',
                           departement=departement,
                           formations=formations,
                           enseignants=enseignants)


@app.route('/formations')
def formations():
    formations = db_fetch_all("""
        SELECT f.*, d.nom AS nom_departement
        FROM formation f
        JOIN departement d ON f.departement_id = d.id_departement
        ORDER BY d.nom, f.niveau, f.nom
    """)
    return render_template('formations.html', formations=formations)


@app.route('/formations/<int:id_formation>')
def formation_detail(id_formation):
    formation = db_fetch_one("""
        SELECT f.*, d.nom AS nom_departement
        FROM formation f
        JOIN departement d ON f.departement_id = d.id_departement
        WHERE f.id_formation = %s
    """, (id_formation,))
    if not formation:
        flash('Formation introuvable.', 'error')
        return redirect(url_for('formations'))
    modules = db_fetch_all("""
        SELECT * FROM module_programme
        WHERE formation_id = %s
        ORDER BY semestre, nom_module
    """, (id_formation,))
    return render_template('formation_detail.html',
                           formation=formation,
                           modules=modules)


@app.route('/actualites')
def actualites():
    actualites = db_fetch_all(
        "SELECT * FROM actualite ORDER BY date_publication DESC"
    )
    return render_template('actualites.html', actualites=actualites)


@app.route('/actualites/<int:id_actualite>')
def actualite_detail(id_actualite):
    actualite = db_fetch_one(
        "SELECT * FROM actualite WHERE id_actualite = %s",
        (id_actualite,)
    )
    if not actualite:
        flash('Actualité introuvable.', 'error')
        return redirect(url_for('actualites'))
    return render_template('actualite_detail.html', actualite=actualite)


@app.route('/activites')
def activites():
    activites = db_fetch_all(
        "SELECT * FROM activite ORDER BY date_activite DESC"
    )
    return render_template('activites.html', activites=activites)


@app.route('/activites/<int:id_activite>')
def activite_detail(id_activite):
    activite = db_fetch_one(
        "SELECT * FROM activite WHERE id_activite = %s",
        (id_activite,)
    )
    if not activite:
        flash('Activité introuvable.', 'error')
        return redirect(url_for('activites'))
    photos = db_fetch_all(
        "SELECT * FROM photo WHERE activite_id = %s",
        (id_activite,)
    )
    return render_template('activite_detail.html',
                           activite=activite,
                           photos=photos)


@app.route('/galerie')
def galerie():
    albums = db_fetch_all(
        "SELECT * FROM album ORDER BY date_album DESC"
    )
    return render_template('galerie.html', albums=albums)


@app.route('/galerie/<int:id_album>')
def album_detail(id_album):
    album = db_fetch_one(
        "SELECT * FROM album WHERE id_album = %s",
        (id_album,)
    )
    if not album:
        flash('Album introuvable.', 'error')
        return redirect(url_for('galerie'))
    photos = db_fetch_all(
        "SELECT * FROM photo WHERE album_id = %s",
        (id_album,)
    )
    return render_template('album_detail.html', album=album, photos=photos)


@app.route('/enseignants')
def enseignants():
    enseignants = db_fetch_all("""
        SELECT e.*, d.nom AS nom_departement
        FROM enseignant e
        LEFT JOIN departement d ON e.departement_id = d.id_departement
        ORDER BY e.nom
    """)
    return render_template('enseignants.html', enseignants=enseignants)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        nom     = request.form.get('nom', '').strip()
        email   = request.form.get('email', '').strip()
        sujet   = request.form.get('sujet', '').strip()
        message = request.form.get('message', '').strip()

        if not nom or not email or not message:
            flash('Veuillez remplir tous les champs obligatoires.', 'error')
            return redirect(url_for('contact'))

        # TODO Phase 3 : envoyer l'email via Resend
        flash('Votre message a bien été envoyé. Nous vous répondrons bientôt.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')


# Lancement
if __name__ == '__main__':
    app.run(debug=True)

