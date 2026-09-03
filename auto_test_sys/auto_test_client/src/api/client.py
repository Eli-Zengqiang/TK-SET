import requests
import json
from typing import Dict, Any, Optional
from urllib.parse import urljoin


class APIClient:
    """API客户端"""
    
    def __init__(self, base_url: str, timeout: int = 120):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = self.base_url+endpoint
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            
            # 尝试解析JSON响应
            try:
                return response.json()
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "message": "Request completed",
                    "data": response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Request failed: {str(e)}",
                "error": str(e)
            }
    
    # 测试相关API
    def ping(self) -> Dict[str, Any]:
        """心跳检测"""
        return self._make_request("GET", "/test/ping")
    
    def echo(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """数据回显"""
        return self._make_request("POST", "/test/echo", json=data)
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return self._make_request("GET", "/test/status")
    
    # 系统管理API
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return self._make_request("GET", "/system/info")
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        return self._make_request("GET", "/system/metrics")
    
    def get_battery_status(self) -> Dict[str, Any]:
        """获取电池状态"""
        return self._make_request("GET", "/system/battery")
    
    def get_tf_card_status(self) -> Dict[str, Any]:
        """获取TF卡状态"""
        return self._make_request("GET", "/system/tf-card-status")
    
    # 设备状态API
    def get_devices_status(self) -> Dict[str, Any]:
        """获取所有设备状态"""
        return self._make_request("GET", "/devices/status")
    
    # 电源管理API
    def power_on(self, module: str) -> Dict[str, Any]:
        """给指定模块上电"""
        return self._make_request("POST", "/devices/power/on", json={"module": module})
    
    def power_off(self, module: str) -> Dict[str, Any]:
        """给指定模块断电"""
        return self._make_request("POST", "/devices/power/off", json={"module": module})
    
    def get_power_status(self, module: str) -> Dict[str, Any]:
        """获取指定模块电源状态"""
        return self._make_request("GET", f"/devices/power/status/{module}")
    
    def power_on_all(self) -> Dict[str, Any]:
        """给所有模块上电"""
        return self._make_request("POST", "/devices/power/on-all")
    
    def power_off_all(self) -> Dict[str, Any]:
        """给所有模块断电"""
        return self._make_request("POST", "/devices/power/off-all")

    # === 配置管理API (新增) ===
    def wifi_setup(self) -> Dict[str, Any]:
        """配置WiFi SSID"""
        return self._make_request("POST", "/devices/config/wifi-setup")

    def sync_system_time(self, target_time: str) -> Dict[str, Any]:
        """同步系统时间"""
        return self._make_request("POST", "/devices/config/time-sync", json={"target_time": target_time})

    def motor_configure(self) -> Dict[str, Any]:
        """配置转台参数"""
        return self._make_request("POST", "/devices/motor/configure")

    def min_motor_configure(self) -> Dict[str, Any]:
        """配置小电机参数"""
        return self._make_request("POST", "/devices/min-motor/configure")

    def lidar_setup(self) -> Dict[str, Any]:
        """雷达初始化设置"""
        return self._make_request("POST", "/devices/lidar/setup")

    def setup_all_devices(self) -> Dict[str, Any]:
        """一键配置所有设备"""
        return self._make_request("POST", "/devices/setup/all-devices")


    # 电机控制API
    def motor_find_zero(self, timeout: int = 60) -> Dict[str, Any]:
        """转台找零位"""
        return self._make_request("POST", "/devices/motor/find-zero", json={"timeout": timeout})
    
    def motor_set_position(self, position: float, timeout: int = 60) -> Dict[str, Any]:
        """设置转台位置"""
        return self._make_request("POST", "/devices/motor/set-position", 
                                json={"position": position, "timeout": timeout})
    
    def motor_set_speed(self, speed: float) -> Dict[str, Any]:
        """设置转台速度"""
        return self._make_request("POST", "/devices/motor/set-speed", json={"speed": speed})
    
    def motor_get_angle(self, timeout: int = 60) -> Dict[str, Any]:
        """读取转台当前角度"""
        return self._make_request("GET", "/devices/motor/get-angle", json={"timeout": timeout})
    
    def min_motor_set_angle(self, angle: float, timeout: int = 60) -> Dict[str, Any]:
        """设置小电机角度"""
        return self._make_request("POST", "/devices/min-motor/set-angle",
                                json={"angle": angle, "timeout": timeout})
    
    def min_motor_relative_move(self, delta_angle: float, timeout: int = 30) -> Dict[str, Any]:
        """小电机相对移动"""
        return self._make_request("POST", "/devices/min-motor/relative-move",
                                json={"angle": delta_angle, "timeout": timeout})
    
    def min_motor_read_angle(self) -> Dict[str, Any]:
        """读取小电机角度"""
        return self._make_request("GET", "/devices/min-motor/read-angle")
    
    def min_motor_detect_limits(self, max_rotation: int = 300, timeout: int = 60) -> Dict[str, Any]:
        """检测小电机限位角度"""
        return self._make_request("POST", "/devices/min-motor/detect-limits",
                                json={"max_rotation": max_rotation, "timeout": timeout})
    
    # 相机控制API
    def get_camera_resolutions(self) -> Dict[str, Any]:
        """获取相机分辨率列表"""
        return self._make_request("GET", "/devices/camera/resolutions")
    
    def camera_set_resolution(self, device: str, mode: str) -> Dict[str, Any]:
        """设置相机分辨率"""
        return self._make_request("POST", "/devices/camera/set-resolution",
                                json={"device": device, "mode": mode})
    
    def camera_capture(self, device: str, filename: str) -> Dict[str, Any]:
        """相机拍照"""
        return self._make_request("POST", "/devices/camera/capture",
                                json={"device": device, "filename": filename})
    
    def camera_set_and_capture(self, device: str, mode: str, filename: str) -> Dict[str, Any]:
        """设置分辨率并拍照"""
        return self._make_request("POST", "/devices/camera/set-and-capture",
                                json={"device": device, "mode": mode, "filename": filename})
    
    # LED控制API
    def led_set_color(self, color: str) -> Dict[str, Any]:
        """设置LED颜色"""
        return self._make_request("POST", "/devices/led/set-color", json={"color": color})
    
    def led_set_custom_color(self, red: int, green: int, blue: int) -> Dict[str, Any]:
        """设置LED自定义颜色"""
        return self._make_request("POST", "/devices/led/set-custom-color",
                                json={"red": red, "green": green, "blue": blue})
    
    def led_turn_off(self) -> Dict[str, Any]:
        """关闭LED"""
        return self._make_request("POST", "/devices/led/turn-off")
    
    # 雷达控制API
    def lidar_get_sn(self) -> Dict[str, Any]:
        """获取雷达序列号"""
        return self._make_request("GET", "/devices/lidar/sn")
    
    def lidar_get_calibration(self) -> Dict[str, Any]:
        """获取雷达校准数据"""
        return self._make_request("GET", "/devices/lidar/calibration")
    
    def lidar_setup(self) -> Dict[str, Any]:
        """雷达初始化设置"""
        return self._make_request("POST", "/devices/lidar/setup")

    # 倾角仪控制API
    def inclinometer_read(self) -> Dict[str, Any]:
        """读取倾角仪数据"""
        return self._make_request("GET", "/devices/inclinometer/read")

    # 屏幕测试 API
    def run_screen_test(self) -> Dict[str, Any]:
        """运行屏幕测试"""
        return self._make_request("POST", "/devices/screen-test/run")
    
    def get_screen_test_status(self) -> Dict[str, Any]:
        """获取屏幕测试程序状态"""
        return self._make_request("GET", "/devices/screen-test/status")

    # 文件管理API
    def get_file_md5(self, filename: str, path: Optional[str] = None) -> Dict[str, Any]:
        """获取文件MD5"""
        params = {"path": path} if path else {}
        return self._make_request("GET", f"/files/md5/{filename}", params=params)
    
    def download_file(self, filename: str, save_path: str, remote_path: Optional[str] = None) -> Dict[str, Any]:
        """下载文件"""
        try:
            # 构建下载URL
            url = f"{self.base_url}/files/download/{filename}"
            if remote_path:
                url += f"?path={remote_path}"
            else:
                url += "?path=/app/auto_test_server/"
            
            # 发送GET请求下载文件
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 确保保存目录存在
            import os
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 保存文件
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return {
                "success": True,
                "message": "文件下载成功",
                "data": {
                    "filename": filename,
                    "save_path": save_path,
                    "size": len(response.content)
                }
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"文件下载失败: {str(e)}",
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"文件保存失败: {str(e)}",
                "error": str(e)
            }


class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self):
        self.test_results = []
    
    def add_result(self, module: str, test_name: str, result: Dict[str, Any]):
        """添加测试结果"""
        self.test_results.append({
            "module": module,
            "test_name": test_name,
            "result": result,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
    
    def generate_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results 
                          if result["result"].get("success", False))
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "pass_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            "details": self.test_results,
            "generated_at": __import__('datetime').datetime.now().isoformat()
        }