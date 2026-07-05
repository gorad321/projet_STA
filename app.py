import os
from datetime import datetime
from itertools import groupby

import pymysql
import pymysql.cursors
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

# Configuration
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')


def group_programme(modules):
    """Regroupe des lignes module_programme par semestre puis par unité d'enseignement,
    en conservant l'ordre d'insertion (ordre officiel de la maquette)."""
    programme = []
    for semestre, sem_rows in groupby(modules, key=lambda m: m['semestre']):
        ue_groups = []
        for ue, ue_rows in groupby(sem_rows, key=lambda m: m['unite_enseignement']):
            ue_rows = list(ue_rows)
            ue_groups.append({
                'nom': ue,
                'credits': ue_rows[0]['credits'],
                'elements': ue_rows,
            })
        programme.append({'semestre': semestre, 'ue_groups': ue_groups})
    return programme


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
    directeur = db_fetch_one(
        "SELECT * FROM enseignant WHERE nom = 'Dr. Alioune COULIBALY'"
    )
    return render_template('index.html', actualites=actualites, directeur=directeur)


@app.route('/departements')
def departements():
    departements = db_fetch_all("""
        SELECT d.*, e.id_enseignant AS responsable_id
        FROM departement d
        LEFT JOIN enseignant e ON e.nom = d.responsable
        ORDER BY d.nom
    """)
    return render_template('departements.html', departements=departements)


@app.route('/formations')
def formations():
    return render_template('formations.html')


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
        WHERE formation_id = %s AND specialisation_id IS NULL
        ORDER BY semestre, id_module
    """, (id_formation,))
    specialisations = db_fetch_all("""
        SELECT s.*, d.nom AS nom_departement_specialisation
        FROM specialisation s
        LEFT JOIN departement d ON s.departement_id = d.id_departement
        WHERE s.formation_id = %s
        ORDER BY s.id_specialisation
    """, (id_formation,))
    modules_specialisation = db_fetch_all("""
        SELECT * FROM module_programme
        WHERE formation_id = %s AND specialisation_id IS NOT NULL
        ORDER BY specialisation_id, semestre, id_module
    """, (id_formation,))
    programme = group_programme(modules)
    programme_specialisation = {
        spe_id: group_programme(list(spe_rows))
        for spe_id, spe_rows in groupby(modules_specialisation, key=lambda m: m['specialisation_id'])
    }
    return render_template('formation_detail.html',
                           formation=formation,
                           specialisations=specialisations,
                           programme=programme,
                           programme_specialisation=programme_specialisation)


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
        """SELECT a.*,
                  (SELECT p.chemin FROM photo p
                   WHERE p.activite_id = a.id_activite
                   ORDER BY p.date_ajout ASC LIMIT 1) AS photo
           FROM activite a
           ORDER BY a.date_activite DESC"""
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


@app.route('/enseignants/<int:id_enseignant>')
def enseignant_detail(id_enseignant):
    enseignant = db_fetch_one("""
        SELECT e.*, d.nom AS nom_departement
        FROM enseignant e
        LEFT JOIN departement d ON e.departement_id = d.id_departement
        WHERE e.id_enseignant = %s
    """, (id_enseignant,))
    if not enseignant:
        flash('Enseignant introuvable.', 'error')
        return redirect(url_for('enseignants'))
    return render_template('enseignant_detail.html', enseignant=enseignant)


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