import xml.etree.ElementTree as ET

# 创建根元素
root = ET.Element("root")

# 创建子元素并添加到根元素
child1 = ET.SubElement(root, "child1")
child1.text = "This is child 1"

child2 = ET.SubElement(root, "child2")
child2.set("attribute", "value")
child2.text = "This is child 2 with an attribute"

# 创建嵌套子元素
nested_child = ET.SubElement(child2, "nested_child")
nested_child.text = "This is a nested child"

# 创建ElementTree对象
tree = ET.ElementTree(root)

# 将XML结构写入文件
with open("../output.xml", "wb") as file:
    tree.write(file, encoding='utf-8', xml_declaration=True)

print("XML文件已生成并写入 output.xml")