from google.cloud import bigquery
from collections import defaultdict
import numpy as np

'''
Queries to create the BigQuery tables:

logp_sample table:
with year_counts as
(SELECT year, sum(number) total_count
FROM `bigquery-public-data.usa_names.usa_1910_current`
group by year order by year)
select name, names.year, log10(sum(number)/total_count) logp from
`bigquery-public-data.usa_names.usa_1910_current` names
join year_counts on names.year=year_counts.year
group by name, year, total_count
order by year asc, logp desc

min_logp table:
SELECT year as test_year, MIN(logp) as min_logp
FROM `namedata.sample_dataset.logp_sample`
group by year order by year asc;
'''

logp_table = "namedata.sample_dataset.logp_sample"
min_logp_table = "namedata.sample_dataset.min_logp"
unknown_penalty = 0.4

"""
Returns years and corresponding log probabilities.
"""
def get_log_probs(names_list, timeout_seconds=30):
    bigquery_client = bigquery.Client()
    query = """
        WITH test_names AS
        (SELECT * FROM UNNEST(@names) AS test_name CROSS JOIN {})
        SELECT test_name name, test_year year, IFNULL(logp, min_logp - {}) logp
        FROM `{}`
        RIGHT OUTER JOIN test_names
        ON LOWER(name)=LOWER(test_name) AND year=test_year
        ORDER BY test_year ASC, test_name DESC
    """.format(min_logp_table, unknown_penalty, logp_table)
    job_config = bigquery.QueryJobConfig(query_parameters = [
        bigquery.ArrayQueryParameter('names', 'STRING', names_list)
    ])
    query_job = bigquery_client.query(query, job_config=job_config)
    results = query_job.result(timeout=timeout_seconds)
    d = defaultdict(float)
    for row in results:
        d[row["year"]] += row["logp"]

    items = sorted(d.items())
    years = np.array([i[0] for i in items])
    logps = np.array([i[1] for i in items])
    return years, logps


if __name__ == "__main__":
    test_names = ["George", "Ronald", "Lyndon", "William", "John"]
    years, logps = get_log_probs(test_names)
