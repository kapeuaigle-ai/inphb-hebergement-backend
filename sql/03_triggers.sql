-- 03_triggers.sql

-- Trigger pour mettre à jour la disponibilité de la chambre
CREATE OR REPLACE TRIGGER TRG_UPDATE_DISPONIBILITE_INS
AFTER INSERT ON OCCUPATION
FOR EACH ROW
DECLARE
    v_nb_occupants NUMBER;
    v_capacite NUMBER;
    v_type VARCHAR2(10);
BEGIN
    SELECT type_chambre, capacite INTO v_type, v_capacite FROM CHAMBRE WHERE id_chambre = :NEW.id_chambre;
    
    SELECT COUNT(*) INTO v_nb_occupants FROM OCCUPATION WHERE id_chambre = :NEW.id_chambre AND date_sortie IS NULL;
    
    IF v_nb_occupants >= v_capacite THEN
        UPDATE CHAMBRE SET is_available = 0 WHERE id_chambre = :NEW.id_chambre;
    ELSE
        UPDATE CHAMBRE SET is_available = 1 WHERE id_chambre = :NEW.id_chambre;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER TRG_UPDATE_DISPONIBILITE_DEL
AFTER DELETE ON OCCUPATION
FOR EACH ROW
DECLARE
    v_nb_occupants NUMBER;
    v_capacite NUMBER;
BEGIN
    SELECT capacite INTO v_capacite FROM CHAMBRE WHERE id_chambre = :OLD.id_chambre;
    SELECT COUNT(*) INTO v_nb_occupants FROM OCCUPATION WHERE id_chambre = :OLD.id_chambre AND date_sortie IS NULL;
    
    IF v_nb_occupants < v_capacite THEN
        UPDATE CHAMBRE SET is_available = 1 WHERE id_chambre = :OLD.id_chambre;
    END IF;
END;
/

-- Trigger pour la suspension/blocage
CREATE OR REPLACE TRIGGER TRG_DEBLOCAGE
BEFORE UPDATE ON ETUDIANT
FOR EACH ROW
WHEN (NEW.etat_etudiant = 'BLOQUE' AND OLD.etat_etudiant = 'SUSPENDU')
BEGIN
    :NEW.date_deblocage := SYSDATE + 7;
END;
/
