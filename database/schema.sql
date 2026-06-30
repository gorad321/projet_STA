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
    conditions_admission TEXT,
    debouches           TEXT,
    date_creation       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (departement_id) REFERENCES departement(id_departement)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. MODULE_PROGRAMME (programme détaillé par semestre)

CREATE TABLE module_programme (
    id_module           INT AUTO_INCREMENT PRIMARY KEY,
    formation_id         INT NOT NULL,
    semestre             VARCHAR(50) NOT NULL,       
    nom_module           VARCHAR(150) NOT NULL,
    FOREIGN KEY (formation_id) REFERENCES formation(id_formation)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. ENSEIGNANT

CREATE TABLE enseignant (
    id_enseignant        INT AUTO_INCREMENT PRIMARY KEY,
    departement_id       INT,
    nom                  VARCHAR(150) NOT NULL,
    grade                VARCHAR(100),                -- ex: Maître de conférences
    email                VARCHAR(150),
    domaines_recherche   TEXT,
    photo                VARCHAR(255),                -- chemin du fichier image
    FOREIGN KEY (departement_id) REFERENCES departement(id_departement)
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- 5. ACTUALITE

CREATE TABLE actualite (
    id_actualite        INT AUTO_INCREMENT PRIMARY KEY,
    titre                VARCHAR(200) NOT NULL,
    date_publication     DATE NOT NULL,
    description          TEXT,
    photo                VARCHAR(255),                -- chemin du fichier image
    type                 VARCHAR(50),                 -- séminaire, conférence, soutenance, appel, résultat
    date_creation        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 6. ACTIVITE

CREATE TABLE activite (
    id_activite          INT AUTO_INCREMENT PRIMARY KEY,
    titre                VARCHAR(200) NOT NULL,
    date_activite        DATE NOT NULL,
    lieu                 VARCHAR(150),
    organisateur         VARCHAR(150),
    description          TEXT,
    date_creation        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 7. ALBUM (galerie photo organisée par albums)
CREATE TABLE album (
    id_album             INT AUTO_INCREMENT PRIMARY KEY,
    titre                VARCHAR(150) NOT NULL,
    description           TEXT,
    date_album            DATE,
    date_creation         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 8. PHOTO (liée soit à une activité, soit à un album)

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

-- 9. ADMIN (gestion des accès — mot de passe )

CREATE TABLE admin (
    id_admin             INT AUTO_INCREMENT PRIMARY KEY,
    nom_utilisateur       VARCHAR(100) NOT NULL UNIQUE,
    mot_de_passe          VARCHAR(255) NOT NULL,       -- sera hashé (bcrypt) en Phase 4
    date_creation          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- INDEX utiles

CREATE INDEX idx_formation_departement ON formation(departement_id);
CREATE INDEX idx_module_formation ON module_programme(formation_id);
CREATE INDEX idx_enseignant_departement ON enseignant(departement_id);
CREATE INDEX idx_photo_activite ON photo(activite_id);
CREATE INDEX idx_photo_album ON photo(album_id);
CREATE INDEX idx_actualite_date ON actualite(date_publication);
CREATE INDEX idx_activite_date ON activite(date_activite);
