CREATE TABLE assigned_merchants (
    merchant_id SERIAL PRIMARY KEY,
    merchant_name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    health_status VARCHAR(50),
    last_contact DATE,
    priority INT,
    assigned_activity TEXT,
    assigned_date DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE merchant_profiles (
    merchant_id SERIAL PRIMARY KEY,
    merchant_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(100),
    location VARCHAR(255),
    contact_person VARCHAR(255),
    phone VARCHAR(15),
    health_status VARCHAR(50),
    last_sales DATE,
    monthly_target NUMERIC(10, 2),
    onboarding_date DATE
);
