drop view if exists "google"."SongListened";
create view "google"."SongListened" as
select
    ML.artist as artist,
    ML.title as title,
    ML.time as time,
    A.duration::float4 / (1000 * 60) as duration,
    A.album as album
from "google"."MusicListened" ML LEFT JOIN "google"."AlbumSong" A ON ML.song_id = A.id