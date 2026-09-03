from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, Optional, List
import time
from datetime import datetime
from pathlib import Path

from app.utils.logger import app_logger
from app.core.power_manager import PowerManager
from app.core.Motor import Motor
from app.core.minMotor import MinMotor
from app.core.lidar_http import set_ptp, set_return_mode, get_sn, get_calib
from app.core.Inclinometer import Inclinometer
from app.core.config_manager import configure_wifi_ssid, update_system_time
from app.core.device_settings import lidar_setting, motor_setting, min_motor_setting
from app.core.new_camera import set_resolution, capture_image, is_image_valid, RESOLUTIONS
from app.core.led import LEDController
from app.core.screen_tester import ScreenTester

router = APIRouter()

# 初始化设备管理器
power_manager = PowerManager()
led_controller = LEDController()
motor_manager = MinMotor()

@router.get("/status")
async def get_devices_status() -> Dict[str, Any]:
    """获取所有设备状态"""
    try:
        status = {
            "power_modules": {},
            "timestamp": time.time()
        }
        
        # 检查各模块电源状态
        modules = ['radar', 'motor', 'zt', 'laser', 'inc', 'camera1', 'camera2', 'led']
        for module in modules:
            try:
                status["power_modules"][module] = power_manager.check_power_status(module)
            except Exception as e:
                status["power_modules"][module] = f"Error: {str(e)}"
        
        app_logger.info("Devices status retrieved successfully")
        return {
            "success": True,
            "message": "Devices status retrieved",
            "data": status
        }
        
    except Exception as e:
        app_logger.error(f"Get devices status failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 电源管理API ====================
@router.post("/power/on")
async def power_on_module(module: str = Body(..., embed=True)) -> Dict[str, Any]:
    """给指定模块上电"""
    try:
        result = power_manager.power_on(module)
        if result:
            app_logger.info(f"Module {module} powered on successfully")
            return {
                "success": True,
                "message": f"Module {module} powered on successfully",
                "data": {"module": module, "status": "on"}
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to power on module {module}")
            
    except Exception as e:
        app_logger.error(f"Power on module {module} failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/power/off")
async def power_off_module(module: str = Body(..., embed=True)) -> Dict[str, Any]:
    """给指定模块断电"""
    try:
        result = power_manager.power_off(module)
        if result:
            app_logger.info(f"Module {module} powered off successfully")
            return {
                "success": True,
                "message": f"Module {module} powered off successfully",
                "data": {"module": module, "status": "off"}
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to power off module {module}")
            
    except Exception as e:
        app_logger.error(f"Power off module {module} failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/power/status/{module}")
async def get_power_status(module: str) -> Dict[str, Any]:
    """获取指定模块电源状态"""
    try:
        status = power_manager.check_power_status(module)
        app_logger.info(f"Power status for {module}: {status}")
        return {
            "success": True,
            "message": f"Power status for {module}",
            "data": {"module": module, "status": "on" if status else "off"}
        }
        
    except Exception as e:
        app_logger.error(f"Get power status for {module} failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/power/on-all")
async def power_on_all_modules() -> Dict[str, Any]:
    """给所有模块上电"""
    try:
        power_manager.power_on_all()
        app_logger.info("All modules powered on successfully")
        return {
            "success": True,
            "message": "All modules powered on successfully",
            "data": {"action": "power_on_all", "status": "completed"}
        }
        
    except Exception as e:
        app_logger.error(f"Power on all modules failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/power/off-all")
async def power_off_all_modules() -> Dict[str, Any]:
    """给所有模块断电"""
    try:
        power_manager.power_off_all()
        app_logger.info("All modules powered off successfully")
        return {
            "success": True,
            "message": "All modules powered off successfully",
            "data": {"action": "power_off_all", "status": "completed"}
        }
        
    except Exception as e:
        app_logger.error(f"Power off all modules failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 转台电机API ====================
@router.post("/motor/find-zero")
async def motor_find_zero(timeout: int = Body(60, embed=True)) -> Dict[str, Any]:
    """转台找零位"""
    try:
        motor = Motor()
        result = motor.cmd_find_zero(timeout)
        app_logger.info(f"Motor find zero result: {result}")
        return {
            "success": True,
            "message": "Motor find zero completed",
            "data": {"result": result, "timeout": timeout}
        }
        
    except Exception as e:
        app_logger.error(f"Motor find zero failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/motor/set-position")
async def motor_set_position(position: float = Body(...), timeout: int = Body(60, embed=True)) -> Dict[str, Any]:
    """设置转台位置"""
    try:
        motor = Motor()
        result = motor.cmd_set_position(position, timeout)
        app_logger.info(f"Motor set position {position}° result: {result}")
        return {
            "success": True,
            "message": f"Motor set position {position}° completed",
            "data": {"position": position, "result": result, "timeout": timeout}
        }
        
    except Exception as e:
        app_logger.error(f"Motor set position failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/motor/set-speed")
async def motor_set_speed(speed: float = Body(..., embed=True)) -> Dict[str, Any]:
    """设置转台速度"""
    try:
        motor = Motor()
        motor.cmd_set_speed(speed)
        app_logger.info(f"Motor set speed {speed}°/s")
        return {
            "success": True,
            "message": f"Motor set speed {speed}°/s completed",
            "data": {"speed": speed}
        }
        
    except Exception as e:
        app_logger.error(f"Motor set speed failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/motor/configure")
async def motor_configure_settings() -> Dict[str, Any]:
    """配置转台参数"""
    try:
        motor_setting()
        app_logger.info("Motor configuration completed")
        return {
            "success": True,
            "message": "Motor configuration completed",
            "data": {"action": "configure_motor"}
        }
        
    except Exception as e:
        app_logger.error(f"Motor configuration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/motor/get-angle")
async def motor_get_angle(timeout: int = Body(60, embed=True)) -> Dict[str, Any]:
    """获取转台当前角度（先找零位）"""
    try:
        motor = Motor()
        angle = motor.cmd_get_angle(timeout)
        if angle >= 0:
            app_logger.info(f"Motor get angle: {angle}°")
            return {
                "success": True,
                "message": "Motor angle retrieved successfully",
                "data": {"angle": angle, "timeout": timeout}
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to get motor angle (find zero failed)")
            
    except Exception as e:
        app_logger.error(f"Motor get angle failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 小电机API ====================
@router.post("/min-motor/set-angle")
async def min_motor_set_angle(angle: float = Body(...), timeout: int = Body(60, embed=True)) -> Dict[str, Any]:
    """设置小电机角度"""
    try:
        result = motor_manager.cmd_set_pos(angle, timeout)
        if result:
            app_logger.info(f"Min motor set angle {angle}° successfully")
            return {
                "success": True,
                "message": f"Min motor set angle {angle}° completed",
                "data": {"angle": angle, "result": result, "timeout": timeout}
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to set min motor angle {angle}°")
            
    except Exception as e:
        app_logger.error(f"Min motor set angle failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/min-motor/relative-move")
async def min_motor_relative_move(angle: float = Body(...), timeout: int = Body(60, embed=True)) -> Dict[str, Any]:
    """小电机相对移动"""
    try:
        result = motor_manager.cmd_set_pos_ab(angle, 10, timeout)
        app_logger.info(f"Min motor relative move {angle}° result: {result}")
        return {
            "success": True,
            "message": f"Min motor relative move {angle}° completed",
            "data": {"angle": angle, "result": result, "timeout": timeout}
        }
        
    except Exception as e:
        app_logger.error(f"Min motor relative move failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/min-motor/read-angle")
async def min_motor_read_angle() -> Dict[str, Any]:
    """读取小电机当前角度"""
    try:
        angle = motor_manager.cmd_read_angle()
        app_logger.info(f"Min motor current angle: {angle}°")
        return {
            "success": True,
            "message": "Min motor angle read successfully",
            "data": {"angle": angle}
        }
        
    except Exception as e:
        app_logger.error(f"Min motor read angle failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/min-motor/detect-limits")
async def min_motor_detect_limits(max_rotation: int = Body(300), timeout: int = Body(60, embed=True)) -> Dict[str, Any]:
    """检测小电机限位开关"""
    try:
        result = motor_manager.detect_limit_switches(max_rotation, timeout)
        app_logger.info("Min motor limit detection completed")
        return {
            "success": True,
            "message": "Min motor limit detection completed",
            "data": result
        }
        
    except Exception as e:
        app_logger.error(f"Min motor limit detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/min-motor/configure")
async def min_motor_configure_settings() -> Dict[str, Any]:
    """配置小电机参数"""
    try:
        min_motor_setting()
        app_logger.info("Min motor configuration completed")
        return {
            "success": True,
            "message": "Min motor configuration completed",
            "data": {"action": "configure_min_motor"}
        }
        
    except Exception as e:
        app_logger.error(f"Min motor configuration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 雷达API ====================
@router.post("/lidar/setup")
async def lidar_setup() -> Dict[str, Any]:
    """雷达初始化设置"""
    try:
        result = lidar_setting()
        if result is False:
            raise HTTPException(status_code=400, detail="Lidar setup failed")
        app_logger.info("Lidar setup completed")
        return {
            "success": True,
            "message": "Lidar setup completed",
            "data": {"action": "lidar_setup"}
        }
        
    except Exception as e:
        app_logger.error(f"Lidar setup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lidar/sn")
async def get_lidar_sn() -> Dict[str, Any]:
    """获取雷达序列号"""
    try:
        sn = get_sn()
        app_logger.info(f"Lidar SN: {sn}")
        return {
            "success": True,
            "message": "Lidar SN retrieved",
            "data": {"sn": sn}
        }
        
    except Exception as e:
        app_logger.error(f"Get lidar SN failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lidar/calibration")
async def get_lidar_calibration() -> Dict[str, Any]:
    """获取雷达校准数据"""
    try:
        calibration = get_calib()
        app_logger.info("Lidar calibration data retrieved")
        return {
            "success": True,
            "message": "Lidar calibration data retrieved",
            "data": {"calibration": calibration}
        }
        
    except Exception as e:
        app_logger.error(f"Get lidar calibration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 倾角仪API ====================
@router.get("/inclinometer/read")
async def read_inclinometer() -> Dict[str, Any]:
    """读取倾角仪数据"""
    try:
        inclinometer = Inclinometer()
        success = inclinometer._get_inc()
        if success:
            data = {
                "x_angle": inclinometer.current_inc_x,
                "y_angle": inclinometer.current_inc_y
            }
            app_logger.info(f"Inclinometer data: X={data['x_angle']}, Y={data['y_angle']}")
            return {
                "success": True,
                "message": "Inclinometer data read successfully",
                "data": data
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to read inclinometer data")
            
    except Exception as e:
        app_logger.error(f"Read inclinometer failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/inclinometer/save")
async def save_inclinometer_data(filepath: str = Body(..., embed=True)) -> Dict[str, Any]:
    """保存倾角仪数据到文件"""
    try:
        inclinometer = Inclinometer()
        success = inclinometer.save_inc(filepath)
        if success:
            app_logger.info(f"Inclinometer data saved to {filepath}")
            return {
                "success": True,
                "message": f"Inclinometer data saved to {filepath}",
                "data": {"filepath": filepath}
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to save inclinometer data")
            
    except Exception as e:
        app_logger.error(f"Save inclinometer data failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 系统配置API ====================
@router.post("/config/wifi-setup")
async def setup_wifi_ssid() -> Dict[str, Any]:
    """配置WiFi SSID"""
    try:
        success, message = configure_wifi_ssid()
        if success:
            app_logger.info(f"WiFi setup completed: {message}")
            return {
                "success": True,
                "message": message,
                "data": {"action": "wifi_setup"}
            }
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except Exception as e:
        app_logger.error(f"WiFi setup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/time-sync")
async def sync_system_time(target_time: str = Body(..., embed=True)) -> Dict[str, Any]:
    """同步系统时间"""
    try:
        success, message = update_system_time(target_time)
        if success:
            app_logger.info(f"Time sync completed: {message}")
            return {
                "success": True,
                "message": message,
                "data": {"target_time": target_time}
            }
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except Exception as e:
        app_logger.error(f"Time sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 设备批量操作API ====================
@router.post("/setup/all-devices")
async def setup_all_devices() -> Dict[str, Any]:
    """一键配置所有设备"""
    try:
        results = {
            "lidar": False,
            "motor": False,
            "min_motor": False
        }
        
        # 配置雷达
        try:
            lidar_result = lidar_setting()
            results["lidar"] = lidar_result is not False
        except Exception as e:
            app_logger.error(f"Lidar setup error: {str(e)}")
        
        # 配置转台
        try:
            motor_setting()
            results["motor"] = True
        except Exception as e:
            app_logger.error(f"Motor setup error: {str(e)}")
        
        # 配置小电机
        try:
            min_motor_setting()
            results["min_motor"] = True
        except Exception as e:
            app_logger.error(f"Min motor setup error: {str(e)}")
        
        app_logger.info(f"All devices setup completed: {results}")
        return {
            "success": True,
            "message": "All devices setup completed",
            "data": {"results": results}
        }
        
    except Exception as e:
        app_logger.error(f"All devices setup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 相机API ====================
@router.get("/camera/resolutions")
async def get_camera_resolutions() -> Dict[str, Any]:
    """获取预设分辨率列表"""
    try:
        app_logger.info("Camera resolutions retrieved")
        return {
            "success": True,
            "message": "Camera resolutions retrieved",
            "data": {
                "resolutions": RESOLUTIONS,
                "supported_modes": list(RESOLUTIONS.keys())
            }
        }
    except Exception as e:
        app_logger.error(f"Get camera resolutions failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/camera/set-resolution")
async def set_camera_resolution(
    device: str = Body(..., embed=True),
    mode: str = Body(..., embed=True)
) -> Dict[str, Any]:
    """设置指定相机的分辨率"""
    try:
        # 验证分辨率模式
        if mode not in RESOLUTIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported resolution mode: {mode}. Supported modes: {list(RESOLUTIONS.keys())}"
            )
        
        width, height = RESOLUTIONS[mode]
        
        # 设置分辨率
        set_resolution(device, width, height)
        
        app_logger.info(f"Camera {device} resolution set to {mode} ({width}x{height})")
        return {
            "success": True,
            "message": f"Camera {device} resolution set to {mode}",
            "data": {
                "device": device,
                "mode": mode,
                "resolution": f"{width}x{height}"
            }
        }
        
    except ValueError as e:
        app_logger.error(f"Set camera resolution failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        app_logger.error(f"Set camera resolution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/camera/capture")
async def capture_camera_image(
    device: str = Body(..., embed=True),
    filename: str = Body(..., embed=True)
) -> Dict[str, Any]:
    """指定相机拍照并保存为指定文件名"""
    try:
        # 拍照
        capture_image(device, filename)
        
        # 验证图片格式
        if not is_image_valid(filename):
            # 如果图片无效，删除文件并返回错误
            try:
                Path(filename).unlink()
            except:
                pass
            raise HTTPException(
                status_code=400, 
                detail="Captured image format is invalid"
            )
        
        app_logger.info(f"Image captured successfully: {filename} from device {device}")
        return {
            "success": True,
            "message": "Image captured successfully",
            "data": {
                "device": device,
                "filename": filename,
                "status": "valid"
            }
        }
        
    except ValueError as e:
        app_logger.error(f"Capture image failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Capture image failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== LED控制API ====================
@router.post("/led/set-custom-color")
async def set_led_custom_color(
    red: int = Body(..., ge=0, le=255, embed=True),
    green: int = Body(..., ge=0, le=255, embed=True),
    blue: int = Body(..., ge=0, le=255, embed=True)
) -> Dict[str, Any]:
    """设置LED自定义颜色(RGB值)"""
    try:
        success = led_controller.set_custom_color(red, green, blue)
        if success:
            app_logger.info(f"LED custom color set: R={red}, G={green}, B={blue}")
            return {
                "success": True,
                "message": "LED custom color set successfully",
                "data": {
                    "red": red,
                    "green": green,
                    "blue": blue,
                    "rgb": f"({red}, {green}, {blue})"
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to set LED custom color")
            
    except Exception as e:
        app_logger.error(f"Set LED custom color failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 屏幕测试 API ====================
@router.post("/screen-test/run")
async def run_screen_test() -> Dict[str, Any]:
    """
    运行屏幕测试
    
    通过命令行调用 C++测试程序，根据输出判断测试结果。
    输出包含"true"则判定为通过，否则为失败。
    超时时间由配置文件 SCREEN_TEST_TIMEOUT 指定。
    
    Returns:
        Dict[str, Any]: 测试结果
    """
    try:
        # 创建屏幕测试器实例
        screen_tester = ScreenTester()
        
        # 检查程序是否存在
        if not screen_tester.test_program_exists():
            raise HTTPException(
                status_code=400,
                detail=f"屏幕测试程序不存在或不可执行"
            )
        
        app_logger.info("开始执行屏幕测试...")
        
        # 运行测试
        result = screen_tester.run_test()
        
        if result.get("success", False):
            app_logger.info("屏幕测试完成：通过")
        else:
            app_logger.warning(f"屏幕测试完成：失败 - {result.get('message', '未知错误')}")
        
        return {
            "success": True,
            "message": "屏幕测试执行完成",
            "data": result
        }
        
    except HTTPException:
        # 重新抛出 HTTPException，保持原有的状态码
        raise
    except Exception as e:
        app_logger.error(f"运行屏幕测试失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

