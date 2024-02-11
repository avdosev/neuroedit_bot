import json
import random
import re
import logging

rnd = random.SystemRandom()

def read_json(path):
    try:
        with open(path, 'r',  encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def read_file(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except:
        logging.error('cant read file', path)
    
    return None

def write_file(path, info):
    try:
        with open(path, 'w') as f:
            f.write(info)
            f.flush()    
    except:
        logging.error('cant write file', path)
    
    return None


def read_key(key):
    return read_file(f'sensitive_info/{key}')


def dump_json(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.flush()
