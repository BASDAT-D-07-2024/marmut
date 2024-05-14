-- Memperbarui durasi saat Menambahkan atau Menghapus Episode dalam Podcast:
CREATE OR REPLACE FUNCTION update_durasi_konten()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        UPDATE KONTEN
        SET durasi = COALESCE((SELECT SUM(durasi)
                               FROM EPISODE
                               WHERE id_konten_podcast = OLD.id_konten_podcast), 0)
        WHERE id = OLD.id_konten_podcast;
    ELSE
        UPDATE KONTEN
        SET durasi = COALESCE((SELECT SUM(durasi)
                               FROM EPISODE
                               WHERE id_konten_podcast = NEW.id_konten_podcast), 0)
        WHERE id = NEW.id_konten_podcast;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_modify_episode
AFTER INSERT OR UPDATE OR DELETE ON EPISODE
FOR EACH ROW
EXECUTE FUNCTION update_durasi_konten();

-- Memperbarui Atribut Durasi dan Jumlah Lagu
CREATE OR REPLACE FUNCTION update_album()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        UPDATE ALBUM
        SET total_durasi = COALESCE((SELECT SUM(KONTEN.durasi)
                                     FROM SONG
                                     JOIN KONTEN ON SONG.id_konten = KONTEN.id
                                     WHERE SONG.id_album = OLD.id_album), 0),
            jumlah_lagu = COALESCE((SELECT COUNT(*)
                                    FROM SONG
                                    WHERE SONG.id_album = OLD.id_album), 0)
        WHERE id = OLD.id_album;
    ELSE
        UPDATE ALBUM
        SET total_durasi = COALESCE((SELECT SUM(KONTEN.durasi)
                                     FROM SONG
                                     JOIN KONTEN ON SONG.id_konten = KONTEN.id
                                     WHERE SONG.id_album = NEW.id_album), 0),
            jumlah_lagu = COALESCE((SELECT COUNT(*)
                                    FROM SONG
                                    WHERE SONG.id_album = NEW.id_album), 0)
        WHERE id = NEW.id_album;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER after_modify_song
AFTER INSERT OR UPDATE OR DELETE ON SONG
FOR EACH ROW
EXECUTE FUNCTION update_album();