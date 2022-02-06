import argparse
import json
import re
import glob
import os
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='path', action='store', default="/logs/access_20k", help='Path to logs')
args = parser.parse_args()

dict_ip = defaultdict(
    lambda: {"COUNT": 0, "GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "HEAD": 0}
)

dict_time = defaultdict(
    lambda: {"METHOD": '', "URL": '', "DURATION": 0, "TIME": ''}
)

dict_count = {"TOTAL REQUESTS": 0}


def top_frequency_request():
    for filename in glob.glob(os.getcwd() + f'{args.path}' + '*.log'):
        print(filename)
        with open(os.path.join(os.getcwd(), filename), 'r') as file:
            for line in file.readlines():
                ip_match = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
                if ip_match is not None:
                    ip = ip_match.group()
                    method = re.search(r"POST|GET|PUT|DELETE|HEAD", line)
                    if method is not None:
                        dict_ip[ip][method.group()] += 1
                        dict_ip[ip]["COUNT"] += 1
    return dict(sorted(dict_ip.items(), key=lambda x: x[1].get('COUNT'), reverse=True)[:3])


def top_long_request():
    for filename in glob.glob(os.getcwd() + f'{args.path}' + '*.log'):
        with open(os.path.join(os.getcwd(), filename), 'r') as file:
            for line in file.readlines():
                method_match = re.search(r"POST|GET|PUT|DELETE|HEAD", line)
                url_match = re.search(r"http.+(?=\"\s\")", line)
                ip_match = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
                duration_match = re.search(r"(?<=\s)\d+(?=\n)", line)
                time_match = re.search(r"(?<=\[).+(?= \+)", line)
                if (method_match is not None) and (url_match is not None) and (ip_match is not None) and \
                        (duration_match is not None) and (time_match is not None):
                    ip = ip_match.group()
                    dict_time[ip]["METHOD"] = method_match.group()
                    dict_time[ip]["URL"] = url_match.group()
                    dict_time[ip]["DURATION"] = int(duration_match.group())
                    dict_time[ip]["TIME"] = time_match.group()
    return dict(sorted(dict_time.items(), key=lambda x: x[1].get("DURATION"), reverse=True)[:3])


def count_requests():
    for filename in glob.glob(os.getcwd() + f'{args.path}' + '*.log'):
        with open(os.path.join(os.getcwd(), filename), 'r') as file:
            for line in file.readlines():
                ip_match = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
                if ip_match is not None:
                    dict_count["TOTAL REQUESTS"] += 1
    return dict_count


result = [count_requests()]
result.append(top_frequency_request())
result.append(top_long_request())

with open("result.json", "w") as jsonfile:
    json.dump(result, jsonfile, indent=4)

print(json.dumps(result, indent=4))
