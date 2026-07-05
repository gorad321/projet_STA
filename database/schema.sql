-- Création Database pour Site Web Vitrine UFR STA

CREATE DATABASE IF NOT EXISTS ufr_sta_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ufr_sta_db;

-- 1. DEPARTEMENT

CREATE TABLE departement (
    id_departement      INT AUTO_INCREMENT PRIMARY KEY,
    nom                 VARCHAR(150) NOT NULL,
    description         TEXT,
    responsable         VARCHAR(150),
    contact             VARCHAR(150),
    date_creation       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. FORMATION

CREATE TABLE formation (
    id_formation        INT AUTO_INCREMENT PRIMARY KEY,
    departement_id      INT NOT NULL,
    nom                 VARCHAR(150) NOT NULL,
    niveau              VARCHAR(50) NOT NULL,
    duree               VARCHAR(50),
    objectif            TEXT,
    conditions_admission TEXT,
    debouches           TEXT,
    date_creation       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (departement_id) REFERENCES departement(id_departement)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. SPECIALISATION (filières au sein d'une formation, ex: MPI en S5)

CREATE TABLE specialisation (
    id_specialisation    INT AUTO_INCREMENT PRIMARY KEY,
    formation_id         INT NOT NULL,
    nom                  VARCHAR(150) NOT NULL,
    semestre_debut       VARCHAR(50),                 -- ex: Semestre 5
    description          TEXT,
    debouches            TEXT,
    departement_id       INT NULL,                    -- si la spécialisation migre vers un autre département
    FOREIGN KEY (formation_id) REFERENCES formation(id_formation)
        ON DELETE CASCADE,
    FOREIGN KEY (departement_id) REFERENCES departement(id_departement)
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- 4. MODULE_PROGRAMME (programme détaillé par semestre)

CREATE TABLE module_programme (
    id_module           INT AUTO_INCREMENT PRIMARY KEY,
    formation_id         INT NOT NULL,
    specialisation_id    INT NULL,                    -- NULL = tronc commun ; renseigné = programme propre à une spécialisation (S5/S6)
    semestre             VARCHAR(50) NOT NULL,
    unite_enseignement   VARCHAR(150) NOT NULL,        -- ex: "Mathématiques 1"
    nom_module           VARCHAR(150) NOT NULL,         -- élément constitutif, ex: "Analyse 1"
    vht                  INT,                           -- volume horaire total (heures)
    credits              INT,                           -- crédits de l'UE (dupliqué sur chaque élément de l'UE)
    coefficient          INT,
    FOREIGN KEY (formation_id) REFERENCES formation(id_formation)
        ON DELETE CASCADE,
    FOREIGN KEY (specialisation_id) REFERENCES specialisation(id_specialisation)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. ENSEIGNANT

CREATE TABLE enseignant (
    id_enseignant        INT AUTO_INCREMENT PRIMARY KEY,
    departement_id       INT,
    nom                  VARCHAR(150) NOT NULL,
    grade                VARCHAR(100),                -- ex: Maître de conférences, Professeur Titulaire
    fonction             VARCHAR(255),                -- rôle additionnel, ex: Vice-Recteur chargé des Affaires pédagogiques
    discipline           VARCHAR(255),                -- ex: "Nanosciences Nanotechnologie Matériaux" (utilisé dans "Enseignant-chercheur en ...")
    specialite_cames     VARCHAR(150),                -- spécialité CAMES officielle, ex: "Physique : Milieux denses et matériaux"
    email                VARCHAR(150),
    domaines_recherche   TEXT,                        -- thématiques de recherche, une par ligne
    photo                VARCHAR(255),                -- chemin du fichier image
    FOREIGN KEY (departement_id) REFERENCES departement(id_departement)
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- 6. ACTUALITE

CREATE TABLE actualite (
    id_actualite        INT AUTO_INCREMENT PRIMARY KEY,
    titre                VARCHAR(200) NOT NULL,
    date_publication     DATE NOT NULL,
    description          TEXT,
    photo                VARCHAR(255),                -- chemin du fichier image
    type                 VARCHAR(50),                 -- séminaire, conférence, soutenance, appel, résultat
    date_creation        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 7. ACTIVITE

CREATE TABLE activite (
    id_activite          INT AUTO_INCREMENT PRIMARY KEY,
    titre                VARCHAR(200) NOT NULL,
    date_activite        DATE NOT NULL,
    lieu                 VARCHAR(150),
    organisateur         VARCHAR(150),
    description          TEXT,
    photo                VARCHAR(255),                -- chemin du fichier image
    date_creation        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 8. ALBUM (galerie photo organisée par albums)
CREATE TABLE album (
    id_album             INT AUTO_INCREMENT PRIMARY KEY,
    titre                VARCHAR(150) NOT NULL,
    description           TEXT,
    date_album            DATE,
    date_creation         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 9. PHOTO (liée soit à une activité, soit à un album)

CREATE TABLE photo (
    id_photo             INT AUTO_INCREMENT PRIMARY KEY,
    activite_id          INT NULL,
    album_id             INT NULL,
    chemin               VARCHAR(255) NOT NULL,       -- ex: images/activites/atelier_ia_1.jpg
    legende              VARCHAR(200),
    date_ajout           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activite_id) REFERENCES activite(id_activite)
        ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES album(id_album)
        ON DELETE CASCADE
    -- Règle : une photo doit être liée à activite_id OU album_id, jamais les deux,
    -- jamais aucun. Vérification faite côté Python (app.py) avant chaque
    -- insertion, car CHECK n'est pas fiable sur toutes les versions de
    -- MariaDB (XAMPP).
) ENGINE=InnoDB;

-- 10. ADMIN (gestion des accès — mot de passe )

CREATE TABLE admin (
    id_admin             INT AUTO_INCREMENT PRIMARY KEY,
    nom_utilisateur       VARCHAR(100) NOT NULL UNIQUE,
    mot_de_passe          VARCHAR(255) NOT NULL,       -- sera hashé (bcrypt) en Phase 4
    date_creation          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- INDEX utiles

CREATE INDEX idx_formation_departement ON formation(departement_id);
CREATE INDEX idx_module_formation ON module_programme(formation_id);
CREATE INDEX idx_module_specialisation ON module_programme(specialisation_id);
CREATE INDEX idx_specialisation_formation ON specialisation(formation_id);
CREATE INDEX idx_enseignant_departement ON enseignant(departement_id);
CREATE INDEX idx_photo_activite ON photo(activite_id);
CREATE INDEX idx_photo_album ON photo(album_id);
CREATE INDEX idx_actualite_date ON actualite(date_publication);
CREATE INDEX idx_activite_date ON activite(date_activite);