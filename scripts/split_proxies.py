import yaml
import os
import math

# 配置参数
SHARDS = 10  # 分片数量

def main():
    if not os.path.exists('proxies_filtered.yaml'):
        print("proxies_filtered.yaml 不存在")
        return
    
    with open('proxies_filtered.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    proxies = data.get('proxies', [])
    if not proxies:
        print("没有节点可分片")
        return
    
    os.makedirs('shards', exist_ok=True)
    
    # 计算每个分片的节点数
    proxies_per_shard = math.ceil(len(proxies) / SHARDS)
    
    for i in range(SHARDS):
        start_idx = i * proxies_per_shard
        end_idx = min((i + 1) * proxies_per_shard, len(proxies))
        shard_proxies = proxies[start_idx:end_idx]
        
        if shard_proxies:
            with open(f'shards/proxies_{i}.yaml', 'w', encoding='utf-8') as f:
                yaml.dump({'proxies': shard_proxies}, f, allow_unicode=True, default_flow_style=False)
            print(f"分片 {i}: {len(shard_proxies)} 个节点")
    
    print(f"分片完成: 共 {SHARDS} 个分片")

if __name__ == '__main__':
    main()
