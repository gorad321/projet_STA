-- =====================================================
-- UFR STA — Script complet d'initialisation de la base
-- (schema.sql + seed.sql fusionnés)
-- À importer dans phpMyAdmin / MySQL en une seule fois
-- =====================================================

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
    photo                VARCHAR(255),
    type                 VARCHAR(50),
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
    chemin               VARCHAR(255) NOT NULL,
    legende              VARCHAR(200),
    date_ajout           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activite_id) REFERENCES activite(id_activite)
        ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES album(id_album)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- 10. ADMIN (gestion des accès — mot de passe )

CREATE TABLE admin (
    id_admin             INT AUTO_INCREMENT PRIMARY KEY,
    nom_utilisateur       VARCHAR(100) NOT NULL UNIQUE,
    mot_de_passe          VARCHAR(255) NOT NULL,
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

-- =====================================================
-- DONNÉES (seed.sql)
-- =====================================================

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE specialisation;
TRUNCATE TABLE module_programme;
TRUNCATE TABLE formation;
TRUNCATE TABLE enseignant;
TRUNCATE TABLE departement;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO departement (nom, description, responsable, contact) VALUES
('Mathématiques, Informatique et Modélisation',
 'Le département Mathématiques, Informatique et Modélisation (MIM) forme les esprits analytiques et les bâtisseurs du numérique de demain. À travers ses filières Mathématiques, Physique et Informatique (MPI) et Mathématiques Informatique Appliquées aux Sciences Sociales (MIASS), il allie rigueur scientifique et créativité technologique pour préparer des experts en data science, intelligence artificielle, cybersécurité et modélisation mathématique. Porté par une équipe pédagogique engagée et des partenariats académiques solides, le département MIM ouvre la voie à des carrières passionnantes au cœur de la révolution numérique en Afrique et dans le monde.',
 'Dr. Thierno Mohamadane Mansour SOW', 'mim.sta@uam.edu.sn'),

('Sciences de la Matière et de l\'Univers',
 'Le département Sciences de la Matière et de l\'Univers (SMU) invite à explorer les mystères de notre planète et de la matière qui nous entoure. Ses filières Sciences de la Mer et du Littoral (SML) et Physique et Applications (PA) forment des scientifiques capables de relever les défis environnementaux, énergétiques et technologiques majeurs de notre époque. Entre recherche de terrain, laboratoires modernes et projets innovants, les étudiants du SMU acquièrent une expertise reconnue en océanographie, physique appliquée et gestion durable des ressources naturelles, au service du développement du Sénégal et de l\'Afrique.',
 'Dr. Makha NDAO', 'smu.sta@uam.edu.sn');

-- =====================================================
-- FORMATIONS
-- =====================================================
INSERT INTO formation (id_formation, departement_id, nom, niveau, duree, objectif, conditions_admission, debouches) VALUES
(1, 1, 'Mathématiques, Physique et Informatique (MPI)', 'Licence', '3 ans',
 'Cette filière a pour objectif de permettre aux étudiants d\'acquérir des connaissances fondamentales, de développer des compétences analytiques et de résolution de problèmes, et de préparer aux spécialisations et à la recherche scientifique. À partir du Semestre 5, les étudiants choisissent l\'une des trois spécialisations proposées ci-dessous.',
 'Séries S1, S1A, S2, S2A, S3, S4.',
 NULL),

(2, 1, 'Mathématiques Informatique Appliquées aux Sciences Sociales (MIASS)', 'Licence', '3 ans',
 'Cette filière a pour objectif de former des spécialistes dans les métiers de la finance, de l\'économie et de la gestion des organisations et de l\'entreprise, en combinant les outils mathématiques et informatiques pour l\'analyse des phénomènes économiques et sociaux.',
 'Séries S1, S1A, S2, S2A, S3, S4, STEG.',
 'Actuariat, audit, analyste quantitatif, trader, gestionnaire de portefeuille, ingénierie financière, chargé d\'études statistiques, data analyst, contrôleur de gestion, économiste d\'entreprise, entrepreneuriat, poursuite en Master.'),

(3, 2, 'Sciences de la Mer et du Littoral (SML)', 'Licence', '3 ans',
 'Cette filière prépare les étudiants aux métiers de la protection et de l\'aménagement des côtes, de la gestion des ressources marines et des écosystèmes côtiers, et de l\'économie bleue.',
 'Séries S1, S1A, S2, S2A, S3, S4.',
 'Chercheur en biologie et écologie marine, ingénieur d\'étude en environnement littoral et marin (bureaux d\'études, collectivités territoriales, aires marines protégées), chargé de mission dans le domaine des ressources marines vivantes (aquaculture, pêche), ingénieur en dimensionnement d\'ouvrages côtiers et portuaires, technicien supérieur en métrologie et gestion du littoral, cadre écologue, responsable environnement, poursuite en Master Sciences de la Mer.');

-- =====================================================
-- SPECIALISATIONS (MPI — à partir du Semestre 5)
-- =====================================================
INSERT INTO specialisation (formation_id, nom, semestre_debut, description, debouches, departement_id) VALUES
(1, 'Mathématiques et Modélisation', 'Semestre 5',
 'Cette spécialisation approfondit le calcul scientifique, la modélisation mathématique et la simulation numérique. Elle s\'appuie sur les travaux de l\'équipe CMS (Calcul scientifique, Modélisation et Simulations numériques) du laboratoire CMED pour préparer des spécialistes capables de modéliser des phénomènes complexes et de résoudre des problèmes appliqués aux sciences, à l\'ingénierie et à l\'économie.',
 'Actuariat, ingénierie financière, data science, recherche opérationnelle, modélisation environnementale, enseignement-chercheur, ingénierie mathématique.',
 NULL),

(1, 'Informatique Appliquée', 'Semestre 5',
 'Cette spécialisation forme des ingénieurs et développeurs capables de concevoir, développer et sécuriser des systèmes informatiques modernes : intelligence artificielle, big data, IoT et cybersécurité. Elle prolonge les enseignements fondamentaux de la filière par une pratique intensive du développement logiciel et des architectures de données.',
 'Développeur, ingénieur logiciel, data scientist, administrateur systèmes et réseaux, analyste en cybersécurité, spécialiste IA/IoT, architecte de données.',
 NULL),

(1, 'Physique Appliquée', 'Semestre 5',
 'Cette spécialisation rattache les étudiants au département Sciences de la Matière et de l\'Univers (SMU) à partir du Semestre 5. Elle couvre la physique appliquée à l\'énergie, aux matériaux et à l\'instrumentation scientifique, en s\'appuyant sur les équipes de recherche MIT (Matériaux et Innovation Technologiques) du laboratoire CMED.',
 'Ingénieur en énergies renouvelables, ingénieur matériaux, technicien/ingénieur en instrumentation scientifique, recherche en physique appliquée, industries pharmaceutique et aérospatiale.',
 2);

-- =====================================================
-- PROGRAMME — TRONC COMMUN (maquettes officielles S1-S3, novembre 2024)
-- =====================================================

-- MPI (formation_id=1)
INSERT INTO module_programme (formation_id, semestre, unite_enseignement, nom_module, vht, credits, coefficient) VALUES
(1, 'Semestre 1', 'Mathématiques 1', 'Analyse 1', 70, 10, 2),
(1, 'Semestre 1', 'Mathématiques 1', 'Algèbre 1', 70, 10, 2),
(1, 'Semestre 1', 'Mathématiques 1', 'Statistique descriptive', 60, 10, 1),
(1, 'Semestre 1', 'Physique 1', 'Électricité', 80, 8, 1),
(1, 'Semestre 1', 'Physique 1', 'Mécanique du point', 80, 8, 1),
(1, 'Semestre 1', 'Informatique 1', 'Algorithmique et Programmation (Python)', 80, 8, 1),
(1, 'Semestre 1', 'Informatique 1', 'Logique combinatoire', 80, 8, 1),
(1, 'Semestre 1', 'Outils de base 1', 'Anglais 1', 28, 4, 1),
(1, 'Semestre 1', 'Outils de base 1', 'Techniques d\'expression écrite et orale en français', 28, 4, 1),
(1, 'Semestre 1', 'Outils de base 1', 'Histoire des sciences 1', 24, 4, 1),

(1, 'Semestre 2', 'Mathématiques 2', 'Analyse 2', 70, 10, 2),
(1, 'Semestre 2', 'Mathématiques 2', 'Algèbre 2', 70, 10, 2),
(1, 'Semestre 2', 'Mathématiques 2', 'Calcul numérique 1', 60, 10, 1),
(1, 'Semestre 2', 'Physique 2', 'Optique Géométrique', 80, 8, 1),
(1, 'Semestre 2', 'Physique 2', 'Magnétostatique et Régimes Variables', 80, 8, 1),
(1, 'Semestre 2', 'Informatique 2', 'Langage C', 80, 8, 1),
(1, 'Semestre 2', 'Informatique 2', 'Architecture des ordinateurs', 80, 8, 1),
(1, 'Semestre 2', 'Outils de base 2', 'Anglais 2', 28, 4, 1),
(1, 'Semestre 2', 'Outils de base 2', 'Initiation à MATLAB', 28, 4, 1),
(1, 'Semestre 2', 'Outils de base 2', 'Histoire des sciences 2', 24, 4, 1),

(1, 'Semestre 3', 'Mathématiques 3', 'Analyse 3', 65, 9, 2),
(1, 'Semestre 3', 'Mathématiques 3', 'Algèbre 3', 65, 9, 2),
(1, 'Semestre 3', 'Mathématiques 3', 'Analyse numérique matricielle', 50, 9, 1),
(1, 'Semestre 3', 'Physique 3', 'Mécanique Générale', 80, 8, 1),
(1, 'Semestre 3', 'Physique 3', 'Thermodynamique', 80, 8, 1),
(1, 'Semestre 3', 'Informatique 3', 'Programmation orientée objet (Python)', 80, 8, 1),
(1, 'Semestre 3', 'Informatique 3', 'Base de données (PostgreSQL)', 80, 8, 1),
(1, 'Semestre 3', 'Outils de base 3', 'Anglais 3', 20, 5, 1),
(1, 'Semestre 3', 'Outils de base 3', 'Projet Personnel', 20, 5, 1),
(1, 'Semestre 3', 'Outils de base 3', 'Pré-spécialisation : Science des Matériaux, Modélisation ou Cyber Sécurité et Data Sciences (au choix)', 60, 5, 2);

-- MIASS (formation_id=2)
INSERT INTO module_programme (formation_id, semestre, unite_enseignement, nom_module, vht, credits, coefficient) VALUES
(2, 'Semestre 1', 'Fondamentaux en économie et comptabilité 1', 'Analyse économique', 60, 9, 1),
(2, 'Semestre 1', 'Fondamentaux en économie et comptabilité 1', 'Macroéconomie fermée', 60, 9, 1),
(2, 'Semestre 1', 'Fondamentaux en économie et comptabilité 1', 'Comptabilité Générale', 60, 9, 1),
(2, 'Semestre 1', 'Mathématiques 1', 'Analyse 1', 70, 10, 2),
(2, 'Semestre 1', 'Mathématiques 1', 'Algèbre 1', 70, 10, 2),
(2, 'Semestre 1', 'Mathématiques 1', 'Statistique descriptive', 60, 10, 1),
(2, 'Semestre 1', 'Informatique 1', 'Algorithmique et Programmation (Python)', 80, 8, 1),
(2, 'Semestre 1', 'Informatique 1', 'Logique combinatoire', 80, 8, 1),
(2, 'Semestre 1', 'Outils de base 1', 'Anglais 1', 20, 3, 1),
(2, 'Semestre 1', 'Outils de base 1', 'Techniques d\'expression', 20, 3, 1),
(2, 'Semestre 1', 'Outils de base 1', 'Droit des propriétés intellectuelles ou Cyber droit (au choix)', 20, 3, 1),

(2, 'Semestre 2', 'Fondamentaux en économie et comptabilité 2', 'Microéconomie 1', 60, 9, 1),
(2, 'Semestre 2', 'Fondamentaux en économie et comptabilité 2', 'Marchés financiers', 60, 9, 1),
(2, 'Semestre 2', 'Fondamentaux en économie et comptabilité 2', 'Finance d\'entreprise', 60, 9, 1),
(2, 'Semestre 2', 'Mathématiques 2', 'Analyse 2', 70, 10, 2),
(2, 'Semestre 2', 'Mathématiques 2', 'Algèbre 2', 70, 10, 2),
(2, 'Semestre 2', 'Mathématiques 2', 'Méthodes quantitatives', 60, 10, 1),
(2, 'Semestre 2', 'Informatique 2', 'Structures de données (Python)', 80, 8, 1),
(2, 'Semestre 2', 'Informatique 2', 'Introduction aux bases de données (SQL)', 80, 8, 1),
(2, 'Semestre 2', 'Outils de base 2', 'Anglais 2', 20, 3, 1),
(2, 'Semestre 2', 'Outils de base 2', 'Recherche Documentaire', 20, 3, 1),
(2, 'Semestre 2', 'Outils de base 2', 'Excel avancé ou VBA (au choix)', 20, 3, 1),

(2, 'Semestre 3', 'Fondamentaux en économie et comptabilité 3', 'Microéconomie 2', 60, 9, 1),
(2, 'Semestre 3', 'Fondamentaux en économie et comptabilité 3', 'Macroéconomie ouverte', 60, 9, 1),
(2, 'Semestre 3', 'Fondamentaux en économie et comptabilité 3', 'Comptabilité de gestion 1', 60, 9, 1),
(2, 'Semestre 3', 'Mathématiques 3', 'Analyse 3', 65, 9, 2),
(2, 'Semestre 3', 'Mathématiques 3', 'Algèbre 3', 65, 9, 2),
(2, 'Semestre 3', 'Mathématiques 3', 'Mathématiques financières', 50, 9, 1),
(2, 'Semestre 3', 'Informatique 3', 'Programmation orientée objet (Python)', 80, 8, 1),
(2, 'Semestre 3', 'Informatique 3', 'Bases de données (PostgreSQL)', 80, 8, 1),
(2, 'Semestre 3', 'Outils de base 3', 'Anglais 3', 20, 4, 1),
(2, 'Semestre 3', 'Outils de base 3', 'Outils pour le Big Data (Hadoop, Spark)', 40, 4, 2),
(2, 'Semestre 3', 'Outils de base 3', 'Sociologie des politiques, Éthique et données ou Sociologie du risque (au choix)', 20, 4, 1);

-- SML (formation_id=3)
INSERT INTO module_programme (formation_id, semestre, unite_enseignement, nom_module, vht, credits, coefficient) VALUES
(3, 'Semestre 1', 'Mathématiques 1', 'Analyse 1', 70, 10, 2),
(3, 'Semestre 1', 'Mathématiques 1', 'Algèbre 1', 70, 10, 2),
(3, 'Semestre 1', 'Mathématiques 1', 'Statistique descriptive', 60, 10, 1),
(3, 'Semestre 1', 'Physique 1', 'Électricité', 80, 8, 1),
(3, 'Semestre 1', 'Physique 1', 'Mécanique du point', 80, 8, 1),
(3, 'Semestre 1', 'Informatique 1', 'Algorithmique et Programmation (Python)', 80, 8, 1),
(3, 'Semestre 1', 'Informatique 1', 'Logique combinatoire', 80, 8, 1),
(3, 'Semestre 1', 'Géosciences', 'Géodynamique de la terre', 20, 2, 1),
(3, 'Semestre 1', 'Géosciences', 'Océanographie', 20, 2, 1),
(3, 'Semestre 1', 'Outils de base 1', 'Anglais 1', 20, 2, 1),
(3, 'Semestre 1', 'Outils de base 1', 'Techniques d\'expression écrite et orale en français', 20, 2, 1),

(3, 'Semestre 2', 'Mathématiques 2', 'Analyse 2', 70, 10, 2),
(3, 'Semestre 2', 'Mathématiques 2', 'Algèbre 2', 70, 10, 2),
(3, 'Semestre 2', 'Mathématiques 2', 'Calcul numérique 1', 60, 10, 1),
(3, 'Semestre 2', 'Physique 2', 'Optique Géométrique', 80, 8, 1),
(3, 'Semestre 2', 'Physique 2', 'Magnétostatique et Régimes Variables', 80, 8, 1),
(3, 'Semestre 2', 'Informatique 2', 'Structures de données (Python)', 80, 8, 1),
(3, 'Semestre 2', 'Informatique 2', 'Introduction aux bases de données (SQL)', 80, 8, 1),
(3, 'Semestre 2', 'Sciences Maritimes 1', 'Géologie marine', 20, 2, 1),
(3, 'Semestre 2', 'Sciences Maritimes 1', 'Biologie', 20, 2, 1),
(3, 'Semestre 2', 'Outils de base 2', 'Anglais 2', 20, 2, 1),
(3, 'Semestre 2', 'Outils de base 2', 'Initiation à MATLAB', 20, 2, 1),

(3, 'Semestre 3', 'Mathématiques 3', 'Analyse 3', 65, 9, 2),
(3, 'Semestre 3', 'Mathématiques 3', 'Algèbre 3', 65, 9, 2),
(3, 'Semestre 3', 'Mathématiques 3', 'Analyse numérique matricielle', 50, 9, 1),
(3, 'Semestre 3', 'Physique 3', 'Mécanique Générale', 80, 8, 1),
(3, 'Semestre 3', 'Physique 3', 'Thermodynamique', 80, 8, 1),
(3, 'Semestre 3', 'Informatique 3', 'Programmation orientée objet (Python)', 70, 7, 1),
(3, 'Semestre 3', 'Informatique 3', 'Base de données (PostgreSQL)', 70, 7, 1),
(3, 'Semestre 3', 'Chimie 1', 'Atomistique et Liaisons chimiques', 40, 4, 1),
(3, 'Semestre 3', 'Chimie 1', 'Thermochimie et Equilibre Chimique', 40, 4, 1),
(3, 'Semestre 3', 'Outils de base 3', 'Projet Personnel', 20, 2, 1),
(3, 'Semestre 3', 'Outils de base 3', 'Anglais 3', 20, 2, 1);

-- =====================================================
-- ENSEIGNANTS
-- =====================================================
INSERT INTO enseignant (nom, grade, fonction, discipline, specialite_cames, domaines_recherche, photo) VALUES
('Dr. Thierno Mohamadane Mansour SOW', 'Maître de Conférences Titulaire', NULL,
 'Mathématiques Appliquées',
 'Mathématiques Appliquées',
 'Analyse Non linéaire\nGéométrie des Espaces de Banach\nOptimisation et méthodes itératives\nAnalyse Fonctionnelle\nCalcul des Variations',
 'images/sow.png'),

('Dr. Makha NDAO', 'Maître de Conférences Titulaire', NULL,
 'Nanosciences Nanotechnologie Matériaux',
 'Physique : Milieux denses et matériaux',
 'Biomasse et stockage d\'énergie (supercondensateurs, piles) et traitement des eaux\nPolymères et élastomères pour l\'industrie\nSéparation des phases fluides (simulation numérique et expériences)\nPollution marine par les microplastiques\nQualité des eaux et traitements (Osmose inverse, Nanofiltration, Microfiltration, Ultrafiltration)',
 'images/Makha.png'),

('Dr. Alioune COULIBALY', 'Maître de Conférences Titulaire',
 'Directeur de l\'UFR Sciences et Technologies Avancées (STA)',
 'Mathématiques appliquées (Méthodes aléatoires)',
 'Mathématiques : Mathématiques appliquées (Méthodes aléatoires)',
 'Equations aux dérivées partielles (EDP) – Equations différentielles stochastiques (EDS)\nAnalyse fonctionnelle\nProbabilité – Statistique\nSystèmes dynamiques\nCalcul stochastique',
 'images/coulibaly.png'),

('Pr. Issa SAKHO', 'Professeur assimilé',
 'Vice-recteur chargé de la Recherche, de l\'Innovation et du Partenariat',
 'Géosciences marines et littorales',
 'Géosciences marines et littorales',
 'Dynamique physique des systèmes sédimentaires littoraux\nForçages météo-océaniques, Risques littoraux et infrastructures de protection côtière (SD et SFN)\nTransfert de matières (eau, sédiment, dissout) dans les grands hydro-systèmes : de la source à la mer\nDynamique et fonctionnement des écosystèmes de carbone bleu : mangroves et herbiers',
 'images/Sakho.png'),

('Pr. Amadou Dahirou GUEYE', 'Professeur Titulaire',
 'Vice-Recteur chargé des Affaires pédagogiques et de la Vie universitaire',
 'Informatique',
 'Informatique',
 'Télé-laboratoires et Organisations virtuelles\nTélé-enseignement\nIntelligence artificielle appliquée à la santé, la sécurité routière, l\'éducation et l\'environnement\nInternet des Objets et Cloud',
 'images/Dahirou.png'),

('Dr. Sada ANNE', 'Docteur', NULL, NULL, NULL, NULL, 'images/Anne.png'),

('Dr. Lamine YADE', 'Docteur', NULL, NULL, NULL, NULL, 'images/yade.png'),

('Dr. Siny NDOYE', 'Maître de Conférences Titulaire', NULL,
 'Physique: Océanographie et Applications',
 'Physique: Océanographie et Applications',
 'Dynamique Océanique (Hydrodynamique des fluides géophysiques)\nDynamique de l\'Upwelling côtier Ouest Africain\nPollution marine et dimensionnement d\'émissaire en mer\nChangement climatique et Événements extrêmes (Impact du changement climatique sur la dynamique océanique)\nModélisation hydrodynamique de l\'environnement marin et côtier',
 'images/Ndoye.png');
