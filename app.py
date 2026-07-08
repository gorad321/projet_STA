import os
import secrets
import uuid
from datetime import datetime
from functools import wraps
from itertools import groupby

import bcrypt
import pymysql
import pymysql.cursors
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

# Configuration
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images', 'uploads')


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


def select_photos_presentation(photos):
    """Détermine les photos principale/secondaire d'un album pour la page de présentation :
    utilise le choix explicite (ordre_affichage) si présent, sinon les 2 premières photos."""
    principale = next((p for p in photos if p.get('ordre_affichage') == 1), None)
    secondaire = next((p for p in photos if p.get('ordre_affichage') == 2), None)
    restantes = [p for p in photos if p is not principale and p is not secondaire]
    if not principale and restantes:
        principale = restantes.pop(0)
    if not secondaire and restantes:
        secondaire = restantes.pop(0)
    return principale, secondaire


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


# =====================================================
# ADMINISTRATION : authentification, CSRF, upload photos
# =====================================================
@app.before_request
def ensure_csrf_token():
    """Génère un jeton CSRF par session s'il n'existe pas déjà."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)


@app.context_processor
def inject_csrf_token():
    return {'csrf_token': session.get('csrf_token', '')}


def check_csrf():
    """Vérifie le jeton CSRF soumis dans un formulaire POST admin."""
    token = request.form.get('csrf_token', '')
    if not token or not secrets.compare_digest(token, session.get('csrf_token', '')):
        abort(400)


def admin_required(f):
    """Protège une route admin : redirige vers la connexion si non authentifié,
    et vérifie le jeton CSRF sur toute requête POST."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('admin_id'):
            flash('Veuillez vous connecter.', 'error')
            return redirect(url_for('admin_login'))
        if request.method == 'POST':
            check_csrf()
        return f(*args, **kwargs)
    return wrapper


def save_photo(file_storage, subfolder):
    """Sauvegarde une image uploadée dans static/images/uploads/<subfolder>/
    et retourne son chemin relatif (ou None si aucun fichier valide fourni)."""
    if not file_storage or not file_storage.filename:
        return None
    if '.' not in file_storage.filename:
        return None
    ext = file_storage.filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_PHOTO_EXTENSIONS:
        return None
    filename = secure_filename(f'{uuid.uuid4().hex}.{ext}')
    folder = os.path.join(UPLOAD_FOLDER, subfolder)
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, filename))
    return f'images/uploads/{subfolder}/{filename}'


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_id'):
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        nom_utilisateur = request.form.get('nom_utilisateur', '').strip()
        mot_de_passe = request.form.get('mot_de_passe', '')
        admin = db_fetch_one(
            "SELECT * FROM admin WHERE nom_utilisateur = %s", (nom_utilisateur,)
        )
        if admin and bcrypt.checkpw(mot_de_passe.encode('utf-8'), admin['mot_de_passe'].encode('utf-8')):
            session['admin_id'] = admin['id_admin']
            session['admin_nom'] = admin['nom_utilisateur']
            return redirect(url_for('admin_dashboard'))
        flash('Identifiants incorrects.', 'error')
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Vous avez été déconnecté.', 'success')
    return redirect(url_for('admin_login'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    counts = {
        'departements': db_fetch_one("SELECT COUNT(*) AS c FROM departement")['c'],
        'formations': db_fetch_one("SELECT COUNT(*) AS c FROM formation")['c'],
        'enseignants': db_fetch_one("SELECT COUNT(*) AS c FROM enseignant")['c'],
        'actualites': db_fetch_one("SELECT COUNT(*) AS c FROM actualite")['c'],
        'activites': db_fetch_one("SELECT COUNT(*) AS c FROM activite")['c'],
        'albums': db_fetch_one("SELECT COUNT(*) AS c FROM album")['c'],
    }
    return render_template('admin/dashboard.html', counts=counts)


# --- Départements ---
@app.route('/admin/departements')
@admin_required
def admin_departements():
    departements = db_fetch_all("SELECT * FROM departement ORDER BY nom")
    return render_template('admin/departements/list.html', departements=departements)


@app.route('/admin/departements/nouveau', methods=['GET', 'POST'])
@admin_required
def admin_departement_nouveau():
    if request.method == 'POST':
        photo = save_photo(request.files.get('photo'), 'departements')
        db_execute("""
            INSERT INTO departement (nom, description, responsable, contact, photo)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            request.form.get('nom', '').strip(),
            request.form.get('description', '').strip() or None,
            request.form.get('responsable', '').strip() or None,
            request.form.get('contact', '').strip() or None,
            photo,
        ))
        flash('Département créé.', 'success')
        return redirect(url_for('admin_departements'))
    return render_template('admin/departements/form.html', item=None)


@app.route('/admin/departements/<int:id_departement>/modifier', methods=['GET', 'POST'])
@admin_required
def admin_departement_modifier(id_departement):
    item = db_fetch_one("SELECT * FROM departement WHERE id_departement = %s", (id_departement,))
    if not item:
        flash('Département introuvable.', 'error')
        return redirect(url_for('admin_departements'))
    if request.method == 'POST':
        photo = save_photo(request.files.get('photo'), 'departements') or item['photo']
        db_execute("""
            UPDATE departement SET nom = %s, description = %s, responsable = %s, contact = %s, photo = %s
            WHERE id_departement = %s
        """, (
            request.form.get('nom', '').strip(),
            request.form.get('description', '').strip() or None,
            request.form.get('responsable', '').strip() or None,
            request.form.get('contact', '').strip() or None,
            photo,
            id_departement,
        ))
        flash('Département modifié.', 'success')
        return redirect(url_for('admin_departements'))
    return render_template('admin/departements/form.html', item=item)


@app.route('/admin/departements/<int:id_departement>/supprimer', methods=['POST'])
@admin_required
def admin_departement_supprimer(id_departement):
    db_execute("DELETE FROM departement WHERE id_departement = %s", (id_departement,))
    flash('Département supprimé.', 'success')
    return redirect(url_for('admin_departements'))


# --- Enseignants ---
@app.route('/admin/enseignants')
@admin_required
def admin_enseignants():
    enseignants = db_fetch_all("""
        SELECT e.*, d.nom AS nom_departement
        FROM enseignant e
        LEFT JOIN departement d ON e.departement_id = d.id_departement
        ORDER BY e.nom
    """)
    return render_template('admin/enseignants/list.html', enseignants=enseignants)


@app.route('/admin/enseignants/nouveau', methods=['GET', 'POST'])
@admin_required
def admin_enseignant_nouveau():
    departements = db_fetch_all("SELECT * FROM departement ORDER BY nom")
    if request.method == 'POST':
        photo = save_photo(request.files.get('photo'), 'enseignants')
        db_execute("""
            INSERT INTO enseignant
                (departement_id, nom, grade, fonction, discipline, specialite_cames, email, domaines_recherche, photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request.form.get('departement_id') or None,
            request.form.get('nom', '').strip(),
            request.form.get('grade', '').strip() or None,
            request.form.get('fonction', '').strip() or None,
            request.form.get('discipline', '').strip() or None,
            request.form.get('specialite_cames', '').strip() or None,
            request.form.get('email', '').strip() or None,
            request.form.get('domaines_recherche', '').strip() or None,
            photo,
        ))
        flash('Enseignant créé.', 'success')
        return redirect(url_for('admin_enseignants'))
    return render_template('admin/enseignants/form.html', item=None, departements=departements)


@app.route('/admin/enseignants/<int:id_enseignant>/modifier', methods=['GET', 'POST'])
@admin_required
def admin_enseignant_modifier(id_enseignant):
    item = db_fetch_one("SELECT * FROM enseignant WHERE id_enseignant = %s", (id_enseignant,))
    if not item:
        flash('Enseignant introuvable.', 'error')
        return redirect(url_for('admin_enseignants'))
    departements = db_fetch_all("SELECT * FROM departement ORDER BY nom")
    if request.method == 'POST':
        photo = save_photo(request.files.get('photo'), 'enseignants') or item['photo']
        db_execute("""
            UPDATE enseignant SET
                departement_id = %s, nom = %s, grade = %s, fonction = %s, discipline = %s,
                specialite_cames = %s, email = %s, domaines_recherche = %s, photo = %s
            WHERE id_enseignant = %s
        """, (
            request.form.get('departement_id') or None,
            request.form.get('nom', '').strip(),
            request.form.get('grade', '').strip() or None,
            request.form.get('fonction', '').strip() or None,
            request.form.get('discipline', '').strip() or None,
            request.form.get('specialite_cames', '').strip() or None,
            request.form.get('email', '').strip() or None,
            request.form.get('domaines_recherche', '').strip() or None,
            photo,
            id_enseignant,
        ))
        flash('Enseignant modifié.', 'success')
        return redirect(url_for('admin_enseignants'))
    return render_template('admin/enseignants/form.html', item=item, departements=departements)


@app.route('/admin/enseignants/<int:id_enseignant>/supprimer', methods=['POST'])
@admin_required
def admin_enseignant_supprimer(id_enseignant):
    db_execute("DELETE FROM enseignant WHERE id_enseignant = %s", (id_enseignant,))
    flash('Enseignant supprimé.', 'success')
    return redirect(url_for('admin_enseignants'))


# --- Actualités ---
@app.route('/admin/actualites')
@admin_required
def admin_actualites():
    actualites = db_fetch_all("SELECT * FROM actualite ORDER BY date_publication DESC")
    return render_template('admin/actualites/list.html', actualites=actualites)


@app.route('/admin/actualites/nouveau', methods=['GET', 'POST'])
@admin_required
def admin_actualite_nouveau():
    if request.method == 'POST':
        photo = save_photo(request.files.get('photo'), 'actualites')
        db_execute("""
            INSERT INTO actualite (titre, date_publication, description, photo, type)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            request.form.get('titre', '').strip(),
            request.form.get('date_publication') or None,
            request.form.get('description', '').strip() or None,
            photo,
            request.form.get('type', '').strip() or None,
        ))
        flash('Actualité créée.', 'success')
        return redirect(url_for('admin_actualites'))
    return render_template('admin/actualites/form.html', item=None)


@app.route('/admin/actualites/<int:id_actualite>/modifier', methods=['GET', 'POST'])
@admin_required
def admin_actualite_modifier(id_actualite):
    item = db_fetch_one("SELECT * FROM actualite WHERE id_actualite = %s", (id_actualite,))
    if not item:
        flash('Actualité introuvable.', 'error')
        return redirect(url_for('admin_actualites'))
    if request.method == 'POST':
        photo = save_photo(request.files.get('photo'), 'actualites') or item['photo']
        db_execute("""
            UPDATE actualite SET titre = %s, date_publication = %s, description = %s, photo = %s, type = %s
            WHERE id_actualite = %s
        """, (
            request.form.get('titre', '').strip(),
            request.form.get('date_publication') or None,
            request.form.get('description', '').strip() or None,
            photo,
            request.form.get('type', '').strip() or None,
            id_actualite,
        ))
        flash('Actualité modifiée.', 'success')
        return redirect(url_for('admin_actualites'))
    return render_template('admin/actualites/form.html', item=item)


@app.route('/admin/actualites/<int:id_actualite>/supprimer', methods=['POST'])
@admin_required
def admin_actualite_supprimer(id_actualite):
    db_execute("DELETE FROM actualite WHERE id_actualite = %s", (id_actualite,))
    flash('Actualité supprimée.', 'success')
    return redirect(url_for('admin_actualites'))


# --- Activités ---
@app.route('/admin/activites')
@admin_required
def admin_activites():
    activites = db_fetch_all("SELECT * FROM activite ORDER BY date_activite DESC")
    return render_template('admin/activites/list.html', activites=activites)


@app.route('/admin/activites/nouveau', methods=['GET', 'POST'])
@admin_required
def admin_activite_nouveau():
    if request.method == 'POST':
        photo = save_photo(request.files.get('photo'), 'activites')
        db_execute("""
            INSERT INTO activite (titre, date_activite, lieu, organisateur, description, photo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            request.form.get('titre', '').strip(),
            request.form.get('date_activite') or None,
            request.form.get('lieu', '').strip() or None,
            request.form.get('organisateur', '').strip() or None,
            request.form.get('description', '').strip() or None,
            photo,
        ))
        flash('Activité créée.', 'success')
        return redirect(url_for('admin_activites'))
    return render_template('admin/activites/form.html', item=None)


@app.route('/admin/activites/<int:id_activite>/modifier', methods=['GET', 'POST'])
@admin_required
def admin_activite_modifier(id_activite):
    item = db_fetch_one("SELECT * FROM activite WHERE id_activite = %s", (id_activite,))
    if not item:
        flash('Activité introuvable.', 'error')
        return redirect(url_for('admin_activites'))
    if request.method == 'POST':
        photo = save_photo(request.files.get('photo'), 'activites') or item['photo']
        db_execute("""
            UPDATE activite SET titre = %s, date_activite = %s, lieu = %s, organisateur = %s,
                description = %s, photo = %s
            WHERE id_activite = %s
        """, (
            request.form.get('titre', '').strip(),
            request.form.get('date_activite') or None,
            request.form.get('lieu', '').strip() or None,
            request.form.get('organisateur', '').strip() or None,
            request.form.get('description', '').strip() or None,
            photo,
            id_activite,
        ))
        flash('Activité modifiée.', 'success')
        return redirect(url_for('admin_activites'))
    return render_template('admin/activites/form.html', item=item)


@app.route('/admin/activites/<int:id_activite>/supprimer', methods=['POST'])
@admin_required
def admin_activite_supprimer(id_activite):
    db_execute("DELETE FROM activite WHERE id_activite = %s", (id_activite,))
    flash('Activité supprimée.', 'success')
    return redirect(url_for('admin_activites'))


# --- Formations ---
@app.route('/admin/formations')
@admin_required
def admin_formations():
    formations = db_fetch_all("""
        SELECT f.*, d.nom AS nom_departement
        FROM formation f
        JOIN departement d ON f.departement_id = d.id_departement
        ORDER BY f.nom
    """)
    return render_template('admin/formations/list.html', formations=formations)


@app.route('/admin/formations/nouveau', methods=['GET', 'POST'])
@admin_required
def admin_formation_nouveau():
    departements = db_fetch_all("SELECT * FROM departement ORDER BY nom")
    if request.method == 'POST':
        photo = save_photo(request.files.get('photo'), 'formations')
        db_execute("""
            INSERT INTO formation (departement_id, nom, niveau, duree, objectif, conditions_admission, debouches, photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request.form.get('departement_id'),
            request.form.get('nom', '').strip(),
            request.form.get('niveau', '').strip(),
            request.form.get('duree', '').strip() or None,
            request.form.get('objectif', '').strip() or None,
            request.form.get('conditions_admission', '').strip() or None,
            request.form.get('debouches', '').strip() or None,
            photo,
        ))
        flash('Formation créée.', 'success')
        return redirect(url_for('admin_formations'))
    return render_template('admin/formations/form.html', item=None, departements=departements)


@app.route('/admin/formations/<int:id_formation>/modifier', methods=['GET', 'POST'])
@admin_required
def admin_formation_modifier(id_formation):
    item = db_fetch_one("SELECT * FROM formation WHERE id_formation = %s", (id_formation,))
    if not item:
        flash('Formation introuvable.', 'error')
        return redirect(url_for('admin_formations'))
    departements = db_fetch_all("SELECT * FROM departement ORDER BY nom")
    if request.method == 'POST':
        photo = save_photo(request.files.get('photo'), 'formations') or item['photo']
        db_execute("""
            UPDATE formation SET departement_id = %s, nom = %s, niveau = %s, duree = %s,
                objectif = %s, conditions_admission = %s, debouches = %s, photo = %s
            WHERE id_formation = %s
        """, (
            request.form.get('departement_id'),
            request.form.get('nom', '').strip(),
            request.form.get('niveau', '').strip(),
            request.form.get('duree', '').strip() or None,
            request.form.get('objectif', '').strip() or None,
            request.form.get('conditions_admission', '').strip() or None,
            request.form.get('debouches', '').strip() or None,
            photo,
            id_formation,
        ))
        flash('Formation modifiée.', 'success')
        return redirect(url_for('admin_formations'))
    return render_template('admin/formations/form.html', item=item, departements=departements)


@app.route('/admin/formations/<int:id_formation>/supprimer', methods=['POST'])
@admin_required
def admin_formation_supprimer(id_formation):
    db_execute("DELETE FROM formation WHERE id_formation = %s", (id_formation,))
    flash('Formation supprimée.', 'success')
    return redirect(url_for('admin_formations'))


# --- Spécialisations (imbriquées dans une formation) ---
@app.route('/admin/formations/<int:id_formation>/specialisations', methods=['GET', 'POST'])
@admin_required
def admin_specialisations(id_formation):
    formation = db_fetch_one("SELECT * FROM formation WHERE id_formation = %s", (id_formation,))
    if not formation:
        flash('Formation introuvable.', 'error')
        return redirect(url_for('admin_formations'))
    if request.method == 'POST':
        db_execute("""
            INSERT INTO specialisation (formation_id, nom, semestre_debut, description, debouches, departement_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            id_formation,
            request.form.get('nom', '').strip(),
            request.form.get('semestre_debut', '').strip() or None,
            request.form.get('description', '').strip() or None,
            request.form.get('debouches', '').strip() or None,
            request.form.get('departement_id') or None,
        ))
        flash('Spécialisation créée.', 'success')
        return redirect(url_for('admin_specialisations', id_formation=id_formation))
    specialisations = db_fetch_all(
        "SELECT * FROM specialisation WHERE formation_id = %s ORDER BY id_specialisation", (id_formation,)
    )
    departements = db_fetch_all("SELECT * FROM departement ORDER BY nom")
    return render_template('admin/formations/specialisations.html',
                           formation=formation, specialisations=specialisations, departements=departements)


@app.route('/admin/formations/<int:id_formation>/specialisations/<int:id_specialisation>/modifier', methods=['GET', 'POST'])
@admin_required
def admin_specialisation_modifier(id_formation, id_specialisation):
    formation = db_fetch_one("SELECT * FROM formation WHERE id_formation = %s", (id_formation,))
    item = db_fetch_one("SELECT * FROM specialisation WHERE id_specialisation = %s", (id_specialisation,))
    if not formation or not item:
        flash('Introuvable.', 'error')
        return redirect(url_for('admin_formations'))
    departements = db_fetch_all("SELECT * FROM departement ORDER BY nom")
    if request.method == 'POST':
        db_execute("""
            UPDATE specialisation SET nom = %s, semestre_debut = %s, description = %s,
                debouches = %s, departement_id = %s
            WHERE id_specialisation = %s
        """, (
            request.form.get('nom', '').strip(),
            request.form.get('semestre_debut', '').strip() or None,
            request.form.get('description', '').strip() or None,
            request.form.get('debouches', '').strip() or None,
            request.form.get('departement_id') or None,
            id_specialisation,
        ))
        flash('Spécialisation modifiée.', 'success')
        return redirect(url_for('admin_specialisations', id_formation=id_formation))
    return render_template('admin/formations/specialisation_form.html',
                           formation=formation, item=item, departements=departements)


@app.route('/admin/formations/<int:id_formation>/specialisations/<int:id_specialisation>/supprimer', methods=['POST'])
@admin_required
def admin_specialisation_supprimer(id_formation, id_specialisation):
    db_execute("DELETE FROM specialisation WHERE id_specialisation = %s", (id_specialisation,))
    flash('Spécialisation supprimée.', 'success')
    return redirect(url_for('admin_specialisations', id_formation=id_formation))


# --- Programme (modules, imbriqué dans une formation) ---
@app.route('/admin/formations/<int:id_formation>/programme', methods=['GET', 'POST'])
@admin_required
def admin_programme(id_formation):
    formation = db_fetch_one("SELECT * FROM formation WHERE id_formation = %s", (id_formation,))
    if not formation:
        flash('Formation introuvable.', 'error')
        return redirect(url_for('admin_formations'))
    if request.method == 'POST':
        db_execute("""
            INSERT INTO module_programme
                (formation_id, specialisation_id, semestre, unite_enseignement, nom_module, vht, credits, coefficient)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            id_formation,
            request.form.get('specialisation_id') or None,
            request.form.get('semestre', '').strip(),
            request.form.get('unite_enseignement', '').strip(),
            request.form.get('nom_module', '').strip(),
            request.form.get('vht') or None,
            request.form.get('credits') or None,
            request.form.get('coefficient') or None,
        ))
        flash('Module ajouté.', 'success')
        return redirect(url_for('admin_programme', id_formation=id_formation))
    modules = db_fetch_all("""
        SELECT m.*, s.nom AS nom_specialisation
        FROM module_programme m
        LEFT JOIN specialisation s ON m.specialisation_id = s.id_specialisation
        WHERE m.formation_id = %s
        ORDER BY m.semestre, m.id_module
    """, (id_formation,))
    specialisations = db_fetch_all(
        "SELECT * FROM specialisation WHERE formation_id = %s ORDER BY id_specialisation", (id_formation,)
    )
    return render_template('admin/formations/programme.html',
                           formation=formation, modules=modules, specialisations=specialisations)


@app.route('/admin/formations/<int:id_formation>/programme/<int:id_module>/modifier', methods=['GET', 'POST'])
@admin_required
def admin_module_modifier(id_formation, id_module):
    formation = db_fetch_one("SELECT * FROM formation WHERE id_formation = %s", (id_formation,))
    item = db_fetch_one("SELECT * FROM module_programme WHERE id_module = %s", (id_module,))
    if not formation or not item:
        flash('Introuvable.', 'error')
        return redirect(url_for('admin_formations'))
    specialisations = db_fetch_all(
        "SELECT * FROM specialisation WHERE formation_id = %s ORDER BY id_specialisation", (id_formation,)
    )
    if request.method == 'POST':
        db_execute("""
            UPDATE module_programme SET specialisation_id = %s, semestre = %s, unite_enseignement = %s,
                nom_module = %s, vht = %s, credits = %s, coefficient = %s
            WHERE id_module = %s
        """, (
            request.form.get('specialisation_id') or None,
            request.form.get('semestre', '').strip(),
            request.form.get('unite_enseignement', '').strip(),
            request.form.get('nom_module', '').strip(),
            request.form.get('vht') or None,
            request.form.get('credits') or None,
            request.form.get('coefficient') or None,
            id_module,
        ))
        flash('Module modifié.', 'success')
        return redirect(url_for('admin_programme', id_formation=id_formation))
    return render_template('admin/formations/module_form.html',
                           formation=formation, item=item, specialisations=specialisations)


@app.route('/admin/formations/<int:id_formation>/programme/<int:id_module>/supprimer', methods=['POST'])
@admin_required
def admin_module_supprimer(id_formation, id_module):
    db_execute("DELETE FROM module_programme WHERE id_module = %s", (id_module,))
    flash('Module supprimé.', 'success')
    return redirect(url_for('admin_programme', id_formation=id_formation))


# --- Galerie (albums) ---
@app.route('/admin/galerie')
@admin_required
def admin_galerie():
    albums = db_fetch_all("""
        SELECT a.*, COUNT(p.id_photo) AS nb_photos
        FROM album a
        LEFT JOIN photo p ON p.album_id = a.id_album
        GROUP BY a.id_album
        ORDER BY a.date_album DESC
    """)
    return render_template('admin/galerie/list.html', albums=albums)


@app.route('/admin/galerie/nouveau', methods=['GET', 'POST'])
@admin_required
def admin_album_nouveau():
    if request.method == 'POST':
        id_album = db_execute("""
            INSERT INTO album (titre, description, date_album) VALUES (%s, %s, %s)
        """, (
            request.form.get('titre', '').strip(),
            request.form.get('description', '').strip() or None,
            request.form.get('date_album') or None,
        ))
        flash('Album créé. Ajoutez maintenant des photos.', 'success')
        return redirect(url_for('admin_album_photos', id_album=id_album))
    return render_template('admin/galerie/form.html', item=None)


@app.route('/admin/galerie/<int:id_album>/modifier', methods=['GET', 'POST'])
@admin_required
def admin_album_modifier(id_album):
    item = db_fetch_one("SELECT * FROM album WHERE id_album = %s", (id_album,))
    if not item:
        flash('Album introuvable.', 'error')
        return redirect(url_for('admin_galerie'))
    if request.method == 'POST':
        db_execute("""
            UPDATE album SET titre = %s, description = %s, date_album = %s WHERE id_album = %s
        """, (
            request.form.get('titre', '').strip(),
            request.form.get('description', '').strip() or None,
            request.form.get('date_album') or None,
            id_album,
        ))
        flash('Album modifié.', 'success')
        return redirect(url_for('admin_galerie'))
    return render_template('admin/galerie/form.html', item=item)


@app.route('/admin/galerie/<int:id_album>/supprimer', methods=['POST'])
@admin_required
def admin_album_supprimer(id_album):
    db_execute("DELETE FROM album WHERE id_album = %s", (id_album,))
    flash('Album supprimé.', 'success')
    return redirect(url_for('admin_galerie'))


@app.route('/admin/galerie/<int:id_album>/photos', methods=['GET', 'POST'])
@admin_required
def admin_album_photos(id_album):
    album = db_fetch_one("SELECT * FROM album WHERE id_album = %s", (id_album,))
    if not album:
        flash('Album introuvable.', 'error')
        return redirect(url_for('admin_galerie'))
    if request.method == 'POST':
        fichiers = request.files.getlist('photos')
        legende = request.form.get('legende', '').strip() or None
        ajoutees = 0
        for fichier in fichiers:
            chemin = save_photo(fichier, 'galerie')
            if chemin:
                db_execute(
                    "INSERT INTO photo (album_id, chemin, legende) VALUES (%s, %s, %s)",
                    (id_album, chemin, legende)
                )
                ajoutees += 1
        if ajoutees:
            flash(f'{ajoutees} photo(s) ajoutée(s).', 'success')
        else:
            flash('Aucune photo valide sélectionnée.', 'error')
        return redirect(url_for('admin_album_photos', id_album=id_album))
    photos = db_fetch_all("SELECT * FROM photo WHERE album_id = %s ORDER BY id_photo", (id_album,))
    return render_template('admin/galerie/photos.html', album=album, photos=photos)


@app.route('/admin/galerie/<int:id_album>/photos/<int:id_photo>/supprimer', methods=['POST'])
@admin_required
def admin_photo_supprimer(id_album, id_photo):
    db_execute("DELETE FROM photo WHERE id_photo = %s", (id_photo,))
    flash('Photo supprimée.', 'success')
    return redirect(url_for('admin_album_photos', id_album=id_album))


@app.route('/admin/galerie/<int:id_album>/photos/<int:id_photo>/mettre-en-avant/<int:rang>', methods=['POST'])
@admin_required
def admin_photo_mettre_en_avant(id_album, id_photo, rang):
    if rang not in (1, 2):
        abort(404)
    # Retire ce rang de la photo qui l'avait actuellement dans cet album
    db_execute(
        "UPDATE photo SET ordre_affichage = NULL WHERE album_id = %s AND ordre_affichage = %s",
        (id_album, rang)
    )
    db_execute(
        "UPDATE photo SET ordre_affichage = %s WHERE id_photo = %s",
        (rang, id_photo)
    )
    flash('Photo principale mise à jour.' if rang == 1 else 'Photo secondaire mise à jour.', 'success')
    return redirect(url_for('admin_album_photos', id_album=id_album))


@app.route('/admin/galerie/<int:id_album>/photos/<int:id_photo>/retirer-mise-en-avant', methods=['POST'])
@admin_required
def admin_photo_retirer_mise_en_avant(id_album, id_photo):
    db_execute("UPDATE photo SET ordre_affichage = NULL WHERE id_photo = %s", (id_photo,))
    flash('Photo retirée de la mise en avant.', 'success')
    return redirect(url_for('admin_album_photos', id_album=id_album))


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
    formations = db_fetch_all("""
        SELECT f.*, d.nom AS nom_departement
        FROM formation f
        JOIN departement d ON f.departement_id = d.id_departement
        ORDER BY d.nom, f.nom
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
    albums = db_fetch_all("""
        SELECT a.*, p.chemin AS photo_couverture
        FROM album a
        LEFT JOIN photo p ON p.id_photo = (
            SELECT MIN(id_photo) FROM photo WHERE album_id = a.id_album
        )
        ORDER BY a.date_album DESC
    """)
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
        "SELECT * FROM photo WHERE album_id = %s ORDER BY id_photo",
        (id_album,)
    )
    photo_principale, photo_secondaire = select_photos_presentation(photos)
    return render_template('album_detail.html', album=album, photos=photos,
                           photo_principale=photo_principale, photo_secondaire=photo_secondaire)


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