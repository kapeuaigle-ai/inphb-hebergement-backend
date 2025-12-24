-- 05_data_init.sql

-- Insertion des bâtiments
INSERT INTO BATIMENT (id_batiment, nom_batiment, type_public, niveaux_etudes, type_chambre, nombre_niveaux, nombre_chambres, capacite)
VALUES ('A', 'Bâtiment A', 'GARCONS', 'TOUS', 'SIMPLE', 3, 96, 96);
INSERT INTO BATIMENT (id_batiment, nom_batiment, type_public, niveaux_etudes, type_chambre, nombre_niveaux, nombre_chambres, capacite)
VALUES ('G', 'Bâtiment G', 'MIXTE', 'TOUS', 'DOUBLE', 3, 96, 192);
-- ... Continuer pour les 16 bâtiments

-- Insertion d'une année académique
INSERT INTO ANNEE_ACADEMIQUE (id_annee, libelle, date_debut, date_fin, date_limite_depot_cle, est_active)
VALUES ('2024-2025', 'Année Académique 2024-2025', TO_DATE('2024-09-01', 'YYYY-MM-DD'), TO_DATE('2025-06-30', 'YYYY-MM-DD'), TO_DATE('2025-07-05', 'YYYY-MM-DD'), 1);

-- Insertion de l'admin
INSERT INTO GESTIONNAIRE (nom, prenom, contact, email, mot_de_passe, role)
VALUES ('ADMIN', 'Système', '0102030405', 'admin@inphb.ci', 'hashed_password_here', 'ADMIN');
