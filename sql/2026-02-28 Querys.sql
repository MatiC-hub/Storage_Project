-- 1) Customers (snapshot 2026-02-28)  
-- A) Totales y “hoy”
-- Total customers
SELECT COUNT(*) AS total_customers
FROM customers;

-- ¿Cuántos customers “tocados” hoy? (según updated_at)
SELECT COUNT(*) AS updated_today
FROM customers
WHERE DATE(updated_at) = '2026-02-28';

-- Rango de updated_at para ver si estás realmente en 28
SELECT
  MIN(updated_at) AS min_updated_at,
  MAX(updated_at) AS max_updated_at
FROM customers;

SELECT
  MIN(updated_at) AS min_updated_at,
  MAX(updated_at) AS max_updated_at,
  COUNT(*) AS total
FROM customers;

SELECT updated_at
FROM customers
ORDER BY updated_at DESC
LIMIT 10;

-- Cuántos con updated_at en 2026-02-28 (si se está seteando bien)
SELECT COUNT(*) AS updated_on_2026_02_28
FROM customers
WHERE updated_at >= '2026-02-28 00:00:00'
  AND updated_at <  '2026-02-29 00:00:00';

-- 2) Queries de checking (Rentals 2026-02-28)
-- Total rentals
SELECT COUNT(*) AS total_rentals
FROM unit_rentals;

-- Billing types
SELECT billing_type, COUNT(*) AS n
FROM unit_rentals
GROUP BY billing_type;

-- Cuántas monthly (por id manual)
SELECT COUNT(*) AS monthly_rows
FROM unit_rentals
WHERE external_rental_id LIKE 'MONTHLY_RENT_%';

-- Min/Max updated_at
SELECT MIN(updated_at) AS min_updated_at, MAX(updated_at) AS max_updated_at
FROM unit_rentals;

-- Últimas 10
SELECT unit_rental_id, external_rental_id, billing_type, updated_at
FROM unit_rentals
ORDER BY updated_at DESC
LIMIT 10;

-- 3) OTRAS
SHOW COLUMNS FROM customers LIKE 'updated_at';

SELECT 
  COUNT(*) AS total,
  SUM(updated_at IS NULL) AS updated_at_null
FROM customers;

SELECT
  COUNT(*) AS total,
  SUM(external_owner_id IS NULL) AS external_null
FROM customers;

SELECT
  SUM(city IS NULL) AS city_null,
  SUM(province IS NULL) AS province_null,
  SUM(country IS NULL) AS country_null
FROM customers;

SELECT external_owner_id, COUNT(*) AS n
FROM customers
GROUP BY external_owner_id
HAVING COUNT(*) > 1;

SELECT 
    customer_id,
    external_owner_id,
    city,
    province,
    country
FROM customers
WHERE city IS NULL
   OR province IS NULL
   OR country IS NULL
ORDER BY external_owner_id;

SELECT 
    is_business_account,
    customer_status,
    COUNT(*) AS n
FROM customers
WHERE city IS NULL
   OR province IS NULL
   OR country IS NULL
GROUP BY is_business_account, customer_status
ORDER BY n DESC;

SELECT 
    COUNT(*) AS total_incomplete,
    SUM(country IS NULL AND province IS NOT NULL) AS can_infer_spain
FROM customers
WHERE city IS NULL
   OR province IS NULL
   OR country IS NULL;
   
SELECT 
    c.customer_id,
    c.external_owner_id,
    c.city,
    c.province,
    c.country,
    ur.external_unit_id,
    ur.external_rental_id,
    ur.rental_state
FROM customers c
LEFT JOIN unit_rentals ur
    ON ur.external_owner_id = c.external_owner_id
WHERE c.city IS NULL
   OR c.province IS NULL
   OR c.country IS NULL
ORDER BY c.external_owner_id;

SELECT 
    c.customer_id,
    c.external_owner_id,
    c.city,
    c.province,
    c.country,
    ur.external_unit_id,
    ur.external_rental_id,
    ur.rental_state,
    ur.updated_at
FROM customers c
LEFT JOIN (
    SELECT ur1.*
    FROM unit_rentals ur1
    JOIN (
        SELECT external_owner_id, MAX(updated_at) AS max_updated
        FROM unit_rentals
        GROUP BY external_owner_id
    ) ur2
      ON ur1.external_owner_id = ur2.external_owner_id
     AND ur1.updated_at = ur2.max_updated
) ur
    ON ur.external_owner_id = c.external_owner_id
WHERE c.city IS NULL
   OR c.province IS NULL
   OR c.country IS NULL
ORDER BY ur.updated_at DESC;

SELECT 
    c.customer_id,
    c.external_owner_id,
    c.city,
    c.province,
    c.country,
    u.unit_id,
    u.external_unit_id,
    u.unit_number,
    ur.rental_state,
    ur.updated_at
FROM customers c
LEFT JOIN unit_rentals ur
    ON ur.external_owner_id = c.external_owner_id
LEFT JOIN units u
    ON u.external_unit_id = ur.external_unit_id
WHERE c.city IS NULL
   OR c.province IS NULL
   OR c.country IS NULL
ORDER BY ur.updated_at DESC;

SELECT 
    external_unit_id,
    unit_number,
    external_owner_id,
    rental_state,
    updated_at
FROM unit_rentals ur
JOIN units u
    ON u.external_unit_id = ur.external_unit_id
WHERE u.unit_number = 'c3001'
ORDER BY updated_at DESC;

SELECT *
FROM units
WHERE unit_number = 'c3001';

SELECT COUNT(*)
FROM unit_rentals;

SELECT MAX(updated_at)
FROM unit_rentals;

SELECT *
FROM unit_rentals
WHERE external_unit_id = '6909d7ef26c223f960ef9afc';

-- Rentals "ocupadas" sin customer
SELECT 
    ur.unit_rental_id,
    ur.unit_id,
    u.unit_number,
    ur.move_in_date,
    ur.move_out_date,
    ur.rental_state,
    ur.customer_id
FROM unit_rentals ur
JOIN units u 
    ON u.unit_id = ur.unit_id
WHERE ur.rental_state = 'occupied'
  AND ur.customer_id IS NULL;
  
-- Units ocupadas pero sin rental válido
SELECT 
    u.unit_id,
    u.unit_number,
    u.unit_state
FROM units u
LEFT JOIN unit_rentals ur
    ON ur.unit_id = u.unit_id
    AND ur.rental_state = 'occupied'
    AND ur.customer_id IS NOT NULL
WHERE u.unit_state = 'occupied'
  AND ur.unit_rental_id IS NULL;