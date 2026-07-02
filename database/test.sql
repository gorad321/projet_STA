-- =====================================================
-- UFR STA — Données de test (seed.sql)
-- À importer dans phpMyAdmin après schema.sql
-- =====================================================

USE ufr_sta_db;

-- =====================================================
-- 1. DEPARTEMENTS
-- =====================================================
INSERT INTO departement (nom, description, responsable, contact) VALUES
('Informatique', 'Le département Informatique forme des étudiants aux sciences du numérique, à la programmation, aux systèmes d\'information et à l\'intelligence artificielle.', 'Pr. Amadou DIALLO', 'info.sta@uam.edu.sn'),
('Mathématiques', 'Le département Mathématiques assure une formation solide en mathématiques fondamentales et appliquées, ouvrant vers la recherche et l\'ingénierie.', 'Pr. Fatou NDIAYE', 'maths.sta@uam.edu.sn'),
('Physique', 'Le département Physique forme des étudiants en physique fondamentale et appliquée, avec des débouchés dans la recherche, l\'industrie et l\'enseignement.', 'Pr. Moussa SECK', 'physique.sta@uam.edu.sn');

-- =====================================================
-- 2. FORMATIONS
-- =====================================================
INSERT INTO formation (departement_id, nom, niveau, duree, conditions_admission, debouches) VALUES
(1, 'Licence Informatique', 'Licence', '3 ans', 'Baccalauréat série S, L ou équivalent. Concours d\'entrée ou dossier.', 'Développeur web, analyste système, administrateur réseau, data analyst, poursuite en Master.'),
(1, 'Master Informatique', 'Master', '2 ans', 'Licence Informatique ou équivalent. Dossier de candidature.', 'Ingénieur logiciel, chef de projet IT, data scientist, chercheur, enseignant-chercheur.'),
(2, 'Licence Mathématiques', 'Licence', '3 ans', 'Baccalauréat série S ou équivalent. Bonnes bases en mathématiques requises.', 'Enseignement, actuariat, finance, ingénierie, poursuite en Master.'),
(2, 'Master Mathématiques', 'Master', '2 ans', 'Licence Mathématiques ou équivalent.', 'Chercheur, actuaire, ingénieur financier, enseignant-chercheur.'),
(3, 'Licence Physique', 'Licence', '3 ans', 'Baccalauréat série S ou équivalent.', 'Enseignement, recherche, industrie, énergie, poursuite en Master.'),
(3, 'Master Physique', 'Master', '2 ans', 'Licence Physique ou équivalent.', 'Chercheur, ingénieur en énergie, enseignant-chercheur.');

-- =====================================================
-- 3. MODULES PROGRAMME
-- =====================================================

-- Licence Informatique (id=1)
INSERT INTO module_programme (formation_id, semestre, nom_module) VALUES
(1, 'Semestre 1', 'Algorithmique'),
(1, 'Semestre 1', 'Python'),
(1, 'Semestre 1', 'Logique mathématique'),
(1, 'Semestre 1', 'Mathématiques discrètes'),
(1, 'Semestre 2', 'Programmation Orientée Objet'),
(1, 'Semestre 2', 'Base de données'),
(1, 'Semestre 2', 'Système d\'exploitation'),
(1, 'Semestre 2', 'Cybersécurité'),
(1, 'Semestre 3', 'Développement Web'),
(1, 'Semestre 3', 'Réseaux informatiques'),
(1, 'Semestre 3', 'Structures de données'),
(1, 'Semestre 4', 'Intelligence Artificielle'),
(1, 'Semestre 4', 'Génie Logiciel'),
(1, 'Semestre 4', 'Administration système'),
(1, 'Semestre 5', 'Machine Learning'),
(1, 'Semestre 5', 'Cloud Computing'),
(1, 'Semestre 5', 'Projet tutoré'),
(1, 'Semestre 6', 'Stage professionnel'),
(1, 'Semestre 6', 'Mémoire de licence');

-- Master Informatique (id=2)
INSERT INTO module_programme (formation_id, semestre, nom_module) VALUES
(2, 'Semestre 1', 'Deep Learning'),
(2, 'Semestre 1', 'Big Data'),
(2, 'Semestre 1', 'Architecture logicielle'),
(2, 'Semestre 2', 'Vision par ordinateur'),
(2, 'Semestre 2', 'Traitement du langage naturel'),
(2, 'Semestre 2', 'Sécurité avancée'),
(2, 'Semestre 3', 'Recherche et innovation'),
(2, 'Semestre 3', 'Projet de recherche'),
(2, 'Semestre 4', 'Stage de recherche'),
(2, 'Semestre 4', 'Mémoire de master');

-- =====================================================
-- 4. ENSEIGNANTS
-- =====================================================
INSERT INTO enseignant (departement_id, nom, grade, email, domaines_recherche, photo) VALUES
(1, 'Pr. Amadou DIALLO', 'Professeur Titulaire', 'a.diallo@uam.edu.sn', 'Intelligence Artificielle, Machine Learning, Vision par ordinateur', NULL),
(1, 'Dr. Aïssatou MBAYE', 'Maître de Conférences', 'a.mbaye@uam.edu.sn', 'Cybersécurité, Réseaux, Systèmes distribués', NULL),
(1, 'Dr. Ibrahima FALL', 'Maître Assistant', 'i.fall@uam.edu.sn', 'Développement web, Génie logiciel, Base de données', NULL),
(2, 'Pr. Fatou NDIAYE', 'Professeur Titulaire', 'f.ndiaye@uam.edu.sn', 'Mathématiques appliquées, Optimisation, Recherche opérationnelle', NULL),
(2, 'Dr. Cheikh GUEYE', 'Maître de Conférences', 'c.gueye@uam.edu.sn', 'Probabilités, Statistiques, Actuariat', NULL),
(3, 'Pr. Moussa SECK', 'Professeur Titulaire', 'm.seck@uam.edu.sn', 'Physique théorique, Énergie renouvelable, Astrophysique', NULL);

-- =====================================================
-- 5. ACTUALITES
-- =====================================================
INSERT INTO actualite (titre, date_publication, description, photo, type) VALUES
('Résultats du concours d\'entrée en Licence 2025-2026', '2025-09-15', 'Les résultats du concours d\'entrée en Licence à l\'UFR STA pour l\'année académique 2025-2026 sont disponibles. Les candidats admis sont invités à procéder aux inscriptions administratives du 20 au 30 septembre 2025.', NULL, 'résultat'),
('Séminaire international sur l\'IA et le développement durable', '2025-10-10', 'L\'UFR STA organise un séminaire international sur l\'Intelligence Artificielle et le développement durable en Afrique. L\'événement se tiendra les 25 et 26 octobre 2025 dans la salle de conférence de l\'UAM.', NULL, 'séminaire'),
('Appel à candidature — Master Informatique 2026', '2026-01-05', 'L\'UFR STA lance un appel à candidature pour le Master Informatique, spécialité Intelligence Artificielle et Data Science, pour l\'année 2026-2027. Date limite de dépôt des dossiers : 28 février 2026.', NULL, 'appel'),
('Conférence : Les métiers du numérique au Sénégal', '2026-03-20', 'Une conférence sur les métiers du numérique et les opportunités d\'emploi dans le secteur IT au Sénégal sera organisée le 5 avril 2026. Intervenants : professionnels de grandes entreprises technologiques.', NULL, 'conférence'),
('Soutenances de mémoires de Master — Session juin 2026', '2026-05-28', 'Les soutenances de mémoires de Master de l\'UFR STA auront lieu du 15 au 25 juin 2026. Les étudiants concernés sont invités à déposer leurs mémoires au secrétariat avant le 31 mai 2026.', NULL, 'soutenance');

-- =====================================================
-- 6. ACTIVITES
-- =====================================================
INSERT INTO activite (titre, date_activite, lieu, organisateur, description) VALUES
('Atelier IA Générative', '2026-04-15', 'Salle Informatique — UFR STA', 'Département Informatique', 'Formation destinée aux étudiants de L3 Informatique sur l\'utilisation de l\'IA générative dans les projets académiques et professionnels. Thèmes abordés : prompting, outils IA, éthique de l\'IA.'),
('Hackathon UFR STA 2026', '2026-03-08', 'Amphi A — UAM', 'Club Informatique UFR STA', 'Compétition de 24h réunissant les étudiants de l\'UFR STA autour de problématiques liées au numérique et au développement en Afrique. Prix pour les trois meilleures équipes.'),
('Visite pédagogique — Entreprise Orange Sénégal', '2026-02-20', 'Siège Orange Sénégal, Dakar', 'Département Informatique', 'Sortie pédagogique au siège d\'Orange Sénégal pour découvrir les métiers du numérique et les infrastructures télécoms. 45 étudiants de L3 et Master ont participé.'),
('Journée scientifique UFR STA', '2025-12-12', 'Campus UAM', 'Direction UFR STA', 'Journée dédiée à la présentation des travaux de recherche des enseignants et des projets des étudiants. Expositions, présentations et remise de prix aux meilleurs projets étudiants.');

-- =====================================================
-- 7. ALBUMS
-- =====================================================
INSERT INTO album (titre, description, date_album) VALUES
('Hackathon UFR STA 2026', 'Photos de la compétition Hackathon organisée en mars 2026', '2026-03-08'),
('Journée scientifique 2025', 'Galerie photos de la journée scientifique annuelle de l\'UFR STA', '2025-12-12'),
('Visite Orange Sénégal', 'Photos de la sortie pédagogique au siège d\'Orange Sénégal', '2026-02-20');

-- =====================================================
-- 8. ADMIN (mot de passe temporaire — sera hashé en Phase 4)
-- =====================================================
INSERT INTO admin (nom_utilisateur, mot_de_passe) VALUES
('admin', 'admin123');