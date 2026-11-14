-- Independently generated example: customers, products, orders and order items.
-- New empty database only; SQLite >= 3.37 and JSON support are required.
-- Money is in integer cents; timestamps are UTC Unix seconds.
-- The caller must stop and ROLLBACK on error. This is not a migration script.
PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL CHECK (length(trim(customer_name)) > 0),
    email TEXT NOT NULL UNIQUE
) STRICT;

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
) STRICT;

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    order_ref TEXT NOT NULL UNIQUE,
    customer_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'paid', 'cancelled')),
    note TEXT NOT NULL DEFAULT '',
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL CHECK (updated_at >= created_at),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    metadata TEXT NOT NULL DEFAULT '{}' CHECK (json_valid(metadata)),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT
) STRICT;

CREATE TABLE order_items (
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE RESTRICT,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
) STRICT, WITHOUT ROWID;

-- Candidate for customer + status filters with deterministic newest-first pages.
CREATE INDEX idx_orders_customer_status_created
ON orders(customer_id, status, created_at DESC, order_id DESC);

-- The composite primary key begins with order_id, not product_id.
CREATE INDEX idx_order_items_product ON order_items(product_id);

COMMIT;
