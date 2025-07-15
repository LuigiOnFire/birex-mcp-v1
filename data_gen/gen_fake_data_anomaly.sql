INSERT INTO anomaly_data (time, process_id, anomaly_detected)
SELECT
  g1.time,
  r.process_id,
  (random() < r.failure_rate) AS anomaly_detected  
FROM generate_series(now() - interval '24 hour', now(), interval '5 minute') AS g1(time)
JOIN (
  VALUES
    (1111, 0.0),  -- no failures
    (1112, 0.01),  -- 1% failure rate
    (1113, 0.05),  -- 5% failure rate
    (1114, 0.10)   -- 10% failure rate
) AS r(process_id, failure_rate)
ON true;
