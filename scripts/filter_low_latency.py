import yaml
import os

# 配置参数
MAX_LATENCY_MS = 5000  # 最大延迟阈值

def main():
    if not os.path.exists('proxies_dedup.yaml'):
        print("proxies_dedup.yaml 不存在")
        return
    
    with open('proxies_dedup.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    proxies = data.get('proxies', [])
    filtered_proxies = []
    
    for proxy in proxies:
        # 如果没有延迟信息，保留节点
        if 'latency' not in proxy:
            filtered_proxies.append(proxy)
        elif proxy['latency'] <= MAX_LATENCY_MS:
            filtered_proxies.append(proxy)
    
    with open('proxies_filtered.yaml', 'w', encoding='utf-8') as f:
        yaml.dump({'proxies': filtered_proxies}, f, allow_unicode=True, default_flow_style=False)
    
    print(f"过滤完成: {len(proxies)} -> {len(filtered_proxies)} 个节点")

if __name__ == '__main__':
    main()
