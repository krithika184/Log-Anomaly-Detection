import json
import logging
import sys
import pandas as pd
from os.path import dirname
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from preprocessing import preprocess

lines = preprocess()
# print(len(lines))
# print(lines[3])

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')

# config = TemplateMinerConfig()
# config.load('https://github.com/logpai/Drain3/blob/master/examples/drain3.ini')
# config.profiling_enabled = True
# template_miner = TemplateMiner(config=config)

# config = TemplateMinerConfig()
# config.drain_sim_threshold = 0.4  # lower = more general templates
# config.drain_extra_delimiters = r'=:,"\'\(\)\[\]<>/'  # extract more tokens
# config.drain_max_depth = 5  # higher = more tree branches
# template_miner = TemplateMiner(config=config)

from drain3.template_miner_config import TemplateMinerConfig
from drain3.template_miner import TemplateMiner

config = TemplateMinerConfig()
# config.load("drain3.ini")  # Optional if you're using a config file

# Optional tuning:
config.drain_sim_threshold = 0.4
config.drain_extra_delimiters = r'=:,"\'\(\)\[\]<>/'

template_miner = TemplateMiner(config=config)

from drain3.file_persistence import FilePersistence

persistence = FilePersistence("drain3_state.json")
template_miner = TemplateMiner(config=config)

# Load saved templates
state = persistence.load_state()
if state:
    template_miner.load_state(state)

import time

start_time = time.time()
batch_start_time = start_time
batch_size = 10000

line_count=0
templateCol=[]
paramsCol=[]
for line in lines:
    line = line.rstrip()
    # line = line.partition(": ")[2]
    result = template_miner.add_log_message(line)
    templateCol.append(result.get("template_mined"))
    paramsCol.append(result.get("parameter_list", []))
    line_count += 1
    # if(line_count==2):
        # print(result)
    if line_count % batch_size == 0:
        time_took = time.time() - batch_start_time
        rate = batch_size / time_took
        logger.info(f"Processing line: {line_count}, rate {rate:.1f} lines/sec, "
                    f"{len(template_miner.drain.clusters)} clusters so far.")
        batch_start_time = time.time()
    if result["change_type"] != "none":
        result_json = json.dumps(result)
        logger.info(f"Input ({line_count}): {line}")
        logger.info(f"Result: {result_json}")

# Extract template and parameters
# df["template"] = templateCol
# df["params"] = template_results.apply(lambda r: r["parameter_list"])# Use .get() to avoid KeyError
# df["params"] = paramsCol

# print(result)

time_took = time.time() - start_time
rate = line_count / time_took
print(f"--- Done processing file in {time_took:.2f} sec. Total of {line_count} lines, rate {rate:.1f} lines/sec, "
            f"{len(template_miner.drain.clusters)} clusters")

sorted_clusters = sorted(template_miner.drain.clusters, key=lambda it: it.size, reverse=True)
for cluster in sorted_clusters:
    print(cluster)

print("Prefix Tree:")
template_miner.drain.print_tree()
template_miner.profiler.report(0)

print("Training done. Mined clusters:")
# obj = template_miner.drain.clusters.values()
# print(obj)
for cluster in template_miner.drain.clusters:
    print(cluster)
    print(cluster.cluster_id)
    print((cluster.get_template()))
    # print(cluster)

while True:
    log_line = input("> ")
    if log_line == 'q':
        break
    cluster = template_miner.match(log_line)
    if cluster is None:
        print(f"No match found")
    else:
        template = cluster.get_template()
        print(f"Matched template #{cluster.cluster_id}: {template}")
        # print(f"Parameters: {template_miner.get_parameter_list(template, log_line)}")