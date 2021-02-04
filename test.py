import os
from datetime import datetime


def give_me_date() -> str:
    """get the current date and time"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def log_start_status():
    """
    If this client is started, it will first write online time
    to a txt file named client_start_status.txt
    this txt file only log 10 most recent online times.
    """
    if not os.path.exists('client_start_status.txt'):
        f = open('client_start_status.txt', 'w')
        f.close()
    # 文件存在
    else:
        # 先读取
        with open('client_start_status.txt', 'r', encoding='utf-8') as f:
            content = f.read().splitlines()
        # 判断文件长度
        # 超出限制
        if len(content) > 10:
            content.pop(0)
            content.append(give_me_date())
            # 复写文件
            with open('client_start_status.txt', 'w') as f:
                f.write('\n'.join(content))
        else:
            with open('client_start_status.txt', 'a') as f:
                f.write(give_me_date() + '\n')

if __name__ == '__main__':
    log_start_status()
