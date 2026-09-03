"""
Android ADB 自动化脚本 - 隧道扫描仪 SmartEye 完整操作流程
流程：启动App → 连接WiFi → 选择模式 → 开始采集 → 数据分析 → 文件比对
"""
import io, sys, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from xml.etree import ElementTree as ET
import uiautomator2 as u2

# ----- 模式选择 -----
# 命令行参数：0=隧道点云，1=地质模型（默认）
MODE = int(sys.argv[1]) if len(sys.argv) > 1 else 1
MODE_NAME = ["隧道点云", "地质模型"][MODE]

# 连接到 Android 设备（单设备无需指定序列号）
dev = u2.connect()

# ----- 工具函数 -----

def all_texts():
    """获取当前屏幕所有可见文本"""
    xml = dev.dump_hierarchy()
    root = ET.fromstring(xml)
    return [n.get("text", "") for n in root.iter("node") if n.get("text", "")]

def text_clicks(*targets):
    """按文本点击，支持精确匹配和包含匹配"""
    for t in targets:
        el = dev(text=t)
        if el.exists:
            el.click()
            print(f"  ✅ 点击: {t}")
            return True
        el = dev(textContains=t)
        if el.exists:
            el.click()
            print(f"  ✅ 点击(包含): {t}")
            return True
    return False

def dump(title=""):
    """打印当前屏幕 UI 层次（调试用）"""
    if title:
        print(f"\n{'='*50}\n  {title}\n{'='*50}")
    xml = dev.dump_hierarchy()
    root = ET.fromstring(xml)
    seen = set()
    for node in root.iter("node"):
        text = node.get("text", "")
        rid_full = node.get("resource-id", "")
        rid = rid_full.split("/")[-1] if "/" in rid_full else rid_full
        bounds = node.get("bounds", "")
        cls = node.get("class", "").split(".")[-1]
        if not text and not rid:
            continue
        key = (text, bounds)
        if key in seen:
            continue
        seen.add(key)
        if cls in ("ImageView", "ImageButton", "Button", "TextView", "Text", "EditText", "FrameLayout", "Switch"):
            print(f"  {cls:<12} text={text[:20]:<20} id={rid[:22]:<22} {bounds}")

# ----- 启动 App -----
print(f"=== 启动 app（模式: {MODE_NAME}）===")
dev.app_start('com.tunnelkey.smarteye', '.refactor.core_app.main.MainActivity')
time.sleep(3)

# ================================================================
# 1. 连接 WiFi：点击主界面"设备连接"卡片 → 弹窗 → 点"切换"进入 WLAN 设置
# ================================================================
print(f"\n[1/6] 连接设备 → 切换 WiFi")
# 点击 WiFi 连接图标（ImageView），触发"是否切换 WiFi"对话框
card = dev(resourceId="com.tunnelkey.smarteye:id/connectWifiImg")
if card.exists:
    card.click()
else:
    dev.click(204, 1435)
time.sleep(2)

# 如果有"切换"文字，点击切换到 WLAN 设置页
texts = all_texts()
if any("切换" in t for t in texts):
    text_clicks("切换")
    time.sleep(2)

# ================================================================
# 2. 连接 TK-SMARTEYE-V2 设备 WiFi
#    - 如果 WiFi 关闭则打开
#    - 在可用网络列表中找到 TK-SMARTEYE-V2 并连接（密码 12345678）
#    - 如果已连接则跳过
# ================================================================
print(f"\n[2/6] 连接 TK-SMARTEYE-V2 WiFi")
# 打开 WiFi 开关（如果处于关闭状态）
switch = dev(className="android.widget.Switch")
if switch.exists and switch.info.get("checked") == False:
    switch.click()
    print("  WiFi 已打开")
    time.sleep(3)

# 扫描可用网络，找到 TK-SMARTEYE-V2 开头的 WiFi
wifi_name = None
for retry in range(2):
    texts = all_texts()
    wifi_name = next((t for t in texts if t.startswith("TK-SMARTEYE-V2")), None)
    if wifi_name:
        break
    time.sleep(5)

if wifi_name:
    print(f"  找到: {wifi_name}")
    # 点击该 WiFi 名称，弹出连接对话框
    dev(text=wifi_name).click()
    time.sleep(2)
    texts = all_texts()
    if "连接" in texts:
        text_clicks("连接")           # 点击"连接"按钮
        time.sleep(3)
        print("  ✅ 已连接到", wifi_name)
    else:
        print(f"  {wifi_name} 已连接，跳过")
else:
    print("  ⚠️ 未找到 TK-SMARTEYE-V2 WiFi")

# ================================================================
# 3. 从 WLAN 设置返回 App
#    - 尝试各种方式找到返回按钮（文字描述、ImageButton、坐标）
#    - 如果已不在 App 则重新启动
# ================================================================
print(f"\n[3/6] 返回 app")
back_clicked = False
# 按文字描述查找返回按钮
for desc in ["转到上一层级", "返回", "Navigate up"]:
    el = dev(description=desc)
    if el.exists:
        el.click()
        back_clicked = True
        break
# 按 ImageButton 类型查找
if not back_clicked:
    for btn in dev(className="android.widget.ImageButton"):
        btn.click()
        back_clicked = True
        break
# 按 contentDescription 含"返回"查找
if not back_clicked:
    for btn in dev(className="android.widget.Button"):
        cd = btn.info.get("contentDescription", "")
        if "back" in cd.lower() or "返回" in cd:
            btn.click()
            back_clicked = True
            break
# 坐标点击左上角（通用返回位置）
if not back_clicked:
    print("  ⚠️ 未找到返回按钮，尝试坐标(40,100)")
    dev.click(40, 100)
    back_clicked = True
time.sleep(1)
# 如果返回后不在 App 中，重新启动
if dev.app_current().get("package") != "com.tunnelkey.smarteye":
    dev.app_start('com.tunnelkey.smarteye', '.refactor.core_app.main.MainActivity')
    time.sleep(2)

# ================================================================
# 4. 选择扫描模式：点击顶部菜单 → 选择"隧道点云"或"地质模型"
#    - 菜单按钮是右上角的 secondOptionImg
#    - 选择模式后可能进入配置页面，需要按返回回到主界面
# ================================================================
print(f"\n[4/6] 选择模式: {MODE_NAME}")
# 点击右上角菜单图标（三横线）
menu = dev(resourceId="com.tunnelkey.smarteye:id/secondOptionImg")
if menu.exists:
    menu.click()
else:
    dev.click(988, 200)
time.sleep(2)

# 从弹出的菜单中点击模式名称
text_clicks(MODE_NAME)
time.sleep(2)

# 选择模式后可能进入配置页，需要回到主界面
print("  返回主界面...")
back_clicked = False
for desc in ["转到上一层级", "返回", "Navigate up"]:
    el = dev(description=desc)
    if el.exists:
        el.click()
        back_clicked = True
        break
if not back_clicked:
    for btn in dev(className="android.widget.ImageButton"):
        btn.click()
        back_clicked = True
        break
if not back_clicked:
    dev.press("back")
    time.sleep(1)
time.sleep(2)

# ================================================================
# 5. 开始采集
#    - 点击采集按钮 → 处理"设置站点"/"选择工点"弹窗
#    - 等待采集完成（超时 10 分钟）
#    - 检查"采集完成 文件检查"弹窗（异常时下载缺少文件）
#    - 验证图片/激光/其他文件数是否符合预期
# ================================================================
COLLECT_START = True
if COLLECT_START:
    print(f"\n[5/6] 开始采集（模式: {MODE_NAME}）")

    def click_start():
        """点击采集按钮，弹站点/工点则点确定。返回 True 表示已进入采集状态"""
        # 多种方式点击开始采集（ImageView → TextView → 文字 → 坐标）
        clicked = False
        img = dev(resourceId="com.tunnelkey.smarteye:id/startCollectImg")
        if img.exists:
            img.click()
            clicked = True
            print("  点击 startCollectImg")
        if not clicked:
            tv = dev(resourceId="com.tunnelkey.smarteye:id/collectStatusTv")
            if tv.exists:
                tv.click()
                clicked = True
                print("  点击 collectStatusTv")
        if not clicked:
            for t in ["开始采集", "停止采集"]:
                el = dev(text=t)
                if el.exists:
                    el.click()
                    clicked = True
                    print(f"  点击文字: {t}")
                    break
        if not clicked:
            dev.click(879, 1435)
            print("  坐标点击(879,1435)")
        time.sleep(2)

        # 处理"设置站点"或"选择工点"弹窗 → 点确定
        texts = all_texts()
        for kw in ["设置站点", "选择工点"]:
            if kw in texts:
                for sel in [f'{kw}.*确定', '确定']:
                    el = dev(text=sel)
                    if el.exists:
                        el.click()
                        print(f"  点击确定({kw})")
                        break
                else:
                    dev(text="确定").click()
                    print(f"  点击确定({kw})")
                time.sleep(2)

        # 验证是否进入采集状态（按钮变为"停止采集"/"采集中"）
        for _ in range(5):
            texts = all_texts()
            if any(t in texts for t in ["停止采集", "采集中"]):
                return True
            time.sleep(1)
        return False

    def read_file_counts():
        """从屏幕读取图片/激光/其他文件数，返回 (pic, laser, cfg) 或 None"""
        for _ in range(5):
            xml = dev.dump_hierarchy()
            root = ET.fromstring(xml)
            pic = laser = cfg = ""
            for node in root.iter("node"):
                rid = node.get("resource-id", "")
                text = node.get("text", "")
                if "pictureNumberTv" in rid:
                    pic = text
                elif "laserNumberTv" in rid:
                    laser = text
                elif "configNumberTv" in rid:
                    cfg = text
            if pic and laser and cfg:
                return pic, laser, cfg
            time.sleep(2)
        return None

    def is_collecting():
        """判断当前是否正在采集中"""
        texts = all_texts()
        return any(t in texts for t in ["停止采集", "采集中"])

    def is_idle():
        """判断当前是否空闲（按钮显示"开始采集"）"""
        return "开始采集" in all_texts()

    WAIT_TIMEOUT = 600  # 最长等10分钟

    # 5a. 如果正在采集则等待完成
    if is_collecting():
        print("  检测到正在采集，等待完成...")
        deadline = time.time() + WAIT_TIMEOUT
        while time.time() < deadline:
            time.sleep(5)
            if is_idle() and not is_collecting():
                break
        done = is_idle() and not is_collecting()
        print("  采集已完成" if done else "  ⚠️ 等待超时")
    else:
        # 5b. 启动采集
        if not click_start():
            print("  ❌ 无法启动采集")
            sys.exit(1)
        print("  采集已启动")
        deadline = time.time() + WAIT_TIMEOUT
        while time.time() < deadline:
            time.sleep(5)
            if is_idle() and not is_collecting():
                break
        done = is_idle() and not is_collecting()
        print("  采集完成" if done else "  超时")

    # 5c. 采集完成后检查弹窗 & 文件数
    time.sleep(2)
    texts = all_texts()

    # 检查"采集完成 文件检查"弹窗（数据异常时出现）
    if any("采集完成" in t or "文件检查" in t for t in texts):
        print("\n  数据传输存在异常")
        # 点击"下载缺少文件"按钮
        for text in ["下载缺少文件", "下载缺少", "下载"]:
            el = dev(text=text)
            if el.exists:
                el.click()
                print(f"  ✅ 点击: {text}")
                break
        else:
            dev(textContains="下载").click()
            print("  ✅ 点击: 下载")
        time.sleep(2)

    # 读取并验证文件数
    counts = read_file_counts()
    if counts is None:
        print("\n  ⚠️ 未找到文件数控件")
    else:
        pic, laser, cfg = counts
        expected = {"图片文件": "0/0" if MODE == 0 else "18/18",
                    "激光文件": "13/13", "其他文件": "3/3"}
        actual = {"图片文件": pic, "激光文件": laser, "其他文件": cfg}
        print(f"  期望: {expected}")
        print(f"  实际: {actual}")
        if all(actual[k] == expected[k] for k in expected):
            print("  ✅ 文件数正常")
        else:
            for k in expected:
                if actual.get(k) != expected[k]:
                    print(f"  ❌ {k}: 期望 {expected[k]}, 实际 {actual[k]}")

# ================================================================
# 6. 数据分析 → 文件比对
#    - 切换到"数据分析"底部 tab
#    - 点击第一行"待合成"右侧的四个竖点（moreBtn）
#    - 在弹出的菜单中选择"文件比对"
#    - 根据比对结果：
#        - 本地文件完整 → 点击"检查完成"
#        - 文件缺失     → 打印提示，点击"关闭"
# ================================================================
print(f"\n[6/6] 数据分析 → 文件比对")

# 6a. 点击"数据分析"底部 tab
tab = dev(text="数据分析")
if not tab.exists:
    tab = dev(textContains="数据分析")
if tab.exists:
    tab.click()
else:
    dev.click(406, 2354)  # tab 居中坐标
print("  ✅ 点击: 数据分析")
time.sleep(3)

# 6b. 点击第一行"待合成"旁边的四个竖点（moreBtn，text="...."）
more = dev(resourceId="com.tunnelkey.smarteye:id/moreBtn")
if more.exists:
    more.click()
    print("  ✅ 点击: moreBtn（四个竖点）")
else:
    dev.click(976, 387)  # 坐标 fallback: 第一行 moreBtn 中心 [943,358][1009,418]
time.sleep(2)

# 6c. 在弹出的菜单中选择"文件比对"
for t in ["文件比对", "文件对比"]:
    el = dev(text=t)
    if not el.exists:
        el = dev(textContains=t)
    if el.exists:
        el.click()
        print(f"  ✅ 点击: {t}")
        break
time.sleep(2)

# 6d. 根据比对弹窗结果做处理
texts = all_texts()
if any("本地文件完整" in t for t in texts):
    # 文件完整 → 点"检查完成"
    print("\n  本地文件完整，无需重新下载")
    for t in ["检查完成", "完成", "确定"]:
        el = dev(text=t)
        if el.exists:
            el.click()
            print(f"  ✅ 点击: {t}")
            break
elif any("缺少" in t or "缺失" in t for t in texts):
    # 文件缺失 → 打印提示并关闭
    print("\n  文件缺失")
    for t in ["关闭", "取消", "确定"]:
        el = dev(text=t)
        if el.exists:
            el.click()
            print(f"  ✅ 点击: {t}")
            break

print("\n✅ 脚本执行完毕")
