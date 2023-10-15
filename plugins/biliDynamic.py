import asyncio
import json
from bilibili_api import user, sync
from flask import Flask, request, jsonify
# 实例化

async def dynamicsCount(u):
    # 用于记录下一次起点
    u = user.User(u)
    offset = 0

    # 用于存储所有动态
    dynamics = []

    # 无限循环，直到 has_more != 1
    while True:
        # 获取该页动态
        page = await u.get_dynamics(offset)

        if 'cards' in page:
            # 若存在 cards 字段（即动态数据），则将该字段列表扩展到 dynamics
            dynamics.extend(page['cards'])

        if page['has_more'] != 1:
            # 如果没有更多动态，跳出循环
            break

        # 设置 offset，用于下一轮循环
        offset = page['next_offset']

    # 打印动态数量
    #print(dynamics[0])
    return len(dynamics),dynamics[0].get("desc").get("dynamic_id")
    #print(f"共有 {len(dynamics)} 条动态")

app = Flask(__name__)
@app.route('/synthesize', methods=['POST'])
def synthesize():
    # 解析请求中的参数
    data = request.get_json()
    data=json.loads(data)
    print(data)
    uid = int(data["uid"])
    #print(uid)
    count,dynamic_id = sync(dynamicsCount(uid))
    # 返回一个字符串作为响应对象'
    print("========")
    print(dynamic_id)
    return json.dumps({"dynamic_id": str(dynamic_id)})
if __name__ == '__main__':
    app.run(debug=True,host='127.0.0.1', port=9081)

# 入口
