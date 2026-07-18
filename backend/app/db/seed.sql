-- ===============================================
-- Sample e-commerce analytics schema + seed data
-- ===============================================

CREATE TABLE regions (
    region_id   SERIAL PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL
);

CREATE TABLE products (
    product_id   SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category     VARCHAR(50) NOT NULL,
    unit_price   NUMERIC(10,2) NOT NULL
);

CREATE TABLE customers (
    customer_id   SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    region_id     INT REFERENCES regions(region_id)
);

CREATE TABLE orders (
    order_id     SERIAL PRIMARY KEY,
    customer_id  INT REFERENCES customers(customer_id),
    order_date   DATE NOT NULL
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id      INT REFERENCES orders(order_id),
    product_id    INT REFERENCES products(product_id),
    quantity      INT NOT NULL,
    revenue       NUMERIC(12,2) NOT NULL
);

-- ---------- Seed data ----------
INSERT INTO regions (region_name) VALUES
('North America'), ('Europe'), ('Asia Pacific'), ('Latin America');

INSERT INTO products (product_name, category, unit_price) VALUES
('Aurora Wireless Headphones', 'Electronics', 129.99),
('Zenith Running Shoes', 'Apparel', 89.50),
('Lumen Desk Lamp', 'Home', 45.00),
('Nimbus Backpack', 'Accessories', 65.00),
('Solace Yoga Mat', 'Fitness', 32.00),
('Pulse Smartwatch', 'Electronics', 199.99),
('Drift Sunglasses', 'Accessories', 55.00),
('Terra Ceramic Mug Set', 'Home', 24.00),
('Vertex Laptop Stand', 'Electronics', 39.99),
('Ember Scented Candle', 'Home', 18.50);

INSERT INTO customers (customer_name, region_id) VALUES
('Rahul Sharma', 3), ('Emma Wilson', 1), ('Liam Chen', 3),
('Sofia Rossi', 2), ('Carlos Mendes', 4), ('Ananya Iyer', 3),
('James Taylor', 1), ('Mia Dubois', 2), ('Noah Kim', 3),
('Isabella Silva', 4);

-- Generate ~300 randomized orders over the last 6 months
INSERT INTO orders (customer_id, order_date)
SELECT (random() * 9 + 1)::INT,
       CURRENT_DATE - (random() * 180)::INT
FROM generate_series(1, 300);

INSERT INTO order_items (order_id, product_id, quantity, revenue)
SELECT o.order_id,
       p.product_id,
       q.qty,
       ROUND((p.unit_price * q.qty)::NUMERIC, 2)
FROM orders o
JOIN LATERAL (SELECT (random() * 9 + 1)::INT AS product_id) pi ON true
JOIN products p ON p.product_id = pi.product_id
JOIN LATERAL (SELECT (random() * 4 + 1)::INT AS qty) q ON true;

-- ---------- Read-only role for the agent ----------
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'analytics_readonly') THEN
      CREATE ROLE analytics_readonly LOGIN PASSWORD 'readonly_pw';
   END IF;
END
$$;

GRANT CONNECT ON DATABASE analytics TO analytics_readonly;
GRANT USAGE ON SCHEMA public TO analytics_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analytics_readonly;
