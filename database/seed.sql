USE ufr_sta_db;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE module_programme;
TRUNCATE TABLE formation;
TRUNCATE TABLE enseignant;
TRUNCATE TABLE departement;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO departement (nom, description, responsable, contact) VALUES
('Mathématiques, Informatique et Modélisation',
 'Le département Mathématiques, Informatique et Modélisation (MIM) forme les esprits analytiques et les bâtisseurs du numérique de demain. À travers ses filières Mathématiques, Physique et Informatique (MPI) et Mathématiques Informatique Appliquées aux Sciences Sociales (MIASS), il allie rigueur scientifique et créativité technologique pour préparer des experts en data science, intelligence artificielle, cybersécurité et modélisation mathématique. Porté par une équipe pédagogique engagée et des partenariats académiques solides, le département MIM ouvre la voie à des carrières passionnantes au cœur de la révolution numérique en Afrique et dans le monde.',
 'Dr. Thierno Mouhamadan Mansour SOW', 'mim.sta@uam.edu.sn'),

('Sciences de la Matière et de l\'Univers',
 'Le département Sciences de la Matière et de l\'Univers (SMU) invite à explorer les mystères de notre planète et de la matière qui nous entoure. Ses filières Sciences de la Mer et du Littoral (SML) et Physique et Applications (PA) forment des scientifiques capables de relever les défis environnementaux, énergétiques et technologiques majeurs de notre époque. Entre recherche de terrain, laboratoires modernes et projets innovants, les étudiants du SMU acquièrent une expertise reconnue en océanographie, physique appliquée et gestion durable des ressources naturelles, au service du développement du Sénégal et de l\'Afrique.',
 'Dr. Makha NDAO', 'smu.sta@uam.edu.sn');