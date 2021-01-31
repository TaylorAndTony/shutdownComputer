import os
from pprint import pprint, pp

def asscociate_num_and_ip():
    dct = {}
    all_ip = [i[:-5] for i in os.listdir('online_devices')]
    for k, v in zip(range(1, len(all_ip) + 1), all_ip):
        dct[k] = v
    return dct


if __name__ == '__main__':
    pp(asscociate_num_and_ip())