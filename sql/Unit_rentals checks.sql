SELECT * FROM storage_project.unit_rentals;

ALTER TABLE unit_rentals
ADD COLUMN billing_type VARCHAR(20) NOT NULL DEFAULT '28_days'
AFTER price_eur;

SELECT billing_type, COUNT(*) AS n
FROM unit_rentals
GROUP BY billing_type;

UPDATE unit_rentals
SET billing_type = 'monthly'
WHERE external_rental_id LIKE 'MONTHLY_RENT_%';

SELECT COUNT(*) AS monthly_rows
FROM unit_rentals
WHERE external_rental_id LIKE 'MONTHLY_RENT_%';