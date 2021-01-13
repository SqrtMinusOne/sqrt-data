drop materialized view if exists aw.afkwindow;
CREATE MATERIALIZED VIEW aw.afkwindow AS
SELECT C.id,
       C.hostname,
       C.bucket_id,
       case when A.timestamp > C.timestamp then A.timestamp else C.timestamp end                     AS timestamp,
       extract(epoch from (case
                               when (C.timestamp + C.duration * interval '1 second' >
                                     A.timestamp + A.duration * interval '1 second')
                                   then (A.timestamp + A.duration * interval '1 second')
                               else (C.timestamp + C.duration * interval '1 second') end) -
                          (case when A.timestamp > C.timestamp then A.timestamp else C.timestamp end)) as duration,
       C.app,
       C.title
FROM aw.afkstatus A
         INNER JOIN aw.currentwindow C ON
        ((A.timestamp, A.timestamp + A.duration * interval '1 second')
            overlaps
         (C.timestamp, C.timestamp + C.duration * interval '1 second')) AND A.hostname = C.hostname
WHERE A.status = 'not-afk'
ORDER BY timestamp ASC;
