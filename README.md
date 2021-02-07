# shutdownComputer

a tool for shutting down PCs

## usage:

### client:

1. configure `localIP` as the ip address on this client
2. configure `targetIP` as the ip address on the server
3. configure `port` and `cmd_port`, just make sure these are the same as the server's
4. start the `client.py`

### server:

1. configure `ip`, `port`, `cmd_port`, make sure these are the same as the clients'
2. start the server, make sure there is a cmd window to perform actions.
3. click on `start server` button,type y in the cmd and then the server is started.
4. you can see clients conneting to it
5. once you think all clients have started, click `refresh` button
6. now you can select clients. **if you selected one client twice, it will be cancelled**, and you can see which clients are selected on cmd.
7. type cmd in the cmd entry and hit `execute`, and there you go.

notice:
- `read txt ip` can read `manual_set_ip.txt`, and set all ip into it.
- `read all ip in current folder` can dump all existed json files into `manual_set_ip.txt`, then hit `read txt ip` again.

## detailed usage:

see `配置文件说明.md` in Client and Server folder