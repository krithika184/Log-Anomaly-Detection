import json
import logging
import sys
import pandas as pd
from os.path import dirname
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
import drain

def parse_log(log_line):
  import re
  # log_line = "2024-04-29 12:34:56 ERROR [module-name] Something broke here"
  pattern = r'\[(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(?P<level>\w+)\] \[(?P<module>.*?)\] (?P<message>.*)'
  match = re.match(pattern, log_line)
  if match:
    parsed_log = match.groupdict()
    return parsed_log

def getPersistence(persistence_type):
    
    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')
    
    if persistence_type == "KAFKA":
        from drain3.kafka_persistence import KafkaPersistence
        persistence = KafkaPersistence("drain3_state", bootstrap_servers="localhost:9092")
    elif persistence_type == "FILE":
        from drain3.file_persistence import FilePersistence
        persistence = FilePersistence("drain3_state.bin")
    elif persistence_type == "REDIS":
        from drain3.redis_persistence import RedisPersistence
        persistence = RedisPersistence(redis_host='',
                                   redis_port=25061,
                                   redis_db=0,
                                   redis_pass='',
                                   is_ssl=True,
                                   redis_key="drain3_state_key")
    else:
        persistence = None

def extract_parameters(lines):
  res=[]
  for line in lines:
    # print(line)
    res.append(parse_log(line))
  return res

def fetchMessages(lines):
  with open('logs\log_messages.txt','w') as writeFile:
    for line in lines:
      writeFile.write(line)
      writeFile.write(" \n")

def preprocess():
   
   line_count = 0
   with open('logs\system_logs.txt') as inputFile:
    lines = inputFile.readlines()
    
    df = pd.DataFrame.from_dict(extract_parameters(lines))
    msg=df['message'].to_list()
    fetchMessages(msg)

    logMsgFile = open('logs\log_messages.txt', 'r')
    lines = logMsgFile.readlines()
    print("A sample line : ",lines[3])
    return lines

# preprocess()