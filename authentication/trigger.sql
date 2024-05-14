-- Pengecekan Email Pengguna
CREATE OR REPLACE FUNCTION check_email_exists()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM AKUN WHERE email = NEW.email) THEN
        RAISE EXCEPTION 'Email already exists!';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_email_exists
BEFORE INSERT OR UPDATE ON AKUN
FOR EACH ROW
EXECUTE FUNCTION check_email_exists();

-- Pengecekan Email Label
CREATE OR REPLACE FUNCTION check_email_label_exists()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM LABEL WHERE email = NEW.email) THEN
        RAISE EXCEPTION 'Email already exists!';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_email_label_exists
BEFORE INSERT OR UPDATE ON LABEL
FOR EACH ROW
EXECUTE FUNCTION check_email_label_exists();

-- Pendaftaran Pengguna Baru
CREATE OR REPLACE FUNCTION insert_nonpremium()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO nonpremium (email) VALUES (NEW.email);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER akun_insert_trigger
AFTER INSERT ON AKUN
FOR EACH ROW
EXECUTE FUNCTION insert_nonpremium();

-- Memeriksa status langganan Pengguna
CREATE OR REPLACE PROCEDURE check_premium_membership(email_akun VARCHAR(50))
AS $$
BEGIN
    -- Cek apakah email tersebut merupakan akun premium
    IF EXISTS (SELECT 1 FROM PREMIUM WHERE email = email_akun) THEN
        -- Cek apakah akun premium tersebut memiliki transaksi dengan timestamp_berakhir melewati timestamp saat ini
        IF NOT EXISTS (
            SELECT 1 FROM TRANSACTION 
            WHERE email = email_akun 
            AND timestamp_berakhir > CURRENT_TIMESTAMP
        ) THEN
            -- Jika tidak ada transaksi aktif, hubah status premium menjadi nonpremium
            DELETE FROM PREMIUM WHERE email = email_akun;
            INSERT INTO NONPREMIUM (email) VALUES (email_akun);
        END IF;
    END IF;
END;
$$ LANGUAGE plpgsql;

