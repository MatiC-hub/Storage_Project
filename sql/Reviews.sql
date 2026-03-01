SELECT 
    COUNT(*) AS total,
    SUM(first_name IS NOT NULL) AS first_name_not_null,
    SUM(last_name IS NOT NULL) AS last_name_not_null,
    SUM(email_primary IS NOT NULL) AS email_primary_not_null,
    SUM(email_secondary IS NOT NULL) AS email_secondary_not_null,
    SUM(phone_primary IS NOT NULL) AS phone_primary_not_null,
    SUM(phone_secondary IS NOT NULL) AS phone_secondary_not_null
FROM customers;

SELECT external_owner_id, first_name, last_name, email_primary
FROM customers
WHERE first_name IS NOT NULL
   OR last_name IS NOT NULL
   OR email_primary IS NOT NULL;

UPDATE customers
SET first_name = NULL,
    last_name = NULL,
    email_primary = NULL,
    email_secondary = NULL,
    phone_primary = NULL,
    phone_secondary = NULL
WHERE external_owner_id = '<EXTERNAL_OWNER_ID>'; 

SELECT 
    COUNT(*) AS total,
    SUM(first_name IS NOT NULL) AS first_name_not_null,
    SUM(last_name IS NOT NULL) AS last_name_not_null,
    SUM(email_primary IS NOT NULL) AS email_primary_not_null,
    SUM(email_secondary IS NOT NULL) AS email_secondary_not_null,
    SUM(phone_primary IS NOT NULL) AS phone_primary_not_null,
    SUM(phone_secondary IS NOT NULL) AS phone_secondary_not_null
FROM customers;

SELECT customer_id, external_owner_id, first_name, last_name, email_primary
FROM customers
WHERE external_owner_id = '69247e727f9fef26201db7c3';

UPDATE customers
SET first_name = NULL,
    last_name = NULL,
    email_primary = NULL,
    email_secondary = NULL,
    phone_primary = NULL,
    phone_secondary = NULL
WHERE customer_id = 145;

SELECT ROW_COUNT() AS filas_actualizadas;

UPDATE customers
SET first_name = NULL,
    last_name = NULL,
    email_primary = NULL,
    email_secondary = NULL,
    phone_primary = NULL,
    phone_secondary = NULL
WHERE TRIM(external_owner_id) = '69247e727f9fef26201db7c3';

SELECT ROW_COUNT() AS filas_actualizadas;

SELECT customer_id, external_owner_id,
       first_name IS NOT NULL AS fn,
       last_name IS NOT NULL AS ln,
       email_primary IS NOT NULL AS em
FROM customers
WHERE first_name IS NOT NULL
   OR last_name IS NOT NULL
   OR email_primary IS NOT NULL;
   
SELECT *
FROM customers
WHERE customer_id = 145;

SELECT city, COUNT(*)
FROM customers
GROUP BY city
ORDER BY COUNT(*) DESC;

SELECT COUNT(*) AS total FROM customers;

SELECT COUNT(*) AS with_external
FROM customers
WHERE external_owner_id IS NOT NULL;

SELECT COUNT(*) AS without_external
FROM customers
WHERE external_owner_id IS NULL;

SELECT COUNT(*) AS monthly
FROM customers
WHERE external_owner_id LIKE 'MONTHLY_CUST_%';

SELECT
  SUM(first_name IS NOT NULL) AS first_name_not_null,
  SUM(last_name IS NOT NULL) AS last_name_not_null,
  SUM(email_primary IS NOT NULL) AS email_primary_not_null,
  SUM(phone_primary IS NOT NULL) AS phone_primary_not_null
FROM customers







