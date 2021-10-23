# [[file:../../../org/aw.org::*Postprocessing][Postprocessing:5]]
from sqrt_data.api import settings, DBConn

__all__ = [
    'postprocessing_set_sql', 'postprocessing_init', 'postprocessing_dispatch'
]

SQL = """
drop procedure if exists aw.init_postprocessing();
create procedure aw.init_postprocessing()
    language plpgsql as
$$
begin
    drop table if exists aw.notafkwindow;
    drop table if exists aw.notafktab;
    drop table if exists aw._notafkwindow_meta cascade;
    create table aw.notafkwindow (like aw.currentwindow including all);
    create table aw.notafktab (like aw.webtab including all);
    create table aw._notafkwindow_meta (
        date date primary key,
        count int8
    );

    CREATE OR REPLACE VIEW aw._notafkwindow_meta_diff AS
    WITH current_meta AS (
        select date(timestamp) date, count(*) count
        FROM aw.currentwindow
        GROUP BY date(timestamp)
        ORDER BY date ASC
    )
    SELECT CM.date
    FROM current_meta CM
             LEFT JOIN aw._notafkwindow_meta OM ON CM.date = OM.date
    WHERE CM.count != OM.count OR OM.count IS NULL;
end;
$$;
drop function if exists aw.is_afk;
create function aw.is_afk(status bool, duration float, app text, title text) returns bool
    language plpgsql as
$$
begin
    return status = true
        OR (status = false AND duration < current_setting('aw.skip_afk_interval')::int AND
            (app ~ current_setting('aw.skip_afk_apps') OR title ~ current_setting('aw.skip_afk_titles')));
end;
$$;
drop function if exists aw.get_notafkwindow;
create function aw.get_notafkwindow(start_date timestamp, end_date timestamp)
    returns table
            (
                like aw.currentwindow
            )
    language plpgsql
AS
$$
begin
    RETURN QUERY
        WITH A AS (SELECT * FROM aw.afkstatus WHERE timestamp BETWEEN start_date AND end_date),
             C AS (SELECT * FROM aw.currentwindow WHERE timestamp BETWEEN start_date AND end_date)
        SELECT concat('afkw-', substring(C.id from '[0-9]+$'), '-', substring(A.id from '[0-9]+$'))::varchar(256) id,
               C.bucket_id,
               C.hostname,
               C.location,
               case
                   when A.timestamp > C.timestamp then A.timestamp
                   else C.timestamp end AS                                                                        timestamp,
               extract(epoch from
                       least(C.timestamp + C.duration * interval '1 second',
                             A.timestamp + A.duration * interval '1 second') -
                       greatest(A.timestamp, C.timestamp))                                                        duration,
               case
                   when aw.is_afk(A.status, A.duration, app, title) then C.app
                   else 'AFK' end       as                                                                        app,
               case
                   when aw.is_afk(A.status, A.duration, app, title) then C.title
                   else 'AFK' end       as                                                                        title
        FROM A
                 INNER JOIN C ON
                ((A.timestamp, A.timestamp + A.duration * interval '1 second')
                    overlaps
                 (C.timestamp, C.timestamp + C.duration * interval '1 second')) AND A.hostname = C.hostname
        ORDER BY timestamp DESC;
end;
$$;
drop procedure if exists aw.postprocess_notafkwindow;
create procedure aw.postprocess_notafkwindow()
    language plpgsql AS
$$
DECLARE
    date date;
begin
    FOR date IN SELECT * FROM aw._notafkwindow_meta_diff
        LOOP
            DELETE FROM aw.notafkwindow WHERE date(timestamp) = date;
            INSERT INTO aw.notafkwindow
            SELECT *
            FROM aw.get_notafkwindow(date, date + interval '1 day');
        end loop;
    DELETE FROM aw._notafkwindow_meta;
    INSERT INTO aw._notafkwindow_meta
    select date(timestamp) date, count(*) count
    FROM aw.currentwindow
    GROUP BY date(timestamp)
    ORDER BY date;
end;
$$;
"""


def update_settings(db):
    db.execute(
        f"""
    SELECT set_config('aw.skip_afk_interval', '{settings['aw']['skip_afk_interval']}', false);
    SELECT set_config('aw.skip_afk_apps', '{settings['aw']['skip_afk_apps']}', false);
    SELECT set_config('aw.skip_afk_titles', '{settings['aw']['skip_afk_titles']}', false);
    """
    )


def postprocessing_set_sql():
    DBConn()
    with DBConn.get_session() as db:
        update_settings(db)
        db.execute(SQL)
        db.commit()

def postprocessing_init():
    DBConn()
    with DBConn.get_session() as db:
        db.execute("CALL aw.init_postprocessing();")
        db.commit()

def postprocessing_dispatch():
    DBConn()
    with DBConn.get_session() as db:
        update_settings(db)
        db.execute("CALL aw.postprocess_notafkwindow();")
        db.commit()
# Postprocessing:5 ends here
