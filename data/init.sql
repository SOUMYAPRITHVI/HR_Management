DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'employees') THEN
        CREATE TABLE employees  (
                employee_id SERIAL PRIMARY KEY,
                fname VARCHAR(50) NOT NULL,
                lname VARCHAR(50) NOT NULL,
                email VARCHAR(120) NOT NULL,
                phone VARCHAR(50),
                title_id INTEGER REFERENCES designation(designation_id) ON DELETE CASCADE
            );
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'leaves') THEN
        CREATE TABLE leaves (
            id SERIAL PRIMARY KEY,
            date DATE,
            employee  INTEGER REFERENCES employees(employee_id) ON DELETE CASCADE,
            reason VARCHAR(200),
            UNIQUE (employee, date) -- An employee can take only one leave on a given day
            );
     END IF;
END $$;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'designation') THEN
        CREATE TABLE designation (
            designation_id SERIAL PRIMARY KEY,
            designation_name VARCHAR(100) NOT NULL,
            percentage_of_employees  INTEGER NOT NULL,
            total_no_of_leaves INTEGER NOT NULL
            );
     END IF;
END $$;