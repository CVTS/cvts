# Introduction
The notebooks in this directory are designed to be run on the MapMatcher instance and tunneled to your local machine via ssh.



### Connect to CVTS Mapmatcher with an SSH Tunnel

This is based on the guide here: https://ljvmiranda921.github.io/notebook/2018/01/31/running-a-jupyter-notebook/

First add the following lines to your ssh config (~/.ssh/config) and make sure that you have been granted access via public key to the server.

```s
Host cvts-mapmatcher
    HostName 103.160.90.151
    Port 2235
    User ubuntu
    ForwardAgent true
    LocalForward 7799 localhost:7799
```

Then you should be able to login to the server simply with 
```bash
ssh cvts-mapmatcher
```

### Running Jupyter inside TMUX

Once connected, use [tmux](https://en.wikipedia.org/wiki/Tmux) to allow your notebook sessions to persist without the ssh connection being active.

```bash
tmux new-session -A -s main 
```

You can then use tmux commands to create multiple bash prompt that won't be disconnected

```
Ctrl-B C   Creates a new window
Ctrl-B N   Moves to the next windows
Ctrl-B P   Moves to the previous windows
Ctrl-B D   Disconnect from the current session
```


In one of these tmux windows run the 
