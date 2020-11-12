CREATE MATERIALIZED VIEW aw.afkwindow AS
SELECT C.id,
       C.hostname,
       C.bucket_id,
       case when A.timestamp > C.timestamp then C.timestamp else a.timestamp end                         AS timestamp,
       extract(epoch from (case
                               when (C.timestamp + C.duration * interval '1 second' >
                                     A.timestamp + A.duration * interval '1 second')
                                   then (A.timestamp + A.duration * interval '1 second')
                               else (C.timestamp + C.duration * interval '1 second') end) - C.timestamp) as duration,
       C.app,
       C.title
FROM aw.afkstatus A
         INNER JOIN aw.currentwindow C ON
        (A.timestamp, A.timestamp + A.duration * interval '1 second')
        overlaps
        (C.timestamp, C.timestamp + C.duration * interval '1 second')
ORDER BY timestamp ASC;
