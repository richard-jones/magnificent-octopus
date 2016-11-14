import multiprocessing

bind = "127.0.0.1:[port number]"
workers = multiprocessing.cpu_count() * 8 + 1
proc_name = '[your process name]'
max_requests = 1000