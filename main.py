import os
import sys
import argparse
import threading
from yaml import load,dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader,Dumper


if __name__ == "__main__":   
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_path",type=str,default="config.yml",help="config file path")
    parser.add_argument("--port",type=int,help="which port to use")
    parser.add_argument("--logging_mode",type=bool,default=False,help="whether record")
    parser.add_argument("--llm_type",type=str,help="which large language model to use")
    args = parser.parse_args()

    class dotdict(dict):
        __getattr__ = dict.get
        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__
    
    def object_hook(dict_item):
        for key,value in dict_item.items():
            if isinstance(value,dict):
                dict_item[key] = dotdict(value)
            else:
                dict_item[key] = value
        return dotdict(dict_item)
    
    fontcolor_green = "\033[1;32m"
    fontcolor_red = "\033[1;31m"
    fontcolor_white = "\033[1;37m"

    def error_print(*s):
        print(fontcolor_red,end="")
        print(*s)
        print(fontcolor_white,end="")
    # def error_helper(e,doc_url):
    #     error_print(e)
    #     error_print("查看：",doc_url)
    def success_print(*s):
        print(fontcolor_green,end="")
        print(*s)
        print(fontcolor_white,end="")
    
    try:
        stream = open(args.config_path,encoding="utf-8")
    except:
        error_print("加载配置失败，改为加载默认配置")
        stream = open("example.config.yml",encoding="utf-8")
    settings = dotdict(load(stream,Loader=Loader))
    for key,value in args.__dict__.items():
        settings[key] = value
    try:
        settings.llm = settings.llm_models[settings.llm_type]
    except:
        error_print("没有读取到LLM参数，可能是因为当前模型为API调用。")

    class CounterLock:
        def __init__(self):
            self.lock = threading.Lock()
            self.waiting_threads = 0
            self.waiting_threads_lock = threading.Lock()

        def acquire(self):
            with self.waiting_threads_lock:
                self.waiting_threads += 1
            acquired = self.lock.acquire()

        def release(self):
            self.lock.release()
            with self.waiting_threads_lock:
                self.waiting_threads -= 1

        def get_waiting_threads(self):
            with self.waiting_threads_lock:
                return self.waiting_threads

        def __enter__(self):  # 实现 __enter__() 方法，用于在 with 语句的开始获取锁
            self.acquire()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):  # 实现 __exit__() 方法，用于在 with 语句的结束释放锁
            self.release()
    
