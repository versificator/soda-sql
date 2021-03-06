---
layout: default
title: Scan
parent: Documentation
nav_order: 5
---

# Scan

Soda Scan is one of the core concepts of Soda SQL. This section explains what a scan does, how
it works and how you can configure them using 'scan YAML' files.

> Looking for more information on _running_ a scan? Take a look at either
[the CLI]({% link documentation/cli.md %}) or [Orchestrate scans]({% link documentation/orchestrate_scans.md %}) sections.

## Anatomy of a scan

A scan runs within the context of a table and performs the following actions:

* Fetch the column metadata of the table (column name, type and nullable)
* Single aggregation query that computes aggregate metrics for multiple columns like e.g. missing, min, max etc
* For each column
  * One query for distinct_count, unique_count and valid_count
  * One query for mins (list of smallest values)
  * One query for maxs (list of greatest values)
  * One query for frequent values
  * One query for histograms


> Note on performance: we have tuned most column queries by using the same Column Table Expression (CTE).
The goal is to allow some databases, like eg Snowflake, to be able to cache the results, but we didn't see
actual proof of this yet.  If you have knowledge on this, [drop us a line in one of the channels]({% link community.md %}).

## Scan YAML configuration

'Scan YAML' files are used to configure which metrics should be computed and
which tests should be checked. You are free to use any name, but we recommend
naming your Scan YAML files after the tables in your warehouse.

Top level configuration keys:

| Key | Description | Required |
| --- | ----------- | -------- |
| table_name | The table name. | Required |
| metrics | List of default metrics to compute. Column metrics specified here will be computed on each column. | Optional |
| columns | Define validity rules, metrics, [custom SQL Metrics]({% link documentation/sql_metrics.md %}) and tests for specific columns | Optional |
| sql_metrics | A list of [custom SQL Metrics]({% link documentation/sql_metrics.md %}) which don't belong to a specific column | Optional |
| filter | A SQL expression that will be added to query where clause. Uses [Jinja as template language](https://jinja.palletsprojects.com/). Variables can be passed into the scan.  See [Filtering]({% link documentation/filtering.md %}) | Optional |
| mins_maxs_limit | Max number of elements for the mins metric | Optional, default is 5 |
| frequent_values_limit | Max number of elements for the maxs metric | Optional, default is 5 |
| sample_percentage | Adds [sampling](https://docs.snowflake.com/en/sql-reference/constructs/sample.html) to limit the number of rows scanned. Only tested on Postgres | Optional |
| sample_method | For Snowflake, One of { BERNOULLI, ROW, SYSTEM, BLOCK } | Required if sample_percentage is specified |

## Metrics

### Table metrics

| Meric | Description |
| ----- | ------------|
| row_count |  |
| schema |  |

### Column metrics

| Meric | Description |
| ----- | ------------|
| missing_count |  |
| missing_percentage |  |
| values_count |  |
| values_percentage |  |
| valid_count |  |
| valid_percentage |  |
| invalid_count |  |
| invalid_percentage |  |
| min |  |
| max |  |
| avg |  |
| sum |  |
| variance |  |
| stddev |  |
| min_length |  |
| max_length |  |
| avg_length |  |
| distinct |  |
| unique_count |  |
| duplicate_count |  |
| uniqueness |  |
| maxs |  |
| mins |  |
| frequent_values |  |
| histogram |  |

### Metric resolving

Some metrics belong together as they depend on the same query.
When you specify 1 metric in a group, the other metrics in the group are also computed.
So Soda SQL might compute more metrics then are configured in the  scan.yml

Here are the groups

| Metrics |
| ------------|
| missing_count<br/>missing_percentage<br/>values_count<br/>values_percentage |
| valid_count<br/>valid_percentage<br/>invalid_count<br/>invalid_percentage |
| distinct<br/>unique_count<br/>uniqueness<br/>duplicate_count |

There are also some dependencies between the metrics.

Any metric related to invalid values (`valid_count`, `valid_percentage`, `invalid_count`, `invalid_percentage`) will
imply all missing metrics to be included as well (`missing_count`, `missing_percentage`, `values_count`, `values_percentage`)

Any missing metric (`missing_count`, `missing_percentage`, `values_count`, `values_percentage`) will imply
a `row_count` metric.

And last a `histogram` metric will imply `min` and `max` metrics.

## Column configurations

Column configuration keys:

| Key | Description |
| --- | ----------- |
| metrics | Extra metrics to be computed for this column |
| metric_groups | Extra metric groups to be computed for this column |
| tests | Tests to be evaluate for this column |
| missing_values | Customize what values are considered missing |
| missing_format | To customize missing values such as whitespace and empty strings |
| missing_regex | Define your own custom missing values |
| valid_format | Specifies valid values with a named valid text format |
| valid_regex | Specifies valid values with a regex |
| valid_values | Specifies valid values with a list of values |
| valid_min | Specifies a min value for valid values |
| valid_max | Specifies a max value for valid values |
| valid_min_length | Specifies a min length for valid values |
| valid_max_length | Specifies a max length for valid values |