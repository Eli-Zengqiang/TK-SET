import time
import cv2
import numpy as np
import os
from typing import Dict, Any, List

from ..base import BaseTestCase, TestCaseConfig, TestResult, TestStatus, TestType


class CameraComprehensiveTest(BaseTestCase):
    """相机综合测试 - 支持双相机、16M分辨率、图像质量分析"""

    def setup(self) -> bool:
        """测试前置准备"""
        try:
            self.log_step("开始相机综合测试前置准备...")
            
            if not self.api_client:
                self.log_step("API客户端未初始化，无法进行相机测试", 'ERROR')
                return False
                
            # 检查下载目录
            self.download_dir = self.config.parameters.get('download_dir', './downloads')
            if not os.path.exists(self.download_dir):
                os.makedirs(self.download_dir)
                self.log_step(f"创建下载目录: {self.download_dir}")
            
            self.log_step("相机测试准备就绪")
            return True
            
        except Exception as e:
            self.log_step(f"相机测试前置准备异常: {str(e)}", 'ERROR')
            return False

    def execute(self) -> TestResult:
        """执行相机综合测试"""
        start_time = time.time()
        test_data: Dict[str, Any] = {}
        
        try:
            if not self.api_client:
                error_msg = "API客户端未初始化"
                self.log_step(error_msg, 'ERROR')
                return TestResult(
                    test_name=self.config.name,
                    status=TestStatus.ERROR,
                    message=error_msg,
                    error_info=error_msg
                )
            
            # 获取测试配置
            cameras = self.config.parameters.get('cameras', ['/dev/video0', '/dev/video2'])
            resolution = self.config.parameters.get('resolution', '16M')
            test_sequence = self.config.parameters.get('test_sequence', [
                'resolution_test',
                'capture_test',
                'download_test',
                'quality_analysis'
            ])
            
            self.log_step(f"开始相机综合测试")
            self.log_step(f"测试相机: {cameras}")
            self.log_step(f"目标分辨率: {resolution}")
            self.log_step(f"测试序列: {test_sequence}")
            
            results: List[str] = []
            all_passed = True
            success_count = 0
            fail_count = 0
            camera_results = {}
            
            # 为每个相机执行测试序列
            for camera in cameras:
                self.log_step(f"开始测试相机: {camera}")
                camera_result = self._test_single_camera(camera, resolution, test_sequence)
                camera_results[camera] = camera_result
                
                if camera_result.get("success", False):
                    results.append(f"相机 {camera} 测试通过")
                    success_count += 1
                else:
                    results.append(f"相机 {camera} 测试失败: {camera_result.get('message', 'Unknown')}")
                    all_passed = False
                    fail_count += 1
                
                # 相机间间隔
                if len(cameras) > 1 and camera != cameras[-1]:
                    wait_time = self.config.parameters.get('inter_camera_delay', 2)
                    if wait_time > 0:
                        self.log_step(f"等待 {wait_time} 秒后测试下一个相机")
                        time.sleep(wait_time)
            
            # 汇总测试数据
            end_time = time.time()
            duration = end_time - start_time
            test_data.update({
                "results": results,
                "camera_results": camera_results,
                "cameras_tested": len(cameras),
                "success_count": success_count,
                "fail_count": fail_count,
                "duration_seconds": round(duration, 2),
                "resolution": resolution,
                "test_sequence": test_sequence
            })
            
            self.log_step(f"相机综合测试完成，总计测试相机: {len(cameras)}个")
            self.log_step(f"成功: {success_count}个，失败: {fail_count}个")
            
            if all_passed:
                self.log_step("所有相机测试通过")
                return TestResult(
                    test_name=self.config.name,
                    status=TestStatus.PASSED,
                    message=f"所有相机测试通过 ({success_count}/{len(cameras)})",
                    data=test_data
                )
            else:
                self.log_step(f"相机测试部分失败，成功{success_count}个，失败{fail_count}个", 'WARNING')
                return TestResult(
                    test_name=self.config.name,
                    status=TestStatus.FAILED,
                    message=f"相机测试部分失败 ({success_count}/{len(cameras)})",
                    data=test_data
                )
                
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            error_msg = f"相机综合测试执行异常: {str(e)}"
            self.log_step(error_msg, 'ERROR')
            
            test_data.update({
                "duration_seconds": round(duration, 2),
                "error_time": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            return TestResult(
                test_name=self.config.name,
                status=TestStatus.ERROR,
                message=error_msg,
                error_info=str(e),
                data=test_data
            )

    def teardown(self) -> bool:
        """测试后置清理"""
        try:
            self.log_step("开始相机测试后置清理...")
            self.log_step("相机测试后置清理完成")
            return True
        except Exception as e:
            self.log_step(f"相机测试后置清理异常: {str(e)}", 'ERROR')
            return False
    
    def _test_single_camera(self, camera: str, resolution: str, test_sequence: List[str]) -> Dict[str, Any]:
        """测试单个相机的所有项目"""
        try:
            self.log_step(f"开始测试相机 {camera} 的完整测试序列")
            
            camera_data = {
                "camera": camera,
                "resolution": resolution,
                "test_results": {},
                "local_image_path": None,
                "quality_metrics": {}
            }
            
            all_tests_passed = True
            
            # 按顺序执行测试项目
            for test_item in test_sequence:
                try:
                    self.log_step(f"执行测试项目: {test_item}")
                    
                    if test_item == 'resolution_test':
                        result = self._test_resolution_setting(camera, resolution)
                    elif test_item == 'capture_test':
                        result = self._test_image_capture(camera, resolution)
                    elif test_item == 'download_test':
                        filename = f"test_{camera.replace('/', '_')}_{resolution}.jpg"
                        result = self._test_image_download(camera, filename)
                        if result.get('success') and 'local_path' in result:
                            camera_data['local_image_path'] = result['local_path']
                    elif test_item == 'quality_analysis':
                        local_path = camera_data.get('local_image_path')
                        if local_path and os.path.exists(local_path):
                            result = self._analyze_image_quality(local_path)
                            camera_data['quality_metrics'] = result.get('metrics', {})
                        else:
                            result = {"success": False, "message": "本地图片不存在，无法进行质量分析"}
                    else:
                        result = {"success": False, "message": f"未知测试项目: {test_item}"}
                        all_tests_passed = False
                    
                    camera_data['test_results'][test_item] = result
                    
                    if not result.get('success', False):
                        all_tests_passed = False
                        self.log_step(f"测试项目 {test_item} 失败: {result.get('message', 'Unknown')}", 'ERROR')
                    else:
                        self.log_step(f"测试项目 {test_item} 通过")
                        
                except Exception as e:
                    error_msg = f"执行测试项目 {test_item} 时发生异常: {str(e)}"
                    self.log_step(error_msg, 'ERROR')
                    camera_data['test_results'][test_item] = {"success": False, "message": error_msg}
                    all_tests_passed = False
                    continue
                
                # 测试项目间间隔
                wait_time = self.config.parameters.get('inter_test_delay', 1)
                if wait_time > 0:
                    time.sleep(wait_time)
            
            camera_data['overall_success'] = all_tests_passed
            
            if all_tests_passed:
                return {
                    "success": True,
                    "message": f"相机 {camera} 所有测试项目通过",
                    "data": camera_data
                }
            else:
                return {
                    "success": False,
                    "message": f"相机 {camera} 部分测试项目失败",
                    "data": camera_data
                }
                
        except Exception as e:
            self.log_step(f"测试单个相机 {camera} 时发生异常: {str(e)}", 'ERROR')
            return {
                "success": False,
                "message": f"测试相机 {camera} 异常: {str(e)}"
            }
    
    def _test_resolution_setting(self, camera: str, resolution: str) -> Dict[str, Any]:
        """测试分辨率设置"""
        try:
            self.log_step(f"设置相机 {camera} 分辨率为 {resolution}")
            
            result = self.api_client.camera_set_resolution(camera, resolution)
            if not result or not result.get("success", False):
                return {
                    "success": False,
                    "message": f"设置分辨率失败: {result.get('message', 'Unknown') if result else 'No response'}"
                }
            
            self.log_step(f"相机 {camera} 分辨率设置成功")
            return {
                "success": True,
                "message": f"分辨率 {resolution} 设置成功"
            }
            
        except Exception as e:
            self.log_step(f"分辨率设置测试异常: {str(e)}", 'ERROR')
            return {
                "success": False,
                "message": f"分辨率设置异常: {str(e)}"
            }
    
    def _test_image_capture(self, camera: str, resolution: str) -> Dict[str, Any]:
        """测试图像拍摄"""
        try:
            filename = f"test_{camera.replace('/', '_')}_{resolution}.jpg"
            
            self.log_step(f"相机 {camera} 开始拍摄: {filename}")
            
            result = self.api_client.camera_capture(camera, filename)
            if not result or not result.get("success", False):
                return {
                    "success": False,
                    "message": f"拍摄失败: {result.get('message', 'Unknown') if result else 'No response'}"
                }
            
            self.log_step(f"相机 {camera} 拍摄成功: {filename}")
            return {
                "success": True,
                "message": f"拍摄成功: {filename}",
                "remote_filename": filename
            }
            
        except Exception as e:
            self.log_step(f"图像拍摄测试异常: {str(e)}", 'ERROR')
            return {
                "success": False,
                "message": f"图像拍摄异常: {str(e)}"
            }
    
    def _test_image_download(self, camera: str, remote_filename: str) -> Dict[str, Any]:
        """测试图像下载"""
        try:
            if not remote_filename:
                return {
                    "success": False,
                    "message": "远程文件名为空"
                }

            local_path = os.path.join(self.download_dir, remote_filename)
            
            self.log_step(f"下载图像文件: {remote_filename} -> {local_path}")
            
            result = self.api_client.download_file(remote_filename, local_path)
            if not result or not result.get("success", False):
                return {
                    "success": False,
                    "message": f"下载失败: {result.get('message', 'Unknown') if result else 'No response'}"
                }
            
            if os.path.exists(local_path):
                file_size = os.path.getsize(local_path)
                self.log_step(f"图像下载成功: {local_path} ({file_size} bytes)")
                return {
                    "success": True,
                    "message": f"下载成功: {remote_filename} ({file_size} bytes)",
                    "local_path": local_path,
                    "file_size": file_size
                }
            else:
                return {
                    "success": False,
                    "message": "下载完成但本地文件不存在"
                }
                
        except Exception as e:
            self.log_step(f"图像下载测试异常: {str(e)}", 'ERROR')
            return {
                "success": False,
                "message": f"图像下载异常: {str(e)}"
            }
    
    def _analyze_image_quality(self, image_path: str) -> Dict[str, Any]:
        """分析图像质量 - 清晰度评估"""
        try:
            self.log_step(f"开始分析图像质量: {image_path}")
            
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "message": "图像文件不存在"
                }
            
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                return {
                    "success": False,
                    "message": "无法读取图像文件"
                }
            
            height, width = image.shape[:2]
            self.log_step(f"图像尺寸: {width}x{height}")
            
            # 质量分析指标
            metrics = {}
            
            # 1. 拉普拉斯方差（边缘清晰度）
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            metrics['laplacian_variance'] = round(laplacian_var, 2)
            
            # 2. 梯度幅值（整体锐度）
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
            avg_gradient = np.mean(gradient_magnitude)
            metrics['average_gradient'] = round(avg_gradient, 2)
            
            # 3. 对比度
            contrast = np.std(gray)
            metrics['contrast'] = round(contrast, 2)
            
            # 4. 亮度
            brightness = np.mean(gray)
            metrics['brightness'] = round(brightness, 2)
            
            # 5. 信噪比估算
            noise_estimate = np.std(gray[::10, ::10])  # 采样降低计算量
            snr = brightness / (noise_estimate + 1e-8)  # 避免除零
            metrics['snr'] = round(snr, 2)
            
            # 质量评估
            quality_score = 0
            quality_details = []
            
            # 拉普拉斯方差评估（>100通常表示清晰）
            if laplacian_var > 100:
                quality_score += 25
                quality_details.append("清晰度良好")
            elif laplacian_var > 50:
                quality_score += 15
                quality_details.append("清晰度一般")
            else:
                quality_details.append("清晰度较差")
            
            # 梯度评估
            if avg_gradient > 20:
                quality_score += 25
                quality_details.append("锐度良好")
            elif avg_gradient > 10:
                quality_score += 15
                quality_details.append("锐度一般")
            else:
                quality_details.append("锐度不足")
            
            # 对比度评估
            if 30 <= contrast <= 100:
                quality_score += 25
                quality_details.append("对比度适中")
            elif contrast > 100:
                quality_score += 20
                quality_details.append("对比度过高")
            else:
                quality_details.append("对比度偏低")
            
            # 亮度评估
            if 80 <= brightness <= 180:
                quality_score += 25
                quality_details.append("曝光良好")
            elif brightness > 180:
                quality_details.append("曝光过度")
            else:
                quality_details.append("曝光不足")
            
            # 整体评级
            if quality_score >= 80:
                quality_rating = "优秀"
            elif quality_score >= 60:
                quality_rating = "良好"
            elif quality_score >= 40:
                quality_rating = "一般"
            else:
                quality_rating = "较差"
            
            metrics.update({
                'quality_score': quality_score,
                'quality_rating': quality_rating,
                'quality_details': quality_details
            })
            
            self.log_step(f"图像质量分析完成 - 评分: {quality_score}/100 ({quality_rating})")
            self.log_step(f"  清晰度(Laplacian): {laplacian_var:.2f}")
            self.log_step(f"  锐度(Gradient): {avg_gradient:.2f}")
            self.log_step(f"  对比度: {contrast:.2f}")
            self.log_step(f"  亮度: {brightness:.2f}")
            self.log_step(f"  信噪比: {snr:.2f}")
            
            return {
                "success": True,
                "message": f"图像质量分析完成，评分: {quality_score}/100 ({quality_rating})",
                "metrics": metrics
            }
            
        except Exception as e:
            self.log_step(f"图像质量分析异常: {str(e)}", 'ERROR')
            return {
                "success": False,
                "message": f"图像质量分析异常: {str(e)}"
            }