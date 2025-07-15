INSERT INTO process_uptime (time, process_id, status)
SELECT
  time,
  process_id,
  (random() < 0.95) AS status  
FROM generate_series(now() - interval '24 hour', now(), interval '5 minute') AS g1(time), generate_series(1111,1114,1) AS g2(process_id);