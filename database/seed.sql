USE ufr_sta_db;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE module_programme;
TRUNCATE TABLE formation;
TRUNCATE TABLE enseignant;
TRUNCATE TABLE departement;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO departement (nom, description, responsable, contact) VALUES
('Mathématiques, Physique et Informatique',
 'Le département MPI forme des étudiants en mathématiques, physique et informatique avec une approche pluridisciplinaire orientée vers les sciences fondamentales et appliquées.',
 'À définir', NULL),

('Sciences de la Mer et du Littoral',
 'Le département SML forme des spécialistes en sciences marines, gestion des ressources côtières et environnement littoral, en lien avec les enjeux du Sénégal maritime.',
 'À définir', NULL),

('Mathématiques Informatique Appliquées aux Sciences Sociales',
 'Le département MIASS forme des étudiants à l\'utilisation des mathématiques et de l\'informatique comme outils d\'analyse des phénomènes sociaux, économiques et humains.',
 'À définir', NULL);