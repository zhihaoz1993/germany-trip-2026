# -*- coding: utf-8 -*-
"""一次性修订脚本：系统性修复 + 每日素材丰富（小红书/马蜂窝/博客）。"""
import json, os
from urllib.parse import quote

d = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(d, "tripData.json")
trip = json.load(open(path, encoding="utf-8"))
days = trip["days"]

XHS = "https://www.xiaohongshu.com/explore/{}?xsec_token={}"

def card(id, token, title, likes, takeaway, src=None):
    c = {"title": title, "likes": str(likes),
         "url": XHS.format(id, quote(token)), "takeaway": takeaway}
    if src:
        c["src"] = src
    return c

# ---------- 1) dayLabel 补全 ----------
for i, day in enumerate(days):
    if not day.get("dayLabel"):
        day["dayLabel"] = f"D{i}"

# ---------- 2) 主题修复（内嵌 · 导致卡片标题被截断，D4 丢苏黎世） ----------
days[4]["theme"] = "福森 (Füssen) → 林道/博登湖 (Lindau/Bodensee) → 苏黎世 (Zürich)"
days[7]["theme"] = "因特拉肯 (Interlaken) 周边（布里恩茨 (Brienz) 蒸汽火车、施皮茨 (Spiez)）→ 伯尔尼 (Bern)"
days[11]["theme"] = "海德堡 (Heidelberg) → 莱茵河谷（马克斯堡、博帕德 (Boppard)、圣戈尔 (St. Goar)、巴哈拉赫 (Bacharach)）"
days[12]["theme"] = "莱茵河谷（巴哈拉赫 (Bacharach)、上韦瑟尔 (Oberwesel)、洛蕾莱、吕德斯海姆 (Rüdesheim)）→ 法兰克福 (Frankfurt)"

# ---------- 3) 路线修复：起终点与实际住宿一致 ----------
# 9/29 住图恩，但路线终点写成因特拉肯
days[5]["theme"] = "苏黎世 (Zürich) → 琉森 (Luzern) → 龙疆 (Lungern) → 图恩 (Thun)（顺路游玩，不走回头路）"
days[5]["route"]["to"] = "图恩 (Thun)"
days[5]["route"]["mapPts"] = ["Zürich, Switzerland", "Lucerne, Switzerland", "Lungern, Switzerland", "Brienz, Switzerland", "Interlaken, Switzerland", "Thun, Switzerland"]
days[5]["activities"].append({
    "time": "20:00", "name": "因特拉肯 → 图恩，入住 Hotel Aare Thun",
    "duration": "35min", "cost": 0, "transport": "自驾",
    "note": "图恩是接下来两晚的大本营，比因特拉肯更安静、性价比高"})
# 9/30 从图恩出发、回图恩住
days[6]["route"]["from"] = "图恩 (Thun)"
days[6]["route"]["to"] = "图恩 (Thun)"
days[6]["route"]["mapPts"] = ["Thun, Switzerland", "Grindelwald, Switzerland", "Lauterbrunnen, Switzerland", "Interlaken, Switzerland", "Thun, Switzerland"]
# 10/1 从图恩出发
days[7]["route"]["from"] = "图恩 (Thun)"
days[7]["route"]["mapPts"] = ["Thun, Switzerland", "Brienz, Switzerland", "Spiez, Switzerland", "Bern, Switzerland"]
# 10/6 终点应为法兰克福市区（Westin），机场还车在 10/7
days[12]["route"]["to"] = "法兰克福 (Frankfurt)"
days[12]["route"]["mapPts"] = ["Bacharach, Germany", "Oberwesel, Germany", "Loreley, Sankt Goarshausen, Germany", "Rüdesheim am Rhein, Germany", "Frankfurt, Germany"]
for a in days[12]["activities"]:
    if "法兰克福机场" in a.get("name", ""):
        a["name"] = "吕德斯海姆 → 法兰克福市区（入住 Westin）"
        a["note"] = "机场还车安排在明天（10/7）上午，今晚住市中心 Westin，晚饭后可沿美因河散步"
# 修订记录⑤与实际酒店不一致
trip["revisionNotes"] = [n.replace("Day12 住法兰克福机场", "Day12 住法兰克福市中心 Westin（机场还车在 Day13）") for n in trip["revisionNotes"]]

# ---------- 4) 慕尼黑两天丰富（你们逛得快 → 加可选深度/周边项） ----------
# 9/25 抵达日：加可选傍晚项
days[1]["activities"].append({
    "time": "17:30", "name": "阿桑教堂 + 哈克桥日落（可选）", "duration": "1.5h", "cost": 0,
    "transport": "步行/S-Bahn", "priority": "optional",
    "note": "阿桑教堂是暗黑系洛可可，免费、10 分钟即可看完；体力够的话傍晚去 Hackerbrücke 桥，本地人坐在桥栏杆上喝啤酒看日落"})
# 9/26 完整市区日：加宁芬堡/宝马/德意志博物馆可选项 + 午餐备选
for a in days[2]["activities"]:
    if a.get("meal") and "Hofbräuhaus" in a["meal"].get("name", ""):
        a["meal"]["note"] = "备选：谷物市场旁的 Schmalznudel – Cafe Frischhut（糖油果子，本地人排队，只收现金）；想安静可选 Augustiner Bräustuben"
days[2]["activities"].extend([
    {"time": "15:30", "name": "宁芬堡宫（可选，与王宫二选一或都打卡）", "duration": "2h", "cost": 60,
     "transport": "电车17路到 Schloss Nymphenburg", "priority": "optional",
     "note": "宫殿票€8、联票€15、花园免费；电车约20分钟。后花园天鹅湖人少出片；你们逛得快，王宫2小时+宁芬堡2小时完全来得及"},
    {"time": "17:00", "name": "宝马世界 BMW Welt / 宝马博物馆（可选）", "duration": "1.5h", "cost": 0,
     "transport": "U3 到 Olympiazentrum", "priority": "optional",
     "note": "Welt 免费、开到22:00，螺旋展厅很有未来感；博物馆€10、10:00-18:00；车迷必去，不感兴趣可跳过"},
    {"time": "—", "name": "备选：德意志博物馆（雨天/科技爱好者）", "duration": "2h+", "cost": 30,
     "transport": "电车/步行", "priority": "optional",
     "note": "世界最大科技博物馆，€15/人；如遇雨天可替换英国花园"}])
days[2]["overview"]["alert"] = "市政厅木偶钟 11:00/12:00（夏季加17:00）演出；王宫+珍宝馆你们 2 小时够逛，下午可弹性加宁芬堡或宝马。"

# 9/28 苏黎世：加可选夜游
days[4]["activities"].append({
    "time": "20:30", "name": "苏黎世湖畔夜游（可选）", "duration": "45min", "cost": 0,
    "transport": "步行", "priority": "optional",
    "note": "饭后沿 Bürkliplatz 湖边散步看老城灯火；明天长途驾驶日，量力而行"})

# 10/3 罗滕堡：加圣诞商店
days[9]["activities"].insert(-1, {
    "time": "17:00", "name": "Käthe Wohlfahrt 圣诞村商店（可选）", "duration": "45min", "cost": 0,
    "transport": "步行", "priority": "optional",
    "note": "全球最大圣诞用品店，全年都是圣诞节；胡桃夹子和木雕值得看，伴手礼好去处"})
# 10/4 周日提醒
days[10]["overview"]["alert"] = (days[10]["overview"].get("alert", "") + " 10/4 为周日，德国商店全天关门，但景点、餐厅正常营业；想购物请提前在罗滕堡完成。").strip()
# 10/7 法兰克福：加铁桥可选
days[13]["activities"].insert(2, {
    "time": "10:00", "name": "铁桥 Eiserner Steg + 美因河南岸（可选）", "duration": "40min", "cost": 0,
    "transport": "步行", "priority": "optional",
    "note": "挂满同心锁的人行铁桥，拍法兰克福天际线最好的角度"})

# ---------- 5) 每日小红书/其他来源卡片丰富 ----------
add = {
 1: [card("692817ea000000001e00a580", "ABPKTTiWTn5K6o0yjOVz5pVIsYo3NzuGHQA3hmN4CJvhU=", "慕尼黑10小时转机，citywalk暴走全攻略", 124,
          "证明老城核心区半天到一天即可走完：圣母教堂→玛丽亚广场→谷物市场一线全部步行可达"),
     card("6a869059000000001603ff44", "ABgIhU7Rt-CWPh4bz3mOJvm3KJ_u6id-utXRVBp33aaRc=", "德国慕尼黑市区1日游", 62,
          "作者一天走完老城+王宫+英国花园+宝马世界；你们抵达日下午+次日一整天，节奏更从容")],
 2: [card("6810c8070000000023003de0", "AB0AN2jV5vhR8s5PFjzBF3HQl5K-WhOTiX3UH8JWOsWVU=", "宁芬堡宫｜慕尼黑梦幻童话宫殿一日游", 160,
          "电车17路直达；宫殿€8/联票€15/花园免费；镜厅华丽，后花园天鹅湖是出片机位"),
     card("69bc9eca000000001a0293a3", "ABgoy3p9shON2ZcLtmvnw_EcqvYzTNtuZ63FDvdXC40qo=", "慕尼黑暴走一日游：从老城到球场全覆盖", 148,
          "老城→球场动线参考，适合体力好的一天打卡更多点位"),
     card("6a329e4200000000110135fa", "ABnqepJu65JXpkTXHEaLnjRSvIhG13a5aMnX34FiEYNiQ=", "慕尼黑，本地人才知道的小众玩法", 63,
          "本地人视角的小众去处，可与经典线互补"),
     card("6956c01b000000001e0065a3", "ABSPjfwOpF21y5uoV1zbuWEdn_pP-YLk4CFXhKoaz_B20=", "慕尼黑必来啤酒花园？我说点不滤镜的", 10,
          "啤酒花园真实体验：部分需自己找位/柜台点单，可自带食物（英国花园啤酒花园允许）"),
     {"src": "马蜂窝系攻略", "title": "慕尼黑2日游懒人攻略：经典景点与美食推荐", "likes": "攻略",
      "url": "https://www.danglv.com/zhishi/20250221/20597.html",
      "takeaway": "王宫语音导览免费；圣神教堂挂满风筝很出片；哈克桥日落氛围惬意"}],
 4: [card("6a9bd48b0000000011038f71", "ABXxiBZ_yg6ujQGso9KMbf_XZBN732-c_V768P-XQJDKo=", "这座千年古城满足你对中欧所有幻想（林道）", 277,
          "林道港灯塔+巴伐利亚狮像是博登湖明信片机位，老城岛步行一圈约1小时"),
     card("69d90739000000001d01a9aa", "ABPhAEsl1Wx0LW1q53tuqVTZz3W_25_GGUhysNA9UMA4g=", "苏黎世一日游", 1370,
          "苏黎世最高赞一日游：老城、林登霍夫山、班霍夫大街一线走完"),
     card("69d319f70000000022028042", "ABGHgJ-q2g0w2ggHnxYTG7hP-BmOWUmcj4alxJ0juvj7o=", "苏黎世一日通票指南｜爱的迫降打卡", 253,
          "《爱的迫降》同款机位：林登霍夫山、苏黎世湖、老城；自驾进城注意限行，建议停酒店步行"),
     card("6a522c9900000000160263ed", "ABSBMeiPJUQ4XRsWSPxcHAqTMVXFWi_rkGIlfjcSqiCac=", "瑞士被严重低估的城市｜苏黎世私藏机位", 141,
          "私藏机位合集，傍晚林登霍夫山俯瞰老城全景最出片"),
     {"src": "美食推荐", "title": "苏黎世必吃：Zeughauskeller 军械库餐厅 + Sprüngli", "likes": "美食",
      "url": "https://www.mafengwo.cn/search/q.php?q=%E8%8B%8F%E9%BB%8E%E4%B8%96%20%E7%BE%8E%E9%A3%9F",
      "takeaway": "Zeughauskeller 吃苏黎世小牛肉（Zürcher Geschnetzeltes，人均€35）；Sprüngli 的 Luxemburgerli 马卡龙当伴手礼"}],
 5: [card("69e83b4c0000000020038456", "AB5VStRa0CRj7N3AZF8dK0kMU9U0XGvTD-tsYrXFhkMu0=", "瑞士龙疆小镇怎么玩，看这里", 304,
          "龙疆翡翠湖环湖步道约1.5h；S弯观景台（Brünigstrasse 路边）是最经典机位"),
     card("69d47e6b000000001a02b3ff", "ABc1cUt0V-Q9v3L4t5yj6e5s2diSe2fF9poXLwnrnteZY=", "龙疆小镇打卡机位分享", 269,
          "机位合集：湖边长椅、教堂尖顶、山坡俯瞰；下午顺光拍湖水更绿"),
     card("6a4a2401000000001003ee59", "ABMfWHyTX5xL1FoPE0_jN2r-yQpyDtiyLUx6uDn8-CbAc=", "卢塞恩（琉森）老城Citywalk路线", 257,
          "卡佩尔廊桥→老城壁画→垂死狮子像→穆塞格城墙（爬塔俯瞰全城，免费）"),
     card("69f76638000000003601c118", "AB7uG7nCWlyhkd5OWmvWgNmBv8kl7gcUwBUhHUyD_X6S8=", "卢塞恩+Rigi山+龙疆一日速通", 198,
          "速通动线参考；你们自驾版顺序一致，时间更弹性"),
     {"src": "攻略补充", "title": "卢塞恩一日漫游保姆级攻略", "likes": "攻略",
      "url": "https://www.mafengwo.cn/search/q.php?q=%E7%90%89%E6%A3%AE%20%E6%94%BB%E7%95%A5",
      "takeaway": "垂死狮子像纪念1792年保卫法王路易十六的瑞士雇佣兵；城墙塔楼16:50关闭，注意时间"}],
 6: [card("69c92bf3000000002200fd52", "ABeBW_z0lOuZcsmT5AOXIgu0uqt70DYJghkkNiZYH8Pzo=", "少女峰别再走左上右下了！自驾的来抄作业", 378,
          "自驾党路线：车停格林德瓦 Terminal，艾格快线15分钟上艾格冰川站再转登山火车，比劳特布龙嫩线快"),
     card("6a343867000000001702b09f", "ABrb0OpUoRracfI8ze5RRO5Tfcb5hodY4Lbi_8yTaYaeU=", "少女峰快速上山详细攻略", 276,
          "山顶3454m注意高反缓行；冰宫、 Sphinx 观景台必看；下山可绕劳特布龙嫩看瀑布"),
     card("6a6b62d10000000008011199", "AB19I4AeTw2ea3NUhK-GVNxON0EuVt_Cj9Sum8sZw49rs=", "瑞士第一'诈骗'｜少女峰（避坑向）", 108,
          "反方观点值得读：票价贵、天气决定一切——出发前务必查山顶实时摄像头，阴天别硬上"),
     {"src": "攻略补充", "title": "哈德昆 Harder Kulm 日落要点", "likes": "攻略",
      "url": "https://www.mafengwo.cn/search/q.php?q=Harder%20Kulm",
      "takeaway": "因特拉肯北站步行10分钟到缆车站，往返约CHF 38；两湖之间观景台日落时分最美"}],
 7: [card("6a33d9a0000000001c026797", "ABTdoTiU4OkdyZD-mh48lICJW04SFwCfP88AEi4qa1J20=", "布里恩茨蒸汽小火车打卡攻略", 740,
          "Brienz Rothorn Bahn：6月初-10月底运行，往返约CHF 96，旺季务必官网提前订时段；单程约1小时"),
     card("68e83ace0000000004028028", "ABrWQqVG_vrHxUiYZlgXgrY1pA9UDFtEXDuAGA7dniPno=", "按需避雷：布里恩茨蒸汽火车真的不值票价？", 95,
          "反方观点：票价高、山顶停留短——晴天值、阴天亏；坐左侧（湖侧）视野更好"),
     card("6a09c913000000003701d23c", "ABFTxlJAg1JkQnFb3xzeLG-eR8WgbfnnBTt_OVZgraXVY=", "伯尔尼超顺路一日游攻略", 281,
          "时钟塔整点木偶表演（提前5分钟占位置）→爱因斯坦故居→熊苑→玫瑰园俯瞰老城"),
     card("6a6ee2b0000000002402f558", "ABxSHCPEsIS2ebwDk8C7yFocmWD0F9ict6ycKZpCVNO_o=", "瑞士伯尔尼｜被严重低估的童话首都", 95,
          "老城拱廊6km雨天也能逛；玫瑰园餐厅可边看全景边吃晚餐"),
     {"src": "美食推荐", "title": "伯尔尼吃什么：Kornhauskeller 地窖餐厅", "likes": "美食",
      "url": "https://www.mafengwo.cn/search/q.php?q=%E4%BC%AF%E5%B0%94%E5%B0%BC%20%E7%BE%8E%E9%A3%9F",
      "takeaway": "Kornhauskeller 巴洛克地窖吃伯恩拼盘（人均CHF 40）；或玫瑰园餐厅看日落"}],
 8: [card("690a55d100000000070341c5", "ABEtSeOAh3g5Sufubl5WL733pqbn6v3oLnSLneD1YpPVw=", "金秋徒步特里贝格瀑布线", 43,
          "瀑布步道金秋最美；主瀑布入口收门票，旁边的自然步道线免费"),
     card("68f8c306000000000302c7a7", "ABtlM2hfVAdfFX0ZrAxN2jxMeNmVPpTWY2YRjlxgKveVE=", "今日复活点：德国黑森林特里贝格", 20,
          "特里贝格咕咕钟商店街比价再买；德国最大咕咕钟在镇外 Schonachbach"),
     {"src": "美食推荐", "title": "黑森林蛋糕：Café Schäfer（特里贝格）", "likes": "美食",
      "url": "https://www.mafengwo.cn/search/q.php?q=%E7%89%B9%E9%87%8C%E8%B4%9D%E6%A0%BC%20%E9%BB%91%E6%A3%AE%E6%9E%97%E8%9B%8B%E7%B3%95",
      "takeaway": "特里贝格 Café Schäfer 号称最正宗黑森林蛋糕（樱桃酒味浓）；晚餐试黑森林火腿"}],
 9: [card("6a6eed70000000002c003a75", "ABxSHCPEsIS2ebwDk8C7yFoZ4H7Ep8-lFyTnMTec7tGwE=", "罗滕堡一日漫游：把中世纪童话与钟声带回家", 42,
          "城墙环城步道免费、可俯瞰红屋顶；Plönlein 小广场清晨人最少"),
     card("6a981511000000001001f2c6", "ABl-C6mF3xD4EC4m6Ypw5WDe2nZybvbZJpV3aoikKkjeg=", "罗滕堡（无滤镜版）", 54,
          "无滤镜真实反馈：白天旅行团多，傍晚和清晨才是罗滕堡的正确打开方式"),
     {"src": "美食推荐", "title": "罗滕堡必吃：雪球 Schneeball + 法兰肯葡萄酒", "likes": "美食",
      "url": "https://www.mafengwo.cn/search/q.php?q=%E7%BD%97%E6%BB%95%E5%A0%A1%20%E7%BE%8E%E9%A3%9F",
      "takeaway": "雪球是油炸面团球（原味/巧克力/杏仁），买一个分食即可；配法兰肯西万尼白葡萄酒"}],
 10: [card("69ff72bb0000000006020518", "ABTsAn1r2iI8qHJTTab43CHGUxnPcnoltGYxAomgb0aBk=", "一整个时代的野心都被画在这段楼梯之上", 603,
          "维尔茨堡主教宫镜厅与提埃坡罗天顶壁画细节讲解——世界文化遗产，进去前建议读这篇"),
      card("69f74846000000003503043d", "AB7uG7nCWlyhkd5OWmvWgNmBdZffdM-c580FFgKnlx_LE=", "巴洛克幻境：维尔茨堡主教宫教堂（附指引）", 163,
          "主教宫内教堂免费区域与参观动线指引；宫殿部分需跟导览"),
      card("69fb7ecf0000000036033ce0", "ABCt5s8MCKWNAc3v8PNlDZY1Bsg-lqRdR9JWpD1LUXhrg=", "维尔茨堡走一圈，归来不看无忧宫", 37,
          "老美因桥端杯葡萄酒看玛丽恩堡是本地人的日常；周日晚桥上有现场音乐")],
 11: [card("6a1b6327000000003502b656", "AB_4Yf3R6aipvJ9zNGIs42f9krM0HaCuWbm9jBVxkhZg4=", "这个德国小镇，不愧登上《孤独星球》封面（巴哈拉赫）", 517,
          "巴哈拉赫：Postenturm 塔顶俯瞰全镇+葡萄园机位；维尔纳小教堂遗址在镇中心"),
      card("6a3eb4fc0000000008030f30", "ABWlAkdIs0KIuHzjCR1jgqsJ0JuQbkTtQ-24Mdo0THubI=", "Bacharach小镇必看攻略！不然累死", 53,
          "镇子是山城，穿舒服的鞋；Postenturm 爬坡15分钟，日落前上去光线最好"),
      card("6948fbd6000000001f00fd5e", "ABt9usv-aUv10MOjlnoIz1cUEpy9b3J9RLMdyGYMGEoXM=", "德国的浪漫，是莱茵河上古堡写成的史诗", 131,
          "莱茵河谷40座古堡的精华段正是你们开的这一段（布劳巴赫-吕德斯海姆）"),
      {"src": "攻略补充", "title": "马克斯堡 Marksburg 导览须知", "likes": "攻略",
       "url": "https://www.mafengwo.cn/search/q.php?q=%E9%A9%AC%E5%85%8B%E6%96%AF%E5%A0%A1",
       "takeaway": "莱茵河谷唯一未被毁的山顶城堡，只能跟导览进入（约€8，英文/德文场次）；旺季周末排队，建议13:00前到"}],
 12: [card("6a64b0d40000000011011b51", "ABN0bMqzWDsU_MwVbVw6Jw7L4ft7mRrNeHUgkj12jReeA=", "吕德斯海姆｜游船+缆车+画眉鸟巷一日游", 36,
          "缆车上海拔223m尼德瓦尔德纪念碑俯瞰莱茵大拐弯；画眉鸟巷雷司令冰酒值得试"),
      card("68bcd2ac000000001c011f45", "ABXQYaNI2sg7RSdEHk4-Q1hRAgH8DwZhdYpHoitcHA128=", "吕德斯海姆一日游（缆车+游船+酒庄）", 39,
          "环线玩法：缆车上山→徒步纪念碑→缆车下山→画眉鸟巷午餐→下午游船"),
      card("6a82eb6a000000002402fcb8", "AB0sWKnFVRDapn_hwYwbMe4MtIoYYjtaRfS70rQqCPDzQ=", "莱茵河｜用这种方式享受最美的一段景色", 53,
          "KD 游船圣戈尔→巴哈拉赫段是古堡最密集段；若体验游船可把上午车停在巴哈拉赫"),
      {"src": "美食推荐", "title": "画眉鸟巷：雷司令白葡萄酒 + 吕德斯海姆咖啡", "likes": "美食",
       "url": "https://www.mafengwo.cn/search/q.php?q=%E5%90%95%E5%BE%B7%E6%96%AF%E6%B5%B7%E5%A7%86%20%E7%BE%8E%E9%A3%9F",
       "takeaway": "Rüdesheimer Kaffee：白兰地点燃后浇咖啡+奶油，是这里的发明；雷司令选半干（Halbtrocken）"}],
 13: [card("68da2784000000001202fcba", "ABdhDj8r7z9q6p0O7rbhT1mUTPx19z9D4iPD4Z9xgrq4Y=", "法兰克福一日游，跟着这18张照片走就行", 1259,
          "罗马广场→大教堂→铁桥→欧元塔经典动线，半天可走完"),
      card("682e945b00000000200285c3", "ABt8NehYZxnqB_D0ZZGVmdOZLsmwu1kf_HE7SqjtrgEvc=", "法兰克福一日Citywalk攻略", 1351,
          "老城+美因河畔+博物馆岸动线；采尔大街购物安排在行程末尾正好"),
      {"src": "美食推荐", "title": "法兰克福必吃：苹果酒 + 绿汁（Green Sauce）", "likes": "美食",
       "url": "https://www.mafengwo.cn/search/q.php?q=%E6%B3%95%E5%85%B0%E5%85%8B%E7%A6%8F%20%E8%8B%B9%E6%9E%9C%E9%85%92",
       "takeaway": "Sachsenhausen 区苹果酒酒馆（Adolf Wagner / Atschel）：绿汁配炸猪排+苹果酒，人均€25；绿汁是7种香草冷酱，本地骄傲"}],
}
for i, cards in add.items():
    days[i].setdefault("xhs", []).extend(cards)

# ---------- 6) 修订记录 ----------
trip.setdefault("revisionNotes", []).append(
    "⑨ v5：慕尼黑两天按'逛得快'实测节奏加可选项（宁芬堡宫/宝马世界/德意志博物馆/阿桑教堂/哈克桥日落）；"
    "修复 D4 主题因内嵌'·'被截断导致苏黎世从标题消失的问题；9/29-10/1 起终点修正为实际住宿地图恩；"
    "10/6 终点由法兰克福机场修正为市区 Westin（还车在 10/7）；补全 D1-D14 dayLabel；"
    "地图 geo 补充 16 个缺失点位（图恩/布里恩茨/施皮茨/特里贝格/博帕德/圣戈尔/巴哈拉赫/上韦瑟尔/洛蕾莱/法兰克福等）；"
    "每日新增小红书高赞笔记与美食/历史类推荐卡片")
trip["generationDate"] = "2026-09-14（v5 修订）"

json.dump(trip, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("tripData.json updated OK")
