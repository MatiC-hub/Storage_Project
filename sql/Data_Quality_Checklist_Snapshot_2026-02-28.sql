-- Customers
SELECT COUNT(*) AS total_customers
FROM customers;

SELECT COUNT(*) AS without_external_id
FROM customers
WHERE external_owner_id IS NULL;

SELECT
    SUM(city IS NULL) AS city_null,
    SUM(province IS NULL) AS province_null,
    SUM(country IS NULL) AS country_null
FROM customers;

SELECT COUNT(*) AS active_incomplete
FROM customers c
JOIN unit_rentals ur
  ON ur.customer_id = c.customer_id
WHERE ur.rental_state = 'occupied'
  AND (c.city IS NULL OR c.province IS NULL OR c.country IS NULL);

-- Rentals
SELECT COUNT(*) AS total_rentals
FROM unit_rentals;

SELECT billing_type, COUNT(*) 
FROM unit_rentals
GROUP BY billing_type;
SELECT COUNT(*)
FROM units u
LEFT JOIN unit_rentals ur
  ON ur.unit_id = u.unit_id
  AND ur.rental_state = 'occupied'
  AND ur.customer_id IS NOT NULL
WHERE u.unit_state = 'occupied'
  AND ur.unit_rental_id IS NULL;
  
SELECT
  c.customer_id,
  c.external_owner_id,
  c.city, c.province, c.country,
  ur.unit_rental_id,
  ur.external_rental_id,
  ur.external_unit_id,
  ur.rental_state,
  ur.updated_at,
  u.unit_number
FROM customers c
JOIN unit_rentals ur ON ur.customer_id = c.customer_id
LEFT JOIN units u ON u.external_unit_id = ur.external_unit_id
WHERE ur.rental_state = 'occupied'
  AND (c.city IS NULL OR c.province IS NULL OR c.country IS NULL);
  
-- Referential Integrity
SELECT COUNT(*)
FROM unit_rentals ur
LEFT JOIN units u
  ON u.unit_id = ur.unit_id
WHERE u.unit_id IS NULL;

SELECT COUNT(*)
FROM unit_rentals ur
LEFT JOIN customers c
  ON c.customer_id = ur.customer_id
WHERE ur.customer_id IS NOT NULL
  AND c.customer_id IS NULL;
  
SELECT COUNT(*) AS rentals_unit_id_null
FROM unit_rentals
WHERE unit_id IS NULL;

SELECT COUNT(*) AS rentals_with_missing_external_unit
FROM unit_rentals ur
LEFT JOIN units u
  ON u.external_unit_id = ur.external_unit_id
WHERE ur.external_unit_id IS NOT NULL
  AND u.external_unit_id IS NULL;

SELECT ur.unit_rental_id, ur.external_rental_id, ur.external_unit_id
FROM unit_rentals ur
LEFT JOIN units u
  ON u.external_unit_id = ur.external_unit_id
WHERE ur.external_unit_id IS NOT NULL
  AND u.external_unit_id IS NULL;
  
SELECT
  customer_id,
  external_owner_id,
  nationality,
  language,
  city,
  province,
  country,
  is_business_account
FROM customers
WHERE external_owner_id LIKE 'MONTHLY_CUST_%'
  AND (city IS NULL OR province IS NULL)
ORDER BY external_owner_id;

SELECT
  c.external_owner_id,
  c.city, c.province, c.country,
  u.unit_number,
  ur.rental_state,
  ur.billing_type
FROM customers c
JOIN unit_rentals ur ON ur.customer_id = c.customer_id
LEFT JOIN units u ON u.unit_id = ur.unit_id
WHERE c.external_owner_id LIKE 'MONTHLY_CUST_%'
  AND ur.rental_state = 'occupied'
  AND (c.city IS NULL OR c.province IS NULL)
ORDER BY c.external_owner_id;

SELECT
  SUM(city IS NULL) AS city_null,
  SUM(province IS NULL) AS province_null,
  SUM(country IS NULL) AS country_null
FROM customers
WHERE external_owner_id LIKE 'MONTHLY_CUST_%';
