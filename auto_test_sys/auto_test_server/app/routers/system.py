from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
import psutil
import platform
import time
import subprocess
import re
import os
from datetime import datetime
from app.utils.logger import app_logger

router = APIRouter()


@router.get("/info")
async def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    try:
        system_info = {
            "system": {
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation()
            },
            "server": {
                "startup_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "current_time": datetime.now().isoformat()
            }
        }
        return {
            "success": True,
            "message": "System information retrieved successfully",
            "data": system_info
        }
    except Exception as e:
        app_logger.error(f"Get system info failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_system_metrics() -> Dict[str, Any]:
    """获取系统指标"""
    try:
        # CPU信息
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        # 内存信息
        memory = psutil.virtual_memory()

        # 磁盘信息
        disk = psutil.disk_usage('/')

        metrics_data = {
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "frequency": cpu_freq.current if cpu_freq else None
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "timestamp": time.time()
        }

        return {
            "success": True,
            "message": "System metrics retrieved successfully",
            "data": metrics_data
        }
    except Exception as e:
        app_logger.error(f"Get system metrics failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes")
async def get_processes(limit: int = 10) -> Dict[str, Any]:
    """获取进程信息"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            if len(processes) >= limit:
                break

        processes_data = {
            "processes": processes,
            "count": len(processes),
            "timestamp": time.time()
        }

        return {
            "success": True,
            "message": f"Process list (limited to {limit}) retrieved successfully",
            "data": processes_data
        }
    except Exception as e:
        app_logger.error(f"Get processes failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 电池状态API ====================
@router.get("/battery")
async def get_battery_status() -> Dict[str, Any]:
    """获取电池电量和开关机按键状态"""
    try:
        battery_data = {
            "battery_level": 0,
            "power_button_state": 0,
            "status": "unknown"
        }

        # 尝试从 /dev/ttyS3 文件读取电池数据
        try:
            # 使用命令行cat命令读取文件内容
            result = subprocess.run(
                ['timeout', '5', 'head', '-1', '/dev/ttyS3'],
                capture_output=True,
                text=True
            )
            print(f"读取文件内容: {result.stdout}")
            if result.returncode == 0 and result.stdout:
                # 读取到数据，解析格式
                lines = result.stdout.strip().split('\n')

                # 查找包含有效数据的行
                for line in lines:
                    line = line.strip()
                    if line and ';' in line:
                        app_logger.debug(f"解析电池数据行: {line}")

                        parts = line.split(';')
                        if len(parts) >= 3:
                            # 解析电量值（第一部分）
                            try:
                                battery_level = int(parts[0])
                                battery_data["battery_level"] = battery_level
                            except ValueError:
                                app_logger.warning(f"无法解析电池电量: {parts[0]}")

                            # 解析开关机按键状态（最后一部分）
                            try:
                                # 注意：parts[-1] 可能是空字符串，需要处理
                                if parts[-1] != "":
                                    power_button_state = int(parts[-1])
                                elif len(parts) >= 4 and parts[-2] != "":
                                    # 如果最后一部分是空的，尝试前一部分
                                    power_button_state = int(parts[-2])
                                else:
                                    power_button_state = 0

                                battery_data["power_button_state"] = power_button_state
                            except (ValueError, IndexError) as e:
                                app_logger.warning(f"无法解析按键状态: {parts[-1] if len(parts[-1]) > 0 else '空值'}")
                                battery_data["power_button_state"] = 0

                            # 设置状态描述
                            if 2 <= battery_data["battery_level"] <= 100:
                                battery_data["status"] = "normal"
                            elif battery_data["battery_level"] == 1:
                                battery_data["status"] = "low"
                            else:
                                battery_data["status"] = "abnormal"

                            app_logger.info(
                                f"成功解析电池数据: 电量={battery_data['battery_level']}, 按键状态={battery_data['power_button_state']}, 状态={battery_data['status']}")
                            break
                else:
                    app_logger.warning("未找到有效的电池数据行")
            else:
                app_logger.warning(f"cat命令执行失败或无输出: 返回码={result.returncode}")

        except subprocess.TimeoutExpired:
            app_logger.error("读取电池数据超时")
        except FileNotFoundError:
            app_logger.error("电池数据文件 /dev/ttyS3 不存在")
        except PermissionError:
            app_logger.error("权限不足，无法读取 /dev/ttyS3")
        except Exception as e:
            app_logger.warning(f"读取电池数据失败: {str(e)}")



        app_logger.info(f"Battery status retrieved: level={battery_data['battery_level']}, button={battery_data['power_button_state']}, status={battery_data['status']}")
        return {
            "success": True,
            "message": "Battery status retrieved",
            "data": battery_data
        }
        
    except Exception as e:
        app_logger.error(f"Get battery status failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== TF卡挂载状态API ====================
@router.get("/tf-card-status")
async def get_tf_card_status() -> Dict[str, Any]:
    """获取TF卡挂载状态"""
    try:
        tf_card_data = {
            "exists": False,
            "device": "",
            "size": "",
            "type": "",
            "mountpoint": "",
            "status": "not_found"
        }
        
        try:
            # 执行 lsblk 命令获取磁盘信息
            result = subprocess.run(['lsblk', '-o', 'NAME,MAJ:MIN,RM,SIZE,RO,TYPE,MOUNTPOINT'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                raise Exception(f"lsblk command failed: {result.stderr}")
            
            output = result.stdout
            lines = output.strip().split('\n')
            
            # 查找 mmcblk1 相关的信息
            for line in lines[1:]:  # 跳过表头
                if 'mmcblk1' in line:
                    # 解析 mmcblk1 的信息
                    parts = line.strip().split()
                    if len(parts) >= 7:
                        tf_card_data["exists"] = True
                        tf_card_data["device"] = parts[0]  # NAME
                        tf_card_data["size"] = parts[3]   # SIZE
                        tf_card_data["type"] = parts[5]   # TYPE
                        tf_card_data["mountpoint"] = parts[6] if len(parts) > 6 else ""  # MOUNTPOINT
                        
                        # 设置状态
                        if tf_card_data["mountpoint"] and tf_card_data["mountpoint"] != "":
                            tf_card_data["status"] = "mounted"
                        else:
                            tf_card_data["status"] = "detected"
                        
                        break
            
            app_logger.info(f"TF card status retrieved: exists={tf_card_data['exists']}, device={tf_card_data['device']}, mountpoint={tf_card_data['mountpoint']}, status={tf_card_data['status']}")
            return {
                "success": True,
                "message": "TF card status retrieved",
                "data": tf_card_data
            }
            
        except Exception as e:
            app_logger.error(f"Get TF card status failed: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get TF card status: {str(e)}",
                "data": tf_card_data
            }
        
    except Exception as e:
        app_logger.error(f"Get TF card status failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== TF卡读写速度测试API ====================
@router.get("/tf-write-speed")
async def test_tf_write_speed(
        size_mb: int = 100
) -> Dict[str, Any]:
    """测试TF卡写入速度"""
    try:
        file_path="/media/mmcblk1p1/write_speed_test.bin"
        # 清除缓存
        subprocess.run(['sync'], check=False)
        with open('/proc/sys/vm/drop_caches', 'w') as f:
            f.write('3')

        # 执行dd命令测试写入速度
        start_time = time.time()
        dd_cmd = f"dd if=/dev/zero of={file_path} bs=1M count={size_mb} 2>&1"
        result = subprocess.run(
            dd_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        end_time = time.time()

        if result.returncode != 0:
            # 清理可能创建的文件
            if os.path.exists(file_path):
                os.remove(file_path)
            raise Exception(f"dd命令执行失败: {result.stderr}")

        # 解析dd输出获取速度
        dd_output = result.stdout
        speed_match = re.search(r'(\d+\.?\d*)\s*MB/s', dd_output)
        speed = float(speed_match.group(1)) if speed_match else 0

        # 删除测试文件
        if os.path.exists(file_path):
            os.remove(file_path)

        # 计算总时间和平均速度
        total_time = end_time - start_time
        total_bytes = size_mb * 1024 * 1024
        calculated_speed = (total_bytes / total_time) / (1024 * 1024)  # MB/s

        app_logger.info(f"TF卡写入速度测试完成: 速度={speed}MB/s, 时间={total_time:.2f}s")

        return {
            "success": True,
            "message": "写入速度测试完成",
            "data": {
                "test_type": "write",
                "file_size_mb": size_mb,
                "file_size_bytes": total_bytes,
                "total_time_seconds": round(total_time, 4),
                "dd_reported_speed_mb_per_s": speed,
                "calculated_speed_mb_per_s": round(calculated_speed, 2),
                "test_file": file_path,
                "raw_output": dd_output.strip()
            }
        }

    except subprocess.TimeoutExpired:
        app_logger.error("写入速度测试超时")
        # 清理可能创建的文件
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=408, detail="测试超时")
    except Exception as e:
        app_logger.error(f"测试TF卡写入速度失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tf-read-speed")
async def test_tf_read_speed(
        size_mb: int = 100
) -> Dict[str, Any]:
    """测试TF卡读取速度"""
    try:
        # 首先创建一个测试文件用于读取
        test_file = f"/media/mmcblk1p1/read_speed_test.bin"

        # 检查是否已经有测试文件，没有则创建
        if not os.path.exists(test_file) or os.path.getsize(test_file) < size_mb * 1024 * 1024:
            app_logger.info("创建读取测试文件...")
            create_cmd = f"dd if=/dev/zero of={test_file} bs=1M count={size_mb} 2>&1"
            create_result = subprocess.run(
                create_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            if create_result.returncode != 0:
                raise Exception(f"创建测试文件失败: {create_result.stderr}")

        # 清除缓存
        subprocess.run(['sync'], check=False)
        with open('/proc/sys/vm/drop_caches', 'w') as f:
            f.write('3')

        # 执行dd命令测试读取速度
        start_time = time.time()
        dd_cmd = f"dd if={test_file} of=/dev/null bs=1M 2>&1"
        result = subprocess.run(
            dd_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        end_time = time.time()

        if result.returncode != 0:
            raise Exception(f"dd命令执行失败: {result.stderr}")

        # 解析dd输出获取速度
        dd_output = result.stdout
        speed_match = re.search(r'(\d+\.?\d*)\s*MB/s', dd_output)
        speed = float(speed_match.group(1)) if speed_match else 0

        # 计算总时间和平均速度
        total_time = end_time - start_time
        total_bytes = size_mb * 1024 * 1024
        calculated_speed = (total_bytes / total_time) / (1024 * 1024)  # MB/s

        app_logger.info(f"TF卡读取速度测试完成: 速度={speed}MB/s, 时间={total_time:.2f}s")

        return {
            "success": True,
            "message": "读取速度测试完成",
            "data": {
                "test_type": "read",
                "data_size_mb": size_mb,
                "data_size_bytes": total_bytes,
                "total_time_seconds": round(total_time, 4),
                "dd_reported_speed_mb_per_s": speed,
                "calculated_speed_mb_per_s": round(calculated_speed, 2),
                "test_file": test_file,
                "raw_output": dd_output.strip()
            }
        }

    except subprocess.TimeoutExpired:
        app_logger.error("读取速度测试超时")
        raise HTTPException(status_code=408, detail="测试超时")
    except Exception as e:
        app_logger.error(f"测试TF卡读取速度失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


