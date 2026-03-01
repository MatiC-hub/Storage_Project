-- 1) Unidades "mismatch"
SELECT
  u.unit_number,
  u.unit_state,
  ur.unit_rental_id,
  ur.external_rental_id,
  ur.rental_state,
  ur.updated_at,
  ur.move_in_date,
  ur.move_out_date
FROM units u
JOIN unit_rentals ur
  ON ur.external_unit_id = u.external_unit_id
WHERE u.unit_state = 'available'
  AND ur.rental_state = 'occupied'
  AND (ur.external_rental_id NOT LIKE 'MONTHLY_RENT_%' OR ur.external_rental_id IS NULL)
ORDER BY ur.updated_at DESC;

-- 2) Contar mismatches
SELECT COUNT(*) AS mismatches
FROM units u
JOIN unit_rentals ur
  ON ur.external_unit_id = u.external_unit_id
WHERE u.unit_state = 'available'
  AND ur.rental_state = 'occupied'
  AND (ur.external_rental_id NOT LIKE 'MONTHLY_RENT_%' OR ur.external_rental_id IS NULL);
  
-- 3) Control mensual + test
SELECT
  u.unit_state,
  COUNT(*) AS n
FROM units u
GROUP BY u.unit_state;

SELECT
  u.unit_state,
  CASE
    WHEN mu.unit_number IS NOT NULL THEN 'monthly'
    WHEN tu.unit_number IS NOT NULL THEN 'test'
    ELSE 'normal'
  END AS blocked_reason,
  COUNT(*) AS n
FROM units u
LEFT JOIN ref_monthly_units mu ON mu.unit_number = u.unit_number
LEFT JOIN ref_test_units tu ON tu.unit_number = u.unit_number
WHERE u.unit_state = 'blocked'
GROUP BY u.unit_state, blocked_reason;