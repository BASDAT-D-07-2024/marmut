-- Manajemen Langganan Paket
CREATE OR REPLACE FUNCTION check_subscription()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM TRANSACTION
        WHERE email = NEW.email
        AND timestamp_berakhir > NEW.timestamp_dimulai
    ) THEN
        RAISE EXCEPTION 'You have already subscribed!';
    ELSE
        IF EXISTS (
            SELECT 1
            FROM NONPREMIUM
            WHERE email = NEW.email
        ) THEN
            DELETE FROM NONPREMIUM WHERE email = NEW.email;
            INSERT INTO PREMIUM (email) VALUES (NEW.email);
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_subscription_trigger
BEFORE INSERT ON TRANSACTION
FOR EACH ROW
EXECUTE FUNCTION check_subscription();

-- Manajemen Play User Playlist
CREATE OR REPLACE FUNCTION management_play_user_playlist()
RETURNS TRIGGER AS $$
DECLARE
    playlist_id UUID;
    song_id UUID;
BEGIN
    SELECT id_playlist INTO playlist_id
    FROM USER_PLAYLIST
    WHERE id_user_playlist = NEW.id_user_playlist;

    FOR song_id IN
        SELECT id_song FROM PLAYLIST_SONG WHERE id_playlist = playlist_id
    LOOP
        IF NOT EXISTS (
            SELECT 1 FROM AKUN_PLAY_SONG 
            WHERE email_pemain = NEW.email_pemain 
            AND id_song = song_id 
            AND waktu = NEW.waktu
        ) THEN
            -- Jika belum, tambahkan entri baru ke AKUN_PLAY_SONG
            INSERT INTO AKUN_PLAY_SONG (email_pemain, id_song, waktu) 
            VALUES (NEW.email_pemain, song_id, NEW.waktu);
        END IF;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER management_play_user_playlist_trigger
AFTER INSERT ON AKUN_PLAY_USER_PLAYLIST
FOR EACH ROW
EXECUTE FUNCTION management_play_user_playlist();

