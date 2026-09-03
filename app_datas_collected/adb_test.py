import uiautomator2 as u2

class ADB:
    def __init__(self, device_id=None):
        self.d = u2.connect(device_id)
        self.d.set_input_ime(True)

    def _bounds_to_center(self, bounds):
        x1, y1, x2, y2 = bounds
        return (x1 + x2) // 2, (y1 + y2) // 2

    def click(self, x, y):
        self.d.click(x, y)

    def click_by_text(self, text):
        """通过文字点击（精确匹配，无匹配则模糊匹配）"""
        el = self.d(text=text)
        if el.exists:
            el.click()
            return
        el = self.d(textContains=text)
        if el.exists:
            el.click()
            return
        raise ValueError(f'未找到含"{text}"的元素')

    def click_by_desc(self, desc):
        """通过 content-desc 点击（图标常用）"""
        el = self.d(description=desc)
        if el.exists:
            el.click()
            return
        el = self.d(descriptionContains=desc)
        if el.exists:
            el.click()
            return
        raise ValueError(f'未找到content-desc含"{desc}"的元素')

    def click_by_id(self, res_id):
        """通过 resource-id 点击（支持完整或末尾片段）"""
        el = self.d(resourceId=res_id)
        if el.exists:
            el.click()
            return
        # 尝试作为不完整id匹配
        root = self.d.dump_hierarchy()
        from xml.etree import ElementTree as ET
        for node in ET.fromstring(root).iter('node'):
            rid = node.get('resource-id', '')
            if rid.endswith(res_id):
                bounds = node.get('bounds', '')
                cx, cy = self._parse_bounds(bounds)
                self.click(cx, cy)
                return
        raise ValueError(f'未找到id="{res_id}"的元素')

    def click_by_class(self, class_name, index=0):
        """通过 class 名 + 序号点击（如 ImageButton, TextView）"""
        root = self.d.dump_hierarchy()
        from xml.etree import ElementTree as ET
        nodes = [n for n in ET.fromstring(root).iter('node') if n.get('class', '').endswith(class_name)]
        if index < len(nodes):
            bounds = nodes[index].get('bounds', '')
            cx, cy = self._parse_bounds(bounds)
            self.click(cx, cy)
            return
        raise ValueError(f'未找到第{index}个{class_name}')

    def _parse_bounds(self, bounds_str):
        """解析 '[x1,y1][x2,y2]' 格式的 bounds 字符串"""
        parts = bounds_str.replace('[', ' ').replace(']', ' ').replace(',', ' ').split()
        x1, y1, x2, y2 = map(int, parts)
        return (x1 + x2) // 2, (y1 + y2) // 2

    def list_elements(self):
        """列出当前界面所有可交互元素"""
        xml = self.d.dump_hierarchy()
        from xml.etree import ElementTree as ET
        root = ET.fromstring(xml)
        items = []
        seen = set()
        for node in root.iter('node'):
            bounds = node.get('bounds', '')
            cls = node.get('class', '').split('.')[-1]
            text = node.get('text', '')
            desc = node.get('content-desc', '')
            rid_full = node.get('resource-id', '')
            rid = rid_full.split('/')[-1] if '/' in rid_full else rid_full
            key = (text, desc, bounds)
            if key in seen:
                continue
            seen.add(key)
            if cls in ('ImageView', 'ImageButton', 'Button', 'TextView', 'Text', 'EditText', 'FrameLayout'):
                items.append((cls, text, desc, rid, bounds))
        return items

    def text(self, content):
        self.d.send_keys(content)

    def keyevent(self, code):
        self.d.press(code)

    def screenshot(self, path='screenshot.png'):
        self.d.screenshot(path)

    def launch_app(self, pkg, activity=None):
        if activity:
            self.d.app_start(pkg, activity)
        else:
            self.d.app_start(pkg)

    def close_app(self, pkg):
        self.d.app_stop(pkg)

    def back(self):
        self.d.press("back")

    def wait(self, s):
        import time
        time.sleep(s)


if __name__ == '__main__':
    d = ADB()

    print("当前界面所有可交互元素:")
    print(f"{'类':<16} {'文字':<16} {'描述':<24} {'ID':<20} {'坐标'}")
    print("-" * 100)
    for cls, text, desc, rid, bounds in d.list_elements():
        print(f"{cls:<16} {text[:14]:<16} {desc[:22]:<24} {rid[:18]:<20} {bounds}")
