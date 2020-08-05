drop view if exists mpd."MpdSongListened";
create view mpd."MpdSongListened" as
select
    S.title title,
    S.album album,
    S.album_artist artist,
    S.duration::float4 / 60 duration,
    S.year "year",
    L.time "time"
from mpd."SongListened" L
left join mpd."MpdSong" S ON L.song_id = S.id
order by time asc;

drop function if exists fixSongTitle;

create function fixSongTitle(title text)
    returns text language PLPGSQL as $$
begin
    title = regexp_replace(title, ':.*$', '');
    return title;
end; $$;

start transaction;
update mpd."MpdSong"
    set title = fixSongTitle(title);

commit;