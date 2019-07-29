#coding=utf-8

import requests
import re
import time
import queue
import requests
import os
import socket
from socket import error
import threading
import random

def huoquIP(): # 获取IP数据
    agent = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:48.0) Gecko/20100101 Firefox/48.0'}
    url = 'http://192.168.1.114:3289/pop/'
    try:
        while True:
            a = requests.get(url, headers=agent).json()
            s = a['http']
            aa = s.strip("http://")
            f = open('ip.txt','a+')
            f.write(aa +'\n')
            f.close()
    except:
        pass
    return aa

localtime = time.asctime( time.localtime(time.time()))

class ProxyServerTest():
    def __init__(self,proxyip):
        #本地socket服务
        self.ser=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.proxyip = proxyip

    def run(self):
        try:
            #本地服务IP和端口
            self.ser.bind(('0.0.0.0', 9999))
            #最大连接数
            self.ser.listen(5)
        except error as e:
            print("[-]The local service : "+str(e))
            return "[-]The local service : "+str(e)
        while True:
            try :
                #接收客户端数据
                client,addr=self.ser.accept()
                print ('[*]accept %s connect'%(addr,))
                data=client.recv(1024)
                if not data:
                    break
                print ('[*'+localtime+']: Accept data...')
            except error as e:
                print("[-]Local receiving client : "+str(e))
                return "[-]Local receiving client : "+str(e)
            while True:
                    #目标代理服务器，将客户端接收数据转发给代理服务器
                    mbsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    iplen = len(self.proxyip)
                    proxyip = self.proxyip[random.randint(0,iplen-1)]
                    print("[!]Now proxy ip:"+str(proxyip))
                    prip = proxyip[0]
                    prpo= proxyip[1]
                    try:
                        mbsocket.settimeout(3)
                        mbsocket.connect((prip, prpo))
                    except:
                        print("[-]RE_Connect...")
                        continue
                    break
            try:
                mbsocket.send(data)
            except error as e:
                print("[-]Sent to the proxy server : "+str(e))
                return "[-]Sent to the proxy server : "+str(e)

            while True:
                try:
                    #从代理服务器接收数据，然后转发回客户端
                    data_1 = mbsocket.recv(1024)
                    if not data_1:
                        break
                    print ('[*'+localtime+']: Send data...')
                    client.send(data_1)
                except socket.timeout as e:
                    print(proxyip)
                    print("[-]Back to the client : "+str(e))
                    continue
            #关闭连接
            client.close()
            mbsocket.close()

def Loadips():
    print("[*]Loading proxy ips..")
    ip_list = []
    ip = ['ip','port']
    with open("ip.txt") as ips:
        lines = ips.readlines()
    for line in lines:
        ip[0],ip[1] = line.strip().split(":")
        ip[1] = eval(ip[1])
        nip = tuple(ip)
        ip_list.append(nip)
    return ip_list

def main():
    print("代理启动..........")
    ip_list = Loadips()
    try:
        pst = ProxyServerTest(ip_list)
        #多线程
        t = threading.Thread(target=pst.run, name='LoopThread')
        print ('[*]Waiting for connection...')
        #关闭多线程
        t.start()
        t.join()
    except Exception as e:
        print("[-]main : "+str(e))
        return "[-]main : "+str(e)

if __name__ == '__main__':
    print("""
    * by Explo1t
    * 2019.07.29
    * 更新了IP池子
                 
                                           
  ____       _   _            
 / ___|  ___| |_| |_ ___ _ __ 
 \___ \ / _ \ __| __/ _ \ '__|
  ___) |  __/ |_| ||  __/ |   
 |____/ \___|\__|\__\___|_|   
           
           
                                                                             
    
    """)

    a = input("是否启用抓取模式？如果不启用则需要本地填充IP.txt文本里的IP地址。")
    if a == "Y":
        huoquIP()
        print("开始抓取 .... ")
        main()
        print("代理开启 .... ")
        print("127.0.0.1:9999")
    else:
        main()


