import xml.etree.ElementTree as ET
from datetime import datetime

# region xml操作
def if_match(node, kv_map):
    '''''判断某个节点是否包含所有传入参数属性
       node: 节点
       kv_map: 属性及属性值组成的map'''
    for key in kv_map:
        if node.get(key) != kv_map.get(key):
            return False
    return True

def find_nodes(tree, path):
    '''''查找某个路径匹配的所有节点
       tree: xml树
       path: 节点路径'''
    return tree.findall(path)

def get_node_by_keyvalue(nodelist, kv_map):
    '''''根据属性及属性值定位符合的节点，返回节点
       nodelist: 节点列表
       kv_map: 匹配属性及属性值map'''
    result_nodes = []
    for node in nodelist:
        if if_match(node, kv_map):
            result_nodes.append(node)
    return result_nodes

def change_node_properties(node, kv_map, is_delete=False):
    '''''修改/增加 /删除 节点的属性及属性值
       nodelist: 节点
       kv_map:属性及属性值map'''
    for key in kv_map:
        if is_delete:
            if key in node.attrib:
                del node.attrib[key]
        else:
            node.set(key, kv_map.get(key))

def change_node_text(node, text, is_add=False, is_delete=False):
    '''''改变/增加/删除一个节点的文本
       nodelist:节点
       text : 更新后的文本'''
    if is_add:
        node.text += text
    elif is_delete:
        node.text = ""
    else:
        node.text = text
# endregion


class CfgClass:
    '''对应CFG的参数'''
    def __init__(self):
        self.DeviceId="TK-Default"
        self.UpdateTime = "2024-05-17 12:00:00"
        #相机0-向前的
        self.IntrinsicMatrix_0=['3388.20829','0.00000','1601.46233',
                                '0.00000','3392.76827','2413.27527',
                                '0.0','0.0','1.0']
        self.DistCoeffs_0=['-0.0211544042','0.146641772','0.0008582','0.00008454']
        self.CameraTransVec_0=['-0.115','0.037','-0.022']
        self.CameraRotVec_0=['0.99','1.5','-1.499']
        # 相机1-向上的
        self.IntrinsicMatrix_1 = ['3423.18414', '0.00000', '1589.45486',
                                  '0.00000', '3424.46322', '2404.22227',
                                  '0.0', '0.0', '1.0']
        self.DistCoeffs_1 = ['0.01897944', '-0.00088049', '-0.00207076', '-0.00268095']
        self.CameraTransVec_1 = ['0.094', '-0.004', '0.239']
        self.CameraRotVec_1 = ['0.356', '0.510', '-1.877']

        #雷达
        self.LidarOffsetVec=['0.0','0.0','0.0027']
        self.LidarInstallRotAngle=['-0.16','0.0','20.17']

        #全站仪
        self.TotalStationOffsetVec=['0.0','0.0','0.2663']
        self.TotalStationOffsetAngle = ['0.0', '0.0', '83.8822']

        #倾角仪
        self.LinometerCalibAngle=["-0.04","0.787"]

        #激光指点
        self.LaserOffsetVec=['0.0','0.036','0.0']
        self.LaserOffsetAngle='-0.534'
        self.MinMotorOffsetAngle='35.3'
        self.tree=None


    def readFromCFG(self,path):
        self.tree = ET.parse(path)
        # 根节点
        root = self.tree.getroot()
        # 标签名
        print('root_tag:', root.tag)
        if "DeviceID" in root.attrib:
            self.DeviceId=root.attrib["DeviceID"]
        else:
            print("未找到DeviceID")
        if "UpdateTime" in root.attrib:
            self.UpdateTime=root.attrib["UpdateTime"]
        else:
            print("未找到UpdateTime")


        for item in root:
            # 属性值
            if item.tag=="SonyCameraMatries":#解析相机的
                for item_1 in item:
                    print(item_1.tag)
                    is0=False
                    for need_item in item_1:
                        if need_item.tag=="CameraID":
                            if need_item.text=='0':
                                is0=True
                            else:
                                is0=False
                        elif need_item.tag=="IntrinsicMatrix":
                            temp_list=[need_item.attrib["X00"],need_item.attrib["X01"],need_item.attrib["X02"],
                                       need_item.attrib["X10"],need_item.attrib["X11"],need_item.attrib["X12"],
                                       need_item.attrib["X20"],need_item.attrib["X21"],need_item.attrib["X22"]]
                            if is0:
                                self.IntrinsicMatrix_0=temp_list
                            else:
                                self.IntrinsicMatrix_1=temp_list
                        elif need_item.tag=="DistCoeffs":
                            temp_list=[need_item.attrib["X"],need_item.attrib["Y"],need_item.attrib["Z"],need_item.attrib["W"]]
                            if is0:
                                self.DistCoeffs_0=temp_list
                            else:
                                self.DistCoeffs_1=temp_list
                        elif need_item.tag=="CameraTransVec":
                            temp_list=[need_item.attrib["X"],need_item.attrib["Y"],need_item.attrib["Z"]]
                            if is0:
                                self.CameraTransVec_0=temp_list
                            else:
                                self.CameraTransVec_1=temp_list
                        elif need_item.tag=="CameraRotVec":
                            temp_list=[need_item.attrib["X"],need_item.attrib["Y"],need_item.attrib["Z"]]
                            if is0:
                                self.CameraRotVec_0=temp_list
                            else:
                                self.CameraRotVec_1=temp_list
            elif item.tag=="LidarOffsetVec":
                print(item.attrib)
                self.LidarOffsetVec=[item.attrib["X"],item.attrib["Y"],item.attrib["Z"]]
            elif item.tag=="LinometerCalibAngle":
                print(item.attrib)
                self.LinometerCalibAngle=[(item.attrib["X"]),item.attrib["Y"]]
            elif item.tag=="LidarInstallRotAngleX":
                print(item.attrib)
                self.LidarInstallRotAngle[0]=item.text
            elif item.tag=="LidarInstallRotAngleY":
                print(item.attrib)
                self.LidarInstallRotAngle[1]=item.text
            elif item.tag=="LidarInstallRotAngleZ":
                print(item.attrib)
                self.LidarInstallRotAngle[2]=item.text
            elif item.tag=="TotalStationOffsetVec":
                print(item.attrib)
                self.TotalStationOffsetVec=[item.attrib["X"],item.attrib["Y"],item.attrib["Z"]]
            elif item.tag=="TotalStationOffsetAngle":
                print(item.attrib)
                self.TotalStationOffsetAngle=[item.attrib["X"],item.attrib["Y"],item.attrib["Z"]]
            elif item.tag == "LaserOffsetAngle":
                print(item.attrib)
                self.LaserOffsetAngle = item.text
            elif item.tag == "MinMotorOffsetAngle":
                print(item.attrib)
                self.MinMotorOffsetAngle = item.text

    def corret_file_cfg(self,radar_x,radar_z):
        self.LidarInstallRotAngle[0] = str(radar_x)
        self.LidarInstallRotAngle[2] = str(radar_z)

    def inc_file_cfg(self,inc_x,inc_z):
        self.LinometerCalibAngle[0] = str(inc_x)
        self.LinometerCalibAngle[1] = str(inc_z)

    def total_station_angle_cfg(self,total_angle):
        self.TotalStationOffsetAngle[2] = str(total_angle)


    def saveFile(self,path):
        '''
        将数据写回去
        :param path:
        :return:
        '''
        current_time = datetime.now()
        self.UpdateTime=current_time.strftime('%Y-%m-%d %H:%M:%S')

        root = self.tree.getroot()
        root.attrib["DeviceID"]=self.DeviceId
        root.attrib["UpdateTime"]=self.UpdateTime


        nodes = find_nodes(self.tree, "SonyCameraMatries/SonyCameraInfo")
        for node in nodes:
            is0 = False
            for need_item in node:
                if need_item.tag == "CameraID":
                    if need_item.text == '0':
                        is0 = True
                    else:
                        is0 = False
                elif need_item.tag == "IntrinsicMatrix":
                    temp_values=self.IntrinsicMatrix_0
                    if not is0:
                        temp_values = self.IntrinsicMatrix_1
                    change_node_properties(need_item,{"X00":temp_values[0]})
                    change_node_properties(need_item, {"X01": temp_values[1]})
                    change_node_properties(need_item, {"X02": temp_values[2]})
                    change_node_properties(need_item, {"X10": temp_values[3]})
                    change_node_properties(need_item, {"X11": temp_values[4]})
                    change_node_properties(need_item, {"X12": temp_values[5]})
                    change_node_properties(need_item, {"X20": temp_values[6]})
                    change_node_properties(need_item, {"X21": temp_values[7]})
                    change_node_properties(need_item, {"X22": temp_values[8]})
                elif need_item.tag == "DistCoeffs":
                    temp_values=self.DistCoeffs_0
                    if not is0:
                        temp_values = self.DistCoeffs_1
                    change_node_properties(need_item,{"X":temp_values[0]})
                    change_node_properties(need_item, {"Y": temp_values[1]})
                    change_node_properties(need_item, {"Z": temp_values[2]})
                    change_node_properties(need_item, {"W": temp_values[3]})
                elif need_item.tag == "CameraTransVec":
                    temp_values=self.CameraTransVec_0
                    if not is0:
                        temp_values = self.CameraTransVec_1
                    change_node_properties(need_item,{"X":temp_values[0]})
                    change_node_properties(need_item, {"Y": temp_values[1]})
                    change_node_properties(need_item, {"Z": temp_values[2]})
                elif need_item.tag == "CameraRotVec":
                    temp_values=self.CameraRotVec_0
                    if not is0:
                        temp_values = self.CameraRotVec_1
                    change_node_properties(need_item,{"X":temp_values[0]})
                    change_node_properties(need_item, {"Y": temp_values[1]})
                    change_node_properties(need_item, {"Z": temp_values[2]})
        nodes=find_nodes(self.tree, "LidarOffsetVec")
        change_node_properties(nodes[0],{"X":self.LidarOffsetVec[0]})
        change_node_properties(nodes[0], {"Y": self.LidarOffsetVec[1]})
        change_node_properties(nodes[0], {"Z": self.LidarOffsetVec[2]})
        nodes=find_nodes(self.tree, "LinometerCalibAngle")
        change_node_properties(nodes[0],{"X":self.LinometerCalibAngle[0]})
        change_node_properties(nodes[0], {"Y": self.LinometerCalibAngle[1]})
        nodes=find_nodes(self.tree, "LaserOffsetVec")
        change_node_properties(nodes[0],{"X":self.LaserOffsetVec[0]})
        change_node_properties(nodes[0], {"Y": self.LaserOffsetVec[1]})
        change_node_properties(nodes[0], {"Z": self.LaserOffsetVec[2]})
        nodes = find_nodes(self.tree, "LaserOffsetAngle")
        change_node_text(nodes[0],self.LaserOffsetAngle)
        nodes = find_nodes(self.tree, "MinMotorOffsetAngle")
        change_node_text(nodes[0], self.MinMotorOffsetAngle)
        nodes = find_nodes(self.tree, "LidarInstallRotAngleX")
        change_node_text(nodes[0], self.LidarInstallRotAngle[0])
        nodes = find_nodes(self.tree, "LidarInstallRotAngleY")
        change_node_text(nodes[0], self.LidarInstallRotAngle[1])
        nodes = find_nodes(self.tree, "LidarInstallRotAngleZ")
        change_node_text(nodes[0], self.LidarInstallRotAngle[2])
        nodes=find_nodes(self.tree, "TotalStationOffsetVec")
        change_node_properties(nodes[0],{"X":self.TotalStationOffsetVec[0]})
        change_node_properties(nodes[0], {"Y": self.TotalStationOffsetVec[1]})
        change_node_properties(nodes[0], {"Z": self.TotalStationOffsetVec[2]})
        nodes=find_nodes(self.tree, "TotalStationOffsetAngle")
        change_node_properties(nodes[0],{"X":self.TotalStationOffsetAngle[0]})
        change_node_properties(nodes[0], {"Y": self.TotalStationOffsetAngle[1]})
        change_node_properties(nodes[0], {"Z": self.TotalStationOffsetAngle[2]})

        self.tree.write(path, encoding="utf-8", xml_declaration=True)
        #cfg=CfgClass()
#cfg.readFromCFG(r"E:\Code\GitSource\tk_set_clac_exe\ConfigData-TkSel_new.cfg")
#print(cfg)




