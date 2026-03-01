-- BLOQUE 1 - Verificar snapshot de units
SELECT COUNT(*) FROM units;

-- Verificación de estados
SELECT unit_state, COUNT(*) 
FROM units 
GROUP BY unit_state;

SELECT COUNT(*)
FROM unit_rentals
WHERE rental_state = 'occupied';

SELECT COUNT(*) AS monthly_occupied
FROM unit_rentals
WHERE rental_state = 'occupied'
  AND external_rental_id LIKE 'MONTHLY_RENT_%';
  
SELECT
  u.unit_number,
  ur.external_rental_id,
  ur.billing_type,
  ur.rental_state
FROM unit_rentals ur
JOIN units u ON u.external_unit_id = ur.external_unit_id
WHERE ur.external_rental_id LIKE 'MONTHLY_RENT_%'
ORDER BY u.unit_number;

SELECT
  u.unit_number,
  u.unit_state,
  ur.unit_rental_id,
  ur.external_rental_id,
  ur.rental_state,
  ur.updated_at,
  ur.move_in_date,
  ur.move_out_date
FROM unit_rentals ur
JOIN units u ON u.external_unit_id = ur.external_unit_id
WHERE ur.rental_state = 'occupied'
  AND (ur.external_rental_id NOT LIKE 'MONTHLY_RENT_%' OR ur.external_rental_id IS NULL)
  AND u.unit_state <> 'occupied'
ORDER BY ur.updated_at DESC;