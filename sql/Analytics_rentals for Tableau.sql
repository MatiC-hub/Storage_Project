-- Analytics_rentals for Tableau
ALTER TABLE units
ADD COLUMN size_m2 DECIMAL(10,2)
GENERATED ALWAYS AS (width_m * length_m) STORED;

CREATE OR REPLACE VIEW analytics_rentals AS
SELECT
    -- UNIT INFO
    u.unit_id,
    u.unit_number,
    u.unit_type,
    u.unit_state,
    u.size_m2,

    -- CUSTOMER INFO
    c.customer_id,
    c.customer_status,
    c.nationality,
    c.country,
    c.province,
    c.city,

    -- RENTAL INFO
    ur.unit_rental_id,
    ur.billing_type,
    ur.rental_state,
    ur.move_in_date,
    ur.move_out_date,

    -- DURATION CALCULATION
    DATEDIFF(
        COALESCE(ur.move_out_date, CURDATE()),
        ur.move_in_date
    ) AS duration_days,

    -- ACTIVE FLAG
    CASE 
        WHEN ur.rental_state = 'occupied' THEN 1
        ELSE 0
    END AS is_active_rental,

    -- MULTI UNIT ANALYSIS
    COUNT(ur.unit_id) OVER (PARTITION BY ur.customer_id) AS customer_total_units,

    -- TOTAL AREA PER CUSTOMER
    SUM(u.size_m2) OVER (PARTITION BY ur.customer_id) AS total_m2_per_customer,

    -- MULTI UNIT FLAG
    CASE
        WHEN COUNT(ur.unit_id) OVER (PARTITION BY ur.customer_id) > 1 THEN 1
        ELSE 0
    END AS multi_unit_flag

FROM unit_rentals ur
JOIN units u ON u.unit_id = ur.unit_id
LEFT JOIN customers c ON c.customer_id = ur.customer_id;

SELECT * FROM analytics_rentals
LIMIT 10;

SELECT COUNT(*) FROM analytics_rentals;

SELECT * FROM analytics_rentals LIMIT 5;