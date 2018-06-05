#!/usr/bin/python
# -*- coding:utf-8 -*-
import os, sys, re,requests,urllib2,time
#可以自行设置请求头
User_Agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'  
header = {}  
header['User-Agent'] = User_Agent 

#定义获取代理函数（网上免费版，吐槽QVQ）
def getfreeProxyIp():  
 proxy = []  
 for i in range(10):  
  try:  
   url = 'http://www.xicidaili.com/nn/'+str(i)  
   req = urllib2.Request(url,headers=header)  
   res = urllib2.urlopen(req).read()
   soup = BeautifulSoup(res,"html.parser")  
   ips = soup.findAll('tr')  
   for x in range(1,len(ips)):  
    ip = ips[x]  
    tds = ip.findAll("td")  
    ip_temp = tds[1].contents[0]+":"+tds[2].contents[0]  
    proxy.append(ip_temp)
  except:  
   continue  
 return  proxy

# 定义获取代理函数（scylla版本，至少我找到了可以用的）
def getProxyIp():  
    url = 'http://192.168.110.128:8899/api/v1/proxies'
    r = requests.get(url).json()
    proxy = []
    try:
        for i in r["proxies"]:
            ip = str(i['ip'])+":"+str(i['port'])
            proxy.append(ip)
    except:  
        pass 
    return  proxy

# 定义验证函数，提取可用IP代理
def testProxys(proxys):
    """ Test the proxys. """
    validProxys = []
    Url = "http://ip.chinaz.com/getip.aspx"
    for proxy in proxys:
        try:
            # set proxy
            proxy_handler = urllib2.ProxyHandler({'http':proxy, 'https':proxy})
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)
            # request website
            response = urllib2.urlopen(Url, timeout=5).read()

            # set filtration condition according website
            if re.findall('{ip:.*?,address:..*?}', response) != []: # remove invalid proxy
                validProxys.append(proxy)
                print "%s\t%s" % (proxy)
        except Exception as e:
            continue

    return validProxys

#定义设置代理函数

def regIESettings(op, noLocal=False, ip='', pac=''):
  '''
    # 根据需求生成Windows代理设置注册表的.reg文件内容
    # DefaultConnectionSettings项是二进制项
  '''
  if not op : return
  # 如果是设置IP代理的模式 则检查IP地址的有效性(允许为空，但不允许格式错误)
  if 'Proxy' in op and not ip == '': 
    # if len(extractIp(ip))==0
    if 1 > len(re.findall('([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\s*:{0,1}\s*([0-9]{1,5}){0,1}',ip)) :
      print '---Unexpected IP Address:%s---'%ip
      return
  options = {'On':'0F','Off':'01','ProxyOnly':'03','PacOnly':'05','ProxyAndPac':'07','D':'09','DIP':'0B','DS':'0D'}
  if op == 'Off':
    reg_value = '46,00,00,00,00,00,00,00,01'
  else:
    switcher = options.get(op)
    if not switcher:
      print '\n---Unexpected Option. Please check the value after [-o]---\n'
      return
    skipLocal = '07,00,00,00,%s'%__toHex('<local>') if noLocal else '00'
    reg_value = '46,00,00,00,00,00,00,00,%(switcher)s,00,00,00,%(ipLen)s,00,00,00,%(ip)s00,00,00,%(skipLocal)s,21,00,00,00%(pac)s' % ({ 'switcher':switcher,'ipLen':__toHex(len(ip)),'ip':__toHex(ip)+',' if ip else '','infoLen':__toHex(len('<local>')),'skipLocal':skipLocal,'pac':','+__toHex(pac) if pac else '' })
  settings = 'Windows Registry Editor Version 5.00\n[HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections]\n"DefaultConnectionSettings"=hex:%s' % reg_value
  # print 'Using proxy address: %s' % ip
  # print op, ip, pac
  # print options[op] +'\n'+ __toHex(ip) +'\n'+ __toHex(pac)
  # print settings
  # === 生成reg文件并导入到注册表中 ===
  filePath = '%s\DefaultConnectionSettings.reg'%os.getcwd() 
  with open(filePath, 'w') as f:
    f.write( settings )
  cmd = 'reg import "%s"' %filePath
  result  = os.popen(cmd)
  if len(result.readlines()) < 2 :
    print ''
  return 

def __toHex(obj):
  if   obj == '': return ''
  elif obj == 0 or obj == '0' or obj == '00': return '00'
  if isinstance(obj, str):
    rehex = [str(hex(ord(s))).replace('0x','') for s in obj]
    return ','.join(rehex)
  elif isinstance(obj, int):
    num = str(hex(obj)).replace('0x', '')
    return num if len(num)>1 else '0'+num # 如果是一位数则自动补上0，7为07，e为0e

def main():

  print'''
    
 .oooooo..o                          .     .o                    
d8P'    `Y8                        .o8   o888                    
Y88bo.      oooo    ooo  .oooo.o .o888oo  888  ooo. .oo.  .oo.   
 `"Y8888o.   `88.  .8'  d88(  "8   888    888  `888P"Y88bP"Y88b  
     `"Y88b   `88..8'   `"Y88b.    888    888   888   888   888  
oo     .d8P    `888'    o.  )88b   888 .  888   888   888   888  
8""88888P'      .8'     8""888P'   "888" o888o o888o o888o o888o 
            .o..P'                                               
            `Y8P'                                               



  '''
  regIESettings(op='Off', ip='', pac='', noLocal=False)
  proxy = getProxyIp()
  validProxys = testProxys(proxy)
  print '---Start agent---'
  while True:
    for ip in validProxys:
    	try:
  	  	print 'Being used'+ip
  	  	regIESettings(op='ProxyOnly', ip=ip, pac='', noLocal=False)
  	  	time.sleep(20)
  	except:
  		print 'GG!'

if __name__ == '__main__': 
    main()
    
