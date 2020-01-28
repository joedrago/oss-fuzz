#!/usr/bin/python3
"""asd."""
# TODO: break up this into pieces that can be re-used.
from google.cloud import bigquery

# Construct a BigQuery client object.
client = bigquery.Client(project='clusterfuzz-external')

query = """
    CREATE TEMP FUNCTION
  TimeIsRight(timestamp FLOAT64) AS ( timestamp >= UNIX_SECONDS(TIMESTAMP("2020-01-14 00:00:00"))
    AND timestamp < UNIX_SECONDS(TIMESTAMP("2020-01-27 00:00:00")) );
SELECT
  fuzz_target,
  edges_without_strategy,
  edges_with_strategy,
  edges_with_strategy - edges_without_strategy AS edge_diff,
  features_without_strategy,
  features_with_strategy,
  runs_without_strategy,
  runs_with_strategy
FROM (
    # Only the fuzzers that used the strategy in the given timeframe.
    # Important for strategies that are not applicable to all fuzzers.
  SELECT
    fuzzer AS fuzz_target
  FROM
    `libFuzzer_stats.TestcaseRun`
  WHERE
    # Important to check that the strategy is ON here.
    strategy_dataflow_tracing = 1
    AND TimeIsRight(timestamp)
  GROUP BY
    fuzzer ) fuzzers_affected
JOIN (
  SELECT
    fuzzer,
    AVG(new_edges) AS edges_without_strategy,
    AVG(new_features) AS features_without_strategy,
    COUNT(1) AS runs_without_strategy,
  FROM
    `libFuzzer_stats.TestcaseRun`
  WHERE
    # Check that the strategy is OFF below.
    (strategy_dataflow_tracing = 0
      OR strategy_dataflow_tracing IS NULL)
    AND TimeIsRight(timestamp)
  GROUP BY
    fuzzer ) without_strategy
ON
  fuzzers_affected.fuzz_target = without_strategy.fuzzer
JOIN (
  SELECT
    fuzzer,
    AVG(new_edges) AS edges_with_strategy,
    AVG(new_features) AS features_with_strategy,
    COUNT(1) AS runs_with_strategy,
  FROM
    `libFuzzer_stats.TestcaseRun`
  WHERE
    # Check that the strategy is ON below.
    strategy_dataflow_tracing = 1
    AND TimeIsRight(timestamp)
  GROUP BY
    fuzzer ) with_strategy
ON
  fuzzers_affected.fuzz_target = with_strategy.fuzzer
ORDER BY
  fuzz_target
"""
query_job = client.query(query)  # Make an API request.

print("The query data:")
for row in query_job:
  # Row values can be accessed by field name or index.
  print(row)
