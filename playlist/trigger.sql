-- Memperbarui Atribut Durasi dan Jumlah Lagu
CREATE OR REPLACE FUNCTION update_user_playlist_on_insert() RETURNS TRIGGER AS $$
DECLARE
    song_duration INT;
BEGIN
    -- Get the duration of the song being added
    SELECT durasi INTO song_duration
    FROM KONTEN
    WHERE id = NEW.id_song;

    -- Update the USER_PLAYLIST table
    UPDATE USER_PLAYLIST
    SET jumlah_lagu = jumlah_lagu + 1,
        total_durasi = total_durasi + song_duration
    WHERE id_playlist = NEW.id_playlist;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_insert_playlist_song
AFTER INSERT ON PLAYLIST_SONG
FOR EACH ROW
EXECUTE FUNCTION update_user_playlist_on_insert();

CREATE OR REPLACE FUNCTION update_user_playlist_on_delete() RETURNS TRIGGER AS $$
DECLARE
    song_duration INT;
BEGIN
    -- Get the duration of the song being removed
    SELECT durasi INTO song_duration
    FROM KONTEN
    WHERE id = OLD.id_song;

    -- Update the USER_PLAYLIST table
    UPDATE USER_PLAYLIST
    SET jumlah_lagu = jumlah_lagu - 1,
        total_durasi = total_durasi - song_duration
    WHERE id_playlist = OLD.id_playlist;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_delete_playlist_song
AFTER DELETE ON PLAYLIST_SONG
FOR EACH ROW
EXECUTE FUNCTION update_user_playlist_on_delete();

-- Memeriksa Lagu Ganda pada Playlist
CREATE OR REPLACE FUNCTION check_duplicate_song() RETURNS TRIGGER AS $$
BEGIN
    -- Check if the song already exists in the playlist
    IF EXISTS (
        SELECT 1
        FROM PLAYLIST_SONG
        WHERE id_playlist = NEW.id_playlist
          AND id_song = NEW.id_song
    ) THEN
        -- Raise an exception if the song is already in the playlist
        RAISE EXCEPTION 'This song is already in the playlist!';
    END IF;

    -- If the song does not exist in the playlist, allow the insert
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_insert_playlist_song
BEFORE INSERT ON PLAYLIST_SONG
FOR EACH ROW
EXECUTE FUNCTION check_duplicate_song();

-- Memeriksa Lagu Ganda pada Downloaded Song
CREATE OR REPLACE FUNCTION check_song_download_existence() RETURNS TRIGGER AS $$
BEGIN
    -- Check if the song has already been downloaded by the user
    IF EXISTS (SELECT 1 FROM DOWNLOADED_SONG WHERE id_song = NEW.id_song AND email_downloader = NEW.email_downloader) THEN
        RAISE EXCEPTION 'You have already downloaded this song!';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_insert_downloaded_song
BEFORE INSERT ON DOWNLOADED_SONG
FOR EACH ROW
EXECUTE FUNCTION check_song_download_existence();
