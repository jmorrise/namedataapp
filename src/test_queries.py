from google.cloud import bigquery
from collections import defaultdict
from matplotlib import pyplot as plt
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


bigquery_client = bigquery.Client()

test_names = ["Ella", "Henry", "Violet"]
logp_table = "namedata.sample_dataset.logp_sample"
min_logp_table = "namedata.sample_dataset.min_logp"
query = """
    WITH test_names AS
    (SELECT * FROM UNNEST(@names) AS test_name CROSS JOIN {})
    SELECT test_name name, test_year year, IFNULL(logp, min_logp - 0.2) logp
    FROM `{}`
    RIGHT OUTER JOIN test_names
    ON LOWER(name)=LOWER(test_name) AND year=test_year
    ORDER BY test_year ASC, test_name DESC
""".format(min_logp_table, logp_table)

job_config = bigquery.QueryJobConfig(query_parameters = [
    bigquery.ArrayQueryParameter('names', 'STRING', test_names)
])
query_job = bigquery_client.query(query, job_config=job_config)
results = query_job.result(timeout=30)

d = defaultdict(float)

for row in results:
    d[row["year"]] += row["logp"]

items = sorted(d.items())
years = list(map(lambda i: i[0], items))
logps = list(map(lambda i: i[1], items))

plt.plot(years, np.exp(logps))
plt.title(", ".join(test_names))
plt.show()
