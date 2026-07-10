import yaml
import os
import re

def extract_country_code(name):
    """从节点名称中提取国家代码"""
    # 改进的正则表达式
    patterns = [
        r'\[([A-Z]{2})\]',  # [US] 格式
        r'([A-Z]{2})\s*[-|]',  # US- 或 US| 格式
        r'^(US|CN|JP|KR|HK|TW|SG|UK|DE|FR|RU|CA|AU)',  # 开头的国家代码
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    
    return None

def group_proxies_by_country(proxies):
    """按国家分组节点"""
    groups = {}
    for proxy in proxies:
        name = proxy.get('name', '')
        country = extract_country_code(name)
        if country:
            if country not in groups:
                groups[country] = []
            groups[country].append(proxy['name'])
    return groups

def main():
    # 读取测速后的节点
    if not os.path.exists('proxies_speedtest.yaml'):
        print("proxies_speedtest.yaml 不存在")
        return
    
    with open('proxies_speedtest.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    proxies = data.get('proxies', [])
    if not proxies:
        print("没有可用节点")
        return
    
    # 按国家分组
    country_groups = group_proxies_by_country(proxies)
    
    # 构建策略组
    proxy_groups = []
    
    # 故障转移组
    proxy_groups.append({
        'name': '故障转移',
        'type': 'fallback',
        'proxies': ['自动选择', '低延迟', '负载均衡'] + [p['name'] for p in proxies[:5]],
        'url': 'https://www.google.com',
        'interval': 300
    })
    
    # 自动选择组
    proxy_groups.append({
        'name': '自动选择',
        'type': 'url-test',
        'proxies': [p['name'] for p in proxies],
        'url': 'https://www.google.com',
        'interval': 300,
        'tolerance': 50
    })
    
    # 低延迟组
    proxy_groups.append({
        'name': '低延迟',
        'type': 'url-test',
        'proxies': [p['name'] for p in proxies[:20]],
        'url': 'https://www.google.com',
        'interval': 300,
        'tolerance': 50
    })
    
    # 负载均衡组
    proxy_groups.append({
        'name': '负载均衡',
        'type': 'load-balance',
        'proxies': [p['name'] for p in proxies],
        'strategy': 'consistent-hashing',
        'url': 'https://www.google.com',
        'interval': 300
    })
    
    # 按国家创建策略组
    for country, proxy_names in country_groups.items():
        if proxy_names:
            proxy_groups.append({
                'name': f'🇨🇳 {country}' if country == 'CN' else f'{country}',
                'type': 'select',
                'proxies': proxy_names[:10]  # 限制每组最多 10 个节点
            })
    
    # 构建最终配置
    config = {
        'port': 7890,
        'socks-port': 7891,
        'redir-port': 7892,
        'allow-lan': False,
        'mode': 'rule',
        'log-level': 'info',
        'external-controller': '127.0.0.1:9090',
        'dns': {
            'enable': True,
            'listen': '0.0.0.0:53',
            'enhanced-mode': 'fake-ip',
            'nameserver': [
                'https://dns.alidns.com/dns-query',
                'https://doh.pub/dns-query'
            ],
            'fallback': [
                'https://dns.google/dns-query',
                'https://cloudflare-dns.com/dns-query'
            ],
            'fallback-filter': {
                'geoip': True,
                'ipcidr': ['240.0.0.0/4']
            }
        },
        'proxies': proxies,
        'proxy-groups': proxy_groups,
        'rules': [
            'DOMAIN-KEYWORD,admarvel,REJECT',
            'DOMAIN-KEYWORD,admaster,REJECT',
            'DOMAIN-KEYWORD,adsage,REJECT',
            'DOMAIN-KEYWORD,adsmogo,REJECT',
            'DOMAIN-KEYWORD,adsrvmedia,REJECT',
            'DOMAIN-KEYWORD,adwords,REJECT',
            'DOMAIN-KEYWORD,adservice,REJECT',
            'DOMAIN-KEYWORD,tracking,REJECT',
            'DOMAIN-KEYWORD,analytics,REJECT',
            'DOMAIN-SUFFIX,appsflyer.com,REJECT',
            'DOMAIN-SUFFIX,adjust.com,REJECT',
            'GEOIP,CN,DIRECT',
            'MATCH,Proxy'
        ]
    }
    
    # 写入配置文件
    with open('clash.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    print(f"配置构建完成: {len(proxies)} 个节点, {len(proxy_groups)} 个策略组")

if __name__ == '__main__':
    main()
