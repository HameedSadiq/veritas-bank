-- ==========================================
-- VERITAS MICROFINANCE BANK
-- Oracle Database Schema
-- ==========================================

-- Drop existing objects (if re-running)
DROP TABLE audit_logs CASCADE CONSTRAINTS;
DROP TABLE transfers CASCADE CONSTRAINTS;
DROP TABLE transactions CASCADE CONSTRAINTS;
DROP TABLE accounts CASCADE CONSTRAINTS;
DROP TABLE customers CASCADE CONSTRAINTS;
DROP TABLE bank_staff CASCADE CONSTRAINTS;
DROP TABLE branches CASCADE CONSTRAINTS;

DROP SEQUENCE cust_seq;
DROP SEQUENCE acc_seq;
DROP SEQUENCE trans_seq;
DROP SEQUENCE transfer_seq;
DROP SEQUENCE audit_seq;
DROP SEQUENCE staff_seq;
DROP SEQUENCE branch_seq;

-- ==========================================
-- SEQUENCES
-- ==========================================
CREATE SEQUENCE branch_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE staff_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE cust_seq START WITH 1000 INCREMENT BY 1;
CREATE SEQUENCE acc_seq START WITH 2000 INCREMENT BY 1;
CREATE SEQUENCE trans_seq START WITH 5000 INCREMENT BY 1;
CREATE SEQUENCE transfer_seq START WITH 7000 INCREMENT BY 1;
CREATE SEQUENCE audit_seq START WITH 10000 INCREMENT BY 1;

-- ==========================================
-- BRANCHES TABLE
-- ==========================================
CREATE TABLE branches (
    branch_id NUMBER PRIMARY KEY,
    branch_name VARCHAR2(100) NOT NULL UNIQUE,
    branch_location VARCHAR2(150) NOT NULL,
    branch_code VARCHAR2(10) NOT NULL UNIQUE,
    created_date TIMESTAMP DEFAULT SYSDATE
);

-- ==========================================
-- BANK STAFF TABLE
-- ==========================================
CREATE TABLE bank_staff (
    staff_id NUMBER PRIMARY KEY,
    first_name VARCHAR2(50) NOT NULL,
    last_name VARCHAR2(50) NOT NULL,
    email VARCHAR2(100) NOT NULL UNIQUE,
    phone VARCHAR2(15),
    position VARCHAR2(50) NOT NULL,
    branch_id NUMBER NOT NULL,
    salary NUMBER(10,2),
    hire_date TIMESTAMP DEFAULT SYSDATE,
    status VARCHAR2(20) DEFAULT 'ACTIVE',
    CONSTRAINT fk_staff_branch FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

-- ==========================================
-- CUSTOMERS TABLE
-- ==========================================
CREATE TABLE customers (
    customer_id NUMBER PRIMARY KEY,
    first_name VARCHAR2(50) NOT NULL,
    last_name VARCHAR2(50) NOT NULL,
    email VARCHAR2(100) NOT NULL UNIQUE,
    phone VARCHAR2(15) NOT NULL,
    address VARCHAR2(200) NOT NULL,
    id_number VARCHAR2(20) NOT NULL UNIQUE,
    date_of_birth DATE NOT NULL,
    registration_date TIMESTAMP DEFAULT SYSDATE,
    status VARCHAR2(20) DEFAULT 'ACTIVE',
    CONSTRAINT chk_dob CHECK (date_of_birth <= TRUNC(SYSDATE) - 365)
);

-- ==========================================
-- ACCOUNTS TABLE
-- ==========================================
CREATE TABLE accounts (
    account_id NUMBER PRIMARY KEY,
    customer_id NUMBER NOT NULL,
    account_type VARCHAR2(20) NOT NULL,
    account_number VARCHAR2(20) NOT NULL UNIQUE,
    balance NUMBER(15,2) NOT NULL DEFAULT 0,
    interest_rate NUMBER(5,3) DEFAULT 0,
    creation_date TIMESTAMP DEFAULT SYSDATE,
    last_modified TIMESTAMP DEFAULT SYSDATE,
    status VARCHAR2(20) DEFAULT 'ACTIVE',
    branch_id NUMBER,
    CONSTRAINT fk_acc_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_acc_branch FOREIGN KEY (branch_id) REFERENCES branches(branch_id),
    CONSTRAINT chk_balance CHECK (balance >= 0),
    CONSTRAINT chk_account_type CHECK (account_type IN ('SAVINGS', 'CURRENT', 'STUDENT'))
);

CREATE INDEX idx_accounts_customer ON accounts(customer_id);
CREATE INDEX idx_accounts_number ON accounts(account_number);

-- ==========================================
-- TRANSACTIONS TABLE
-- ==========================================
CREATE TABLE transactions (
    transaction_id NUMBER PRIMARY KEY,
    account_id NUMBER NOT NULL,
    transaction_type VARCHAR2(20) NOT NULL,
    amount NUMBER(15,2) NOT NULL,
    transaction_date TIMESTAMP DEFAULT SYSDATE,
    description VARCHAR2(200),
    balance_after NUMBER(15,2),
    status VARCHAR2(20) DEFAULT 'COMPLETED',
    CONSTRAINT fk_trans_account FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    CONSTRAINT chk_transaction_type CHECK (transaction_type IN ('DEPOSIT', 'WITHDRAWAL', 'TRANSFER_OUT', 'TRANSFER_IN')),
    CONSTRAINT chk_trans_amount CHECK (amount > 0)
);

CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);

-- ==========================================
-- TRANSFERS TABLE
-- ==========================================
CREATE TABLE transfers (
    transfer_id NUMBER PRIMARY KEY,
    from_account_id NUMBER NOT NULL,
    to_account_id NUMBER NOT NULL,
    amount NUMBER(15,2) NOT NULL,
    transfer_date TIMESTAMP DEFAULT SYSDATE,
    transfer_type VARCHAR2(20) DEFAULT 'INTERNAL',
    status VARCHAR2(20) DEFAULT 'COMPLETED',
    description VARCHAR2(200),
    CONSTRAINT fk_transfer_from FOREIGN KEY (from_account_id) REFERENCES accounts(account_id),
    CONSTRAINT fk_transfer_to FOREIGN KEY (to_account_id) REFERENCES accounts(account_id),
    CONSTRAINT chk_transfer_amount CHECK (amount > 0)
);

CREATE INDEX idx_transfers_from ON transfers(from_account_id);
CREATE INDEX idx_transfers_to ON transfers(to_account_id);

-- ==========================================
-- AUDIT LOGS TABLE
-- ==========================================
CREATE TABLE audit_logs (
    audit_id NUMBER PRIMARY KEY,
    account_id NUMBER,
    customer_id NUMBER,
    action_type VARCHAR2(50) NOT NULL,
    action_description VARCHAR2(500) NOT NULL,
    old_value VARCHAR2(500),
    new_value VARCHAR2(500),
    performed_by NUMBER,
    action_date TIMESTAMP DEFAULT SYSDATE,
    ip_address VARCHAR2(45),
    CONSTRAINT fk_audit_account FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    CONSTRAINT fk_audit_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_audit_staff FOREIGN KEY (performed_by) REFERENCES bank_staff(staff_id)
);

CREATE INDEX idx_audit_date ON audit_logs(action_date);
CREATE INDEX idx_audit_account ON audit_logs(account_id);

-- ==========================================
-- TRIGGERS
-- ==========================================

CREATE OR REPLACE TRIGGER trg_update_account_modified
BEFORE UPDATE ON accounts
FOR EACH ROW
BEGIN
    :NEW.last_modified := SYSDATE;
END;
/

CREATE OR REPLACE TRIGGER trg_audit_balance_change
AFTER UPDATE ON accounts
FOR EACH ROW
WHEN (NEW.balance != OLD.balance)
BEGIN
    INSERT INTO audit_logs (
        audit_id, account_id, action_type, 
        action_description, old_value, new_value, action_date
    ) VALUES (
        audit_seq.NEXTVAL, :NEW.account_id, 'BALANCE_CHANGE',
        'Account balance modified', 
        TO_CHAR(:OLD.balance), TO_CHAR(:NEW.balance), SYSDATE
    );
END;
/

CREATE OR REPLACE TRIGGER trg_prevent_account_delete
BEFORE DELETE ON accounts
FOR EACH ROW
DECLARE
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count FROM transactions WHERE account_id = :OLD.account_id;
    IF v_count > 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Cannot delete account with existing transactions');
    END IF;
END;
/

-- ==========================================
-- STORED PROCEDURES
-- ==========================================

CREATE OR REPLACE PROCEDURE proc_deposit (
    p_account_id IN NUMBER,
    p_amount IN NUMBER,
    p_description IN VARCHAR2 DEFAULT 'Deposit',
    p_result OUT VARCHAR2
) IS
    v_current_balance NUMBER;
    v_account_exists NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_account_exists FROM accounts WHERE account_id = p_account_id AND status = 'ACTIVE';
    
    IF v_account_exists = 0 THEN
        p_result := 'ERROR: Account not found or inactive';
        RETURN;
    END IF;
    
    IF p_amount <= 0 THEN
        p_result := 'ERROR: Amount must be positive';
        RETURN;
    END IF;
    
    SELECT balance INTO v_current_balance FROM accounts WHERE account_id = p_account_id;
    
    UPDATE accounts SET balance = balance + p_amount WHERE account_id = p_account_id;
    
    INSERT INTO transactions (
        transaction_id, account_id, transaction_type, amount, 
        description, balance_after, status
    ) VALUES (
        trans_seq.NEXTVAL, p_account_id, 'DEPOSIT', p_amount,
        p_description, v_current_balance + p_amount, 'COMPLETED'
    );
    
    COMMIT;
    p_result := 'SUCCESS: Deposit completed. New Balance: ' || (v_current_balance + p_amount);
    
EXCEPTION WHEN OTHERS THEN
    ROLLBACK;
    p_result := 'ERROR: ' || SQLERRM;
END proc_deposit;
/

CREATE OR REPLACE PROCEDURE proc_withdraw (
    p_account_id IN NUMBER,
    p_amount IN NUMBER,
    p_description IN VARCHAR2 DEFAULT 'Withdrawal',
    p_result OUT VARCHAR2
) IS
    v_current_balance NUMBER;
    v_account_exists NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_account_exists FROM accounts WHERE account_id = p_account_id AND status = 'ACTIVE';
    
    IF v_account_exists = 0 THEN
        p_result := 'ERROR: Account not found or inactive';
        RETURN;
    END IF;
    
    IF p_amount <= 0 THEN
        p_result := 'ERROR: Amount must be positive';
        RETURN;
    END IF;
    
    SELECT balance INTO v_current_balance FROM accounts WHERE account_id = p_account_id;
    
    IF v_current_balance < p_amount THEN
        p_result := 'ERROR: Insufficient funds. Current Balance: ' || v_current_balance;
        RETURN;
    END IF;
    
    UPDATE accounts SET balance = balance - p_amount WHERE account_id = p_account_id;
    
    INSERT INTO transactions (
        transaction_id, account_id, transaction_type, amount,
        description, balance_after, status
    ) VALUES (
        trans_seq.NEXTVAL, p_account_id, 'WITHDRAWAL', p_amount,
        p_description, v_current_balance - p_amount, 'COMPLETED'
    );
    
    COMMIT;
    p_result := 'SUCCESS: Withdrawal completed. New Balance: ' || (v_current_balance - p_amount);
    
EXCEPTION WHEN OTHERS THEN
    ROLLBACK;
    p_result := 'ERROR: ' || SQLERRM;
END proc_withdraw;
/

CREATE OR REPLACE PROCEDURE proc_transfer (
    p_from_account_id IN NUMBER,
    p_to_account_id IN NUMBER,
    p_amount IN NUMBER,
    p_description IN VARCHAR2 DEFAULT 'Transfer',
    p_result OUT VARCHAR2
) IS
    v_from_balance NUMBER;
    v_to_balance NUMBER;
    v_both_exist NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_both_exist FROM accounts 
    WHERE (account_id = p_from_account_id OR account_id = p_to_account_id) 
    AND status = 'ACTIVE';
    
    IF v_both_exist < 2 THEN
        p_result := 'ERROR: One or both accounts not found or inactive';
        RETURN;
    END IF;
    
    IF p_amount <= 0 THEN
        p_result := 'ERROR: Amount must be positive';
        RETURN;
    END IF;
    
    SELECT balance INTO v_from_balance FROM accounts WHERE account_id = p_from_account_id;
    SELECT balance INTO v_to_balance FROM accounts WHERE account_id = p_to_account_id;
    
    IF v_from_balance < p_amount THEN
        p_result := 'ERROR: Insufficient funds in source account';
        RETURN;
    END IF;
    
    UPDATE accounts SET balance = balance - p_amount WHERE account_id = p_from_account_id;
    UPDATE accounts SET balance = balance + p_amount WHERE account_id = p_to_account_id;
    
    INSERT INTO transfers (
        transfer_id, from_account_id, to_account_id, amount,
        description, status
    ) VALUES (
        transfer_seq.NEXTVAL, p_from_account_id, p_to_account_id,
        p_amount, p_description, 'COMPLETED'
    );
    
    INSERT INTO transactions (
        transaction_id, account_id, transaction_type, amount,
        description, balance_after, status
    ) VALUES (
        trans_seq.NEXTVAL, p_from_account_id, 'TRANSFER_OUT', p_amount,
        p_description, v_from_balance - p_amount, 'COMPLETED'
    );
    
    INSERT INTO transactions (
        transaction_id, account_id, transaction_type, amount,
        description, balance_after, status
    ) VALUES (
        trans_seq.NEXTVAL, p_to_account_id, 'TRANSFER_IN', p_amount,
        p_description, v_to_balance + p_amount, 'COMPLETED'
    );
    
    COMMIT;
    p_result := 'SUCCESS: Transfer completed';
    
EXCEPTION WHEN OTHERS THEN
    ROLLBACK;
    p_result := 'ERROR: ' || SQLERRM;
END proc_transfer;
/

-- ==========================================
-- SAMPLE DATA
-- ==========================================

INSERT INTO branches (branch_id, branch_name, branch_location, branch_code)
VALUES (branch_seq.NEXTVAL, 'Main Branch', 'City Center', 'MB001');

INSERT INTO branches (branch_id, branch_name, branch_location, branch_code)
VALUES (branch_seq.NEXTVAL, 'Student Branch', 'University Campus', 'SB001');

INSERT INTO customers (
    customer_id, first_name, last_name, email, phone, 
    address, id_number, date_of_birth
) VALUES (
    cust_seq.NEXTVAL, 'John', 'Doe', 'john@university.edu', 
    '0700000001', '123 Main Street', 'ID123456', TO_DATE('1995-05-15', 'YYYY-MM-DD')
);

INSERT INTO accounts (
    account_id, customer_id, account_type, account_number, balance, branch_id, status
) VALUES (
    acc_seq.NEXTVAL, 1000, 'STUDENT', 'ACC20001000', 5000, 2, 'ACTIVE'
);

COMMIT;