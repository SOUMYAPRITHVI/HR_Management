DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'employees') THEN
        CREATE TABLE employees  (
                employee_id SERIAL PRIMARY KEY,
                fname VARCHAR(50) NOT NULL,
                lname VARCHAR(50) NOT NULL,
                title VARCHAR(100),
                email VARCHAR(120) NOT NULL,
                phone VARCHAR(50)
            );
    END IF;
END $$;
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'leaves') THEN
        CREATE TABLE leaves (
            id SERIAL PRIMARY KEY,
            date DATE,
            employee  INTEGER REFERENCES employees(employee_id),
            reason VARCHAR(200),
            UNIQUE (employee, date) -- An employee can take only one leave on a given day
            );
     END IF;
END $$;