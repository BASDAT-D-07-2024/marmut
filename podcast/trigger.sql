-- Nambahin total_play saat user menambahkan lagu ke playlist
CREATE OR REPLACE FUNCTION update_total_play()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE SONG
    SET total_play = total_play + 1
    WHERE id_konten = NEW.id_song;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_total_play
AFTER INSERT ON PLAYLIST_SONG
FOR EACH ROW
EXECUTE FUNCTION update_total_play();

-- Nambahin total_download saat user download lagu
CREATE OR REPLACE FUNCTION update_total_download_on_insert()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE SONG
    SET total_download = total_download + 1
    WHERE id_konten = NEW.id_song;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Ngurangin total_download saat user hapus downloaded_song
CREATE TRIGGER trigger_update_total_download_on_insert
AFTER INSERT ON DOWNLOADED_SONG
FOR EACH ROW
EXECUTE FUNCTION update_total_download_on_insert();

CREATE OR REPLACE FUNCTION update_total_download_on_delete()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE SONG
    SET total_download = total_download - 1
    WHERE id_konten = OLD.id_song;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_total_download_on_delete
AFTER DELETE ON DOWNLOADED_SONG
FOR EACH ROW
EXECUTE FUNCTION update_total_download_on_delete();

