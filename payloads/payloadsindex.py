

class PayloadIndex:
    # The class list the reference to every payload
    # The shell reference is the relative path of the shell script from payloads directory without suffix
    windows_x86_tcp_bind: str = "windows/x86/tcp_bind"
    linux_x86_tcp_reverse: str = "linux_x86_tcp_reverse"
    linux_netcat_reverse: str = "linux/netcat_reverse"
