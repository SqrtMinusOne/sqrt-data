# [[file:../../../org/mpd.org::*Postprocessing][Postprocessing:2]]
from sqrt_data.api import DBConn

__all__ = ['create_views']

MPD_VIEW = """
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
"""

def create_views():
    DBConn()
    DBConn.engine.execute(MPD_VIEW)
# Postprocessing:2 ends here