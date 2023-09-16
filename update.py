from subprocess import run
import yaml

url = ''
if not url:
    raise SystemExit
run(['curl', '-o', 'config.yaml', url])

with open('parser.yaml', 'r', encoding='utf-8') as f:
    parser = yaml.safe_load(f)
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

config['secret'] = 'key'

# tun mode: system or gvisor
# config['tun']= {'enable': True, 'stack': 'system', 'auto-route': True, 'auto-detect-interface': True, 'dns-hijack': ['any:53']}

# prepend-proxy-groups:
config['proxy-groups']=parser['prepend-proxy-groups']+config['proxy-groups']

# append-proxy-groups:
config['proxy-groups'].extend(parser['append-proxy-groups'])

# prepend-rules:
config['rules']=parser['prepend-rules']+config['rules']

# commands:
config['proxy-groups'][1]['proxies'].insert(0, '🔯 负载均衡') # - proxy-groups.1.proxies.0+🔯 负载均衡

proxyNames = []
groupNames = ['DIRECT']
for proxy in config['proxies']:
    proxyNames.append(proxy['name'])
for group in parser['append-proxy-groups']:
    groupNames.append(group['name'])

def filter(group, keyword):
    group['proxies'] = [i for i in proxyNames if keyword in i]

for group in config['proxy-groups']:
    if group['name'] == '🔯 负载均衡': # - proxy-groups.🔯 负载均衡.proxies=[]groupNames|⚖️
        group['proxies'] = groupNames
    elif group['name'] == '⚖️ HK': # - proxy-groups.⚖️ HK.proxies=[]proxyNames|香港
        filter(group, '香港')
    elif group['name'] == '⚖️ TW': # - proxy-groups.⚖️ TW.proxies=[]proxyNames|台湾
        filter(group, '台湾')
    elif group['name'] == '⚖️ US': # - proxy-groups.⚖️ US.proxies=[]proxyNames|美国
        filter(group, '美国')

# yaml formatter
class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)

with open('config.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(config, f, Dumper=IndentDumper,allow_unicode=True,default_flow_style=False,sort_keys=False)

run('curl -X PUT -H "Authorization: Bearer key" 127.0.0.1:9090/configs --json "{}"')