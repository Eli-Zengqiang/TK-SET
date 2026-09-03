from ..base import BaseTestCase, TestCaseConfig, TestResult, TestStatus, TestType
import time
import math
# 新增导入，用于实现用户交互对话框
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QMessageBox, QApplication
import threading


class MinMotorControlTest(BaseTestCase):
    """小电机控制测试 - 包含限位检测和用户异响确认"""

    # 新增信号：用于请求用户进行异响确认
    noise_confirmation_requested = pyqtSignal(str, int, int)  # 参数：测试名称，当前步骤，总步骤数
    # 新增信号：用于从主线程接收用户确认结果
    noise_confirmation_result_received = pyqtSignal(object)  # 参数：True(无异常)/False(有异常)/None(取消)

    def __init__(self, config: TestCaseConfig, api_client=None, logger=None):
        """初始化，设置线程同步对象并连接信号"""
        super().__init__(config, api_client, logger)
        # 用于线程同步的事件和结果变量
        self._noise_confirmation_event = threading.Event()
        self._user_noise_confirmation_result = None
        # 连接信号到槽，确保跨线程调用安全
        self.noise_confirmation_requested.connect(self._on_noise_confirmation_requested, Qt.QueuedConnection)
        self.noise_confirmation_result_received.connect(self._on_noise_confirmation_result_received,
                                                        Qt.QueuedConnection)

    def setup(self) -> bool:
        """测试前置准备"""
        self.log_step("开始小电机控制测试前置准备", "INFO")

        try:
            # 检查API客户端连接
            if not self.api_client:
                self.log_step("API客户端未连接，无法执行小电机测试", "ERROR")
                return False

            self.log_step("API客户端连接正常", "INFO")

            # 小电机上电
            self.log_step("开始小电机上电操作", "INFO")
            self.api_client.power_on("laser")
            power_result = self.api_client.power_on("motor")
            if power_result.get("success", False):
                self.log_step("✓ 小电机上电成功", "INFO")
                # 等待上电稳定
                time.sleep(1)
            else:
                error_msg = power_result.get("message", "未知错误")
                self.log_step(f"✗ 小电机上电失败: {error_msg}", "ERROR")
                return False

            return True

        except Exception as e:
            self.log_step(f"小电机测试前置准备异常: {str(e)}", "ERROR")
            return False

    def execute(self) -> TestResult:
        """执行小电机控制测试"""
        try:
            self.log_step("开始执行小电机控制测试", "INFO")

            # 获取测试参数
            detect_timeout = self.config.parameters.get('detect_timeout', 300)
            move_angle = self.config.parameters.get('move_angle', 5.0)
            cycles = self.config.parameters.get('cycles', 3)

            self.log_step(f"测试参数 - 限位检测超时: {detect_timeout}s", "INFO")
            self.log_step(f"测试参数 - 单次移动角度: {move_angle}°", "INFO")
            self.log_step(f"测试参数 - 循环次数: {cycles}", "INFO")

            results = []
            test_steps = []

            # 步骤1: 获取小电机限位角度
            self.log_step("步骤1: 开始获取小电机限位角度", "INFO")
            test_steps.append("获取限位角度")

            left_limit = None
            right_limit = None

            if self.api_client:
                try:
                    limit_result = self.api_client.min_motor_detect_limits(detect_timeout, 100)
                    if limit_result.get("success", False):
                        data = limit_result.get("data", {})
                        left_limit = data.get("left_limit_angle")
                        right_limit = data.get("right_limit_angle")

                        if left_limit is not None and right_limit is not None:
                            self.log_step(f"✓ 获取限位角度成功 - 左限位: {left_limit:.2f}°, 右限位: {right_limit:.2f}°",
                                          "INFO")
                            results.append(f"获取限位角度成功 (左:{left_limit:.2f}°, 右:{right_limit:.2f}°)")
                        else:
                            self.log_step("✗ 获取限位角度数据不完整", "ERROR")
                            results.append("获取限位角度数据不完整")
                            return TestResult(
                                test_name=self.config.name,
                                status=TestStatus.FAILED,
                                message="获取限位角度数据不完整，终止测试",
                                data={"results": results, "steps": test_steps}
                            )
                    else:
                        error_msg = limit_result.get("message", "未知错误")
                        self.log_step(f"✗ 获取限位角度失败: {error_msg}", "ERROR")
                        results.append(f"获取限位角度失败: {error_msg}")
                        return TestResult(
                            test_name=self.config.name,
                            status=TestStatus.FAILED,
                            message="获取限位角度失败，终止测试",
                            data={"results": results, "steps": test_steps}
                        )
                except Exception as e:
                    self.log_step(f"✗ 获取限位角度异常: {str(e)}", "ERROR")
                    results.append(f"获取限位角度异常: {str(e)}")
                    return TestResult(
                        test_name=self.config.name,
                        status=TestStatus.ERROR,
                        message=f"获取限位角度异常: {str(e)}",
                        error_info=str(e),
                        data={"results": results, "steps": test_steps}
                    )

            # 步骤2: 在限位范围内来回旋转测试
            self.log_step("步骤2: 开始限位范围内来回旋转测试", "INFO")
            test_steps.append("限位范围内旋转测试")

            if left_limit is not None and right_limit is not None:
                # 计算安全的起点和终点，避免撞击物理限位
                start_angle = left_limit + 5.0
                end_angle = right_limit - 5.0

                self.log_step(f"移动范围: {start_angle:.2f}° ~ {end_angle:.2f}°", "INFO")
                self.log_step(f"单步移动角度: {move_angle}°， 总循环次数: {cycles}", "INFO")

                # 步骤2.1: 移动到左侧测试点
                self.log_step(f"步骤2.1 - 绝对移动到左侧测试点: {start_angle:.2f}°", "INFO")
                try:
                    move_result = self.api_client.min_motor_set_angle(start_angle, 30)
                    if move_result.get("success", False):
                        self.log_step("✓ 移动到左侧测试点成功", "INFO")
                        results.append("绝对角度移动-左测试点成功")
                    else:
                        error_msg = move_result.get("message", "未知错误")
                        self.log_step(f"✗ 移动到左侧测试点失败: {error_msg}", "ERROR")
                        results.append(f"绝对角度移动-左测试点失败: {error_msg}")
                        return TestResult(
                            test_name=self.config.name,
                            status=TestStatus.FAILED,
                            message="绝对角度移动测试失败，终止测试",
                            data={"results": results, "steps": test_steps}
                        )
                except Exception as e:
                    self.log_step(f"✗ 移动到左侧测试点异常: {str(e)}", "ERROR")
                    results.append(f"绝对角度移动-左测试点异常: {str(e)}")
                    return TestResult(
                        test_name=self.config.name,
                        status=TestStatus.ERROR,
                        message=f"绝对角度移动测试异常: {str(e)}",
                        error_info=str(e),
                        data={"results": results, "steps": test_steps}
                    )

                time.sleep(1)  # 等待稳定

                # 步骤2.2: 移动到右侧测试点
                self.log_step(f"步骤2.2 - 绝对移动到右侧测试点: {end_angle:.2f}°", "INFO")
                try:
                    move_result = self.api_client.min_motor_set_angle(end_angle, 30)
                    if move_result.get("success", False):
                        self.log_step("✓ 移动到右侧测试点成功", "INFO")
                        results.append("绝对角度移动-右测试点成功")
                    else:
                        error_msg = move_result.get("message", "未知错误")
                        self.log_step(f"✗ 移动到右侧测试点失败: {error_msg}", "ERROR")
                        results.append(f"绝对角度移动-右测试点失败: {error_msg}")
                        return TestResult(
                            test_name=self.config.name,
                            status=TestStatus.FAILED,
                            message="绝对角度移动测试失败，终止测试",
                            data={"results": results, "steps": test_steps}
                        )
                except Exception as e:
                    self.log_step(f"✗ 移动到右侧测试点异常: {str(e)}", "ERROR")
                    results.append(f"绝对角度移动-右测试点异常: {str(e)}")
                    return TestResult(
                        test_name=self.config.name,
                        status=TestStatus.ERROR,
                        message=f"绝对角度移动测试异常: {str(e)}",
                        error_info=str(e),
                        data={"results": results, "steps": test_steps}
                    )

                time.sleep(1)  # 等待稳定




                # 执行循环测试
                for cycle in range(cycles):
                    if self.should_stop():
                        self.log_step("测试被用户停止", "INFO")
                        return TestResult(
                            test_name=self.config.name,
                            status=TestStatus.SKIPPED,
                            message="测试被用户停止",
                            data={"results": results, "steps": test_steps}
                        )

                    self.log_step(f"=== 开始第 {cycle + 1}/{cycles} 轮循环测试 ===", "INFO")

                    # 步骤2.1: 绝对移动至起点 (左限位+5°)
                    self.log_step(f"步骤2.3 - 绝对移动至起点: {start_angle:.2f}°", "INFO")
                    try:
                        move_result = self.api_client.min_motor_set_angle(start_angle, 30)
                        if move_result.get("success", False):
                            self.log_step("✓ 移动至起点成功", "INFO")
                            results.append(f"第{cycle + 1}轮-移动至起点成功")
                        else:
                            error_msg = move_result.get("message", "未知错误")
                            self.log_step(f"✗ 移动至起点失败: {error_msg}", "ERROR")
                            results.append(f"第{cycle + 1}轮-移动至起点失败: {error_msg}")
                            break
                    except Exception as e:
                        self.log_step(f"✗ 移动至起点异常: {str(e)}", "ERROR")
                        results.append(f"第{cycle + 1}轮-移动至起点异常: {str(e)}")
                        break

                    time.sleep(1)  # 等待稳定

                    # 步骤2.2: 从起点顺时针逐步相对移动至终点
                    self.log_step(f"步骤2.4 - 从起点顺时针移动至终点: {start_angle:.2f}° → {end_angle:.2f}°", "INFO")

                    # 计算顺时针旋转到终点需要的总角度
                    if start_angle > end_angle:
                        # 跨越0°边界的情况
                        cw_total_angle = (360.0 - start_angle) + end_angle
                    else:
                        # 正常情况
                        cw_total_angle = end_angle - start_angle

                    cw_moved = 0.0
                    cw_step_count = 0
                    cw_success = True

                    while cw_moved < cw_total_angle - 0.1:  # 0.1为误差容限
                        if self.should_stop():
                            self.log_step("测试被用户停止", "INFO")
                            return TestResult(...)  # 同上，返回SKIPPED结果

                        cw_step_count += 1

                        # 计算本次移动角度
                        remaining_angle = cw_total_angle - cw_moved
                        if remaining_angle <= 0:
                            break

                        move_angle_this_step = min(move_angle, remaining_angle)

                        # 计算当前位置的实际角度
                        current_actual_angle = (start_angle + cw_moved) % 360

                        self.log_step(
                            f"  顺时针第{cw_step_count}步: 当前角度{current_actual_angle:.2f}°，相对移动{move_angle_this_step:.2f}°",
                            "DEBUG")

                        try:
                            move_result = self.api_client.min_motor_relative_move(move_angle_this_step, 30)
                            if move_result.get("success", False):
                                cw_moved += move_angle_this_step
                                new_actual_angle = (start_angle + cw_moved) % 360
                                self.log_step(
                                    f"    -> 移动成功，当前位置: {new_actual_angle:.2f}°，已移动角度: {cw_moved:.2f}°",
                                    "DEBUG")
                            else:
                                error_msg = move_result.get("message", "未知错误")
                                self.log_step(f"✗ 顺时针第{cw_step_count}步移动失败: {error_msg}", "ERROR")
                                #results.append(f"第{cycle + 1}轮顺时针旋转-第{cw_step_count}步移动失败: {error_msg}")
                                cw_success = False
                                break
                        except Exception as e:
                            self.log_step(f"✗ 顺时针第{cw_step_count}步移动异常: {str(e)}", "ERROR")
                            #results.append(f"第{cycle + 1}轮顺时针旋转-第{cw_step_count}步移动异常: {str(e)}")
                            cw_success = False
                            break

                        time.sleep(0.5)  # 每步移动后短暂等待

                    if not cw_success:
                        self.log_step(f"✗ 第{cycle + 1}轮顺时针旋转失败，跳过本轮剩余测试", "ERROR")
                        continue

                    # 检查顺时针移动是否完成
                    if cw_moved >= cw_total_angle - 0.1:
                        final_angle = (start_angle + cw_moved) % 360
                        self.log_step(
                            f"✓ 第{cycle + 1}轮顺时针旋转 - 已逐步移动至终点附近 ({final_angle:.2f}°)，总移动角度: {cw_moved:.2f}°",
                            "INFO")
                        results.append(f"第{cycle + 1}轮顺时针旋转-到达终点成功")
                    else:
                        self.log_step(
                            f"✗ 第{cycle + 1}轮顺时针旋转 - 在逐步移动至终点过程中失败，已移动角度: {cw_moved:.2f}°/需移动{cw_total_angle:.2f}°",
                            "ERROR")
                        continue

                    time.sleep(1)  # 在终点处等待稳定

                    # 步骤2.3: 从终点逆时针逐步相对移动回起点
                    self.log_step(f"步骤2.5 - 从终点逆时针移动回起点: {end_angle:.2f}° → {start_angle:.2f}°", "INFO")
                    ccw_total_angle=cw_total_angle

                    # 当前角度应该是终点角度
                    current_angle_at_end = (start_angle + cw_moved) % 360
                    ccw_moved = 0.0
                    ccw_step_count = 0
                    ccw_success = True

                    while ccw_moved < ccw_total_angle - 0.1:  # 0.1为误差容限
                        if self.should_stop():
                            self.log_step("测试被用户停止", "INFO")
                            return TestResult(...)  # 同上，返回SKIPPED结果

                        ccw_step_count += 1

                        # 计算本次移动角度（负值，逆时针）
                        remaining_angle = ccw_total_angle - ccw_moved
                        if remaining_angle <= 0:
                            break

                        move_angle_this_step = -min(move_angle, remaining_angle)  # 负值表示逆时针

                        # 计算当前位置的实际角度
                        current_actual_angle = (current_angle_at_end - ccw_moved) % 360

                        self.log_step(
                            f"  逆时针第{ccw_step_count}步: 当前角度{current_actual_angle:.2f}°，相对移动{move_angle_this_step:.2f}°",
                            "DEBUG")

                        try:
                            move_result = self.api_client.min_motor_relative_move(move_angle_this_step, 30)
                            if move_result.get("success", False):
                                ccw_moved += abs(move_angle_this_step)  # 记录移动的绝对值
                                new_actual_angle = (current_angle_at_end - ccw_moved) % 360
                                self.log_step(
                                    f"    -> 移动成功，当前位置: {new_actual_angle:.2f}°，已移动角度: {ccw_moved:.2f}°",
                                    "DEBUG")
                            else:
                                error_msg = move_result.get("message", "未知错误")
                                self.log_step(f"✗ 逆时针第{ccw_step_count}步移动失败: {error_msg}", "ERROR")
                                #results.append(f"第{cycle + 1}轮逆时针旋转-第{ccw_step_count}步移动失败: {error_msg}")
                                ccw_success = False
                                break
                        except Exception as e:
                            self.log_step(f"✗ 逆时针第{ccw_step_count}步移动异常: {str(e)}", "ERROR")
                            #results.append(f"第{cycle + 1}轮逆时针旋转-第{ccw_step_count}步移动异常: {str(e)}")
                            ccw_success = False
                            break

                        time.sleep(0.5)  # 每步移动后短暂等待

                    if not ccw_success:
                        self.log_step(f"✗ 第{cycle + 1}轮逆时针旋转失败", "ERROR")
                        continue

                    # 检查逆时针移动是否完成
                    if ccw_moved >= ccw_total_angle - 0.1:
                        final_angle = (current_angle_at_end - ccw_moved) % 360
                        self.log_step(
                            f"✓ 第{cycle + 1}轮逆时针旋转 - 已逐步移动回起点附近 ({final_angle:.2f}°)，总移动角度: {ccw_moved:.2f}°",
                            "INFO")
                        results.append(f"第{cycle + 1}轮逆时针旋转-返回起点成功")
                    else:
                        self.log_step(
                            f"✗ 第{cycle + 1}轮逆时针旋转 - 在逐步移动回起点过程中失败，已移动角度: {ccw_moved:.2f}°/需移动{ccw_total_angle:.2f}°",
                            "ERROR")
                        continue

                    time.sleep(1)  # 在起点处等待稳定，准备下一轮循环

            # 步骤3: 用户异响确认
            self.log_step("步骤3: 等待用户确认运行期间是否有异常声响", "INFO")
            test_steps.append("用户异响确认")

            # 等待一小段时间，确保小电机完全静止，便于用户判断
            time.sleep(1)

            # 调用对话框方法，获取用户确认结果
            noise_check_result = self.show_noise_confirmation_dialog(
                self.config.name, 1, 1
            )

            # 根据用户选择记录结果
            noise_check_passed = False
            noise_check_status_str = ""
            if noise_check_result is True:
                self.log_step("✓ 用户确认小电机运行无异常声响", "INFO")
                results.append("用户确认无异常声响-成功")
                noise_check_passed = True
                noise_check_status_str = "用户确认无异常声响"
            elif noise_check_result is False:
                self.log_step("✗ 用户报告小电机运行存在异常声响", "ERROR")
                results.append("用户报告存在异常声响")
                noise_check_status_str = "用户报告存在异常声响"
            elif noise_check_result is None:
                self.log_step("⚠ 用户取消了异响确认步骤", "WARNING")
                results.append("用户取消了异响确认")
                noise_check_status_str = "用户取消了异响确认"
            else:  # 理论上不会进入，容错处理
                self.log_step("⚠ 异响确认对话框返回了未知结果", "WARNING")
                results.append("异响确认结果未知")
                noise_check_status_str = "异响确认结果未知"

            # 测试总结
            passed_count = len([r for r in results if "成功" in r or "通过" in r])
            total_count = len(results)
            pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0

            self.log_step(f"小电机自动化测试完成 - 通过: {passed_count}/{total_count} ({pass_rate:.1f}%)", "INFO")
            self.log_step(f"用户异响确认结果: {noise_check_status_str}", "INFO")

            # 综合判定：自动化测试通过率>=80% 且 用户确认无异常
            overall_passed = (pass_rate >= 80) and noise_check_passed

            status = TestStatus.PASSED if overall_passed else TestStatus.FAILED
            message = f"小电机控制测试完成。自动化步骤通过率: {pass_rate:.1f}%。{noise_check_status_str}。"
            if overall_passed:
                message += "整体测试通过。"
            else:
                if pass_rate < 80:
                    message += "自动化步骤通过率未达标。"
                if not noise_check_passed:
                    message += "异响确认未通过。"

            return TestResult(
                test_name=self.config.name,
                status=status,
                message=message,
                data={
                    "results": results,
                    "steps": test_steps,
                    "passed_count": passed_count,
                    "total_count": total_count,
                    "pass_rate": pass_rate,
                    "noise_check_passed": noise_check_passed,
                    "noise_check_result": noise_check_result,
                    "left_limit": left_limit,
                    "right_limit": right_limit
                }
            )

        except Exception as e:
            self.log_step(f"小电机控制测试执行异常: {str(e)}", "ERROR")
            return TestResult(
                test_name=self.config.name,
                status=TestStatus.ERROR,
                message=f"小电机控制测试执行异常: {str(e)}",
                error_info=str(e)
            )

    def show_noise_confirmation_dialog(self, test_name: str, current_step: int, total_steps: int) -> bool | None:
        """显示异响确认对话框（线程安全版本）"""
        self.log_step(f"请求用户确认小电机运行是否有异常声响", "DEBUG")
        # 重置事件和结果
        self._noise_confirmation_event.clear()
        self._user_noise_confirmation_result = None

        # 发射信号，请求主线程弹出对话框
        self.noise_confirmation_requested.emit(test_name, current_step, total_steps)

        # 等待结果返回（可被停止请求中断），参考LED测试中的`wait_for_event`方法
        try:
            if not self.wait_for_event(self._noise_confirmation_event, timeout=300):  # 设置超时，例如300秒
                self.log_step(f"等待用户异响确认超时", "WARNING")
                return None
        except RuntimeError as e:
            if "停止" in str(e):
                self.log_step(f"等待用户异响确认被停止请求中断", "INFO")
                return None
            raise
        # 返回用户的选择结果 (True: 无异常, False: 有异常, None: 取消)
        return self._user_noise_confirmation_result

    @pyqtSlot(str, int, int)
    def _on_noise_confirmation_requested(self, test_name: str, current_step: int, total_steps: int):
        """此槽函数在主线程执行，负责创建并显示异响确认对话框。"""
        try:
            app = QApplication.instance()
            if app is None:
                # 理论上测试环境应该已有QApplication实例
                return None

            msg_box = QMessageBox()
            msg_box.setWindowTitle("小电机异响确认")
            msg_box.setText(f"请确认小电机在刚才的测试运行中是否有异常声响？\n\n测试项目: {test_name}")
            msg_box.setInformativeText("请根据您听到的声音判断。\n\n注意：无异常声响方可判定为测试通过。")

            # 按钮文本根据业务需求定义
            silent_button = msg_box.addButton("✅ 无异常声响", QMessageBox.YesRole)  # 对应 True
            noisy_button = msg_box.addButton("❌ 有异常声响", QMessageBox.NoRole)  # 对应 False
            cancel_button = msg_box.addButton("取消确认", QMessageBox.RejectRole)  # 对应 None

            msg_box.setDefaultButton(silent_button)
            msg_box.setIcon(QMessageBox.Question)

            result = msg_box.exec_()

            user_choice = None
            if msg_box.clickedButton() == silent_button:
                user_choice = True
                self.log_step(f"用户在主线程确认小电机运行无异常声响")
            elif msg_box.clickedButton() == noisy_button:
                user_choice = False
                self.log_step(f"用户在主线程报告小电机运行存在异常声响")
            else:
                # 点击"取消确认"或关闭窗口
                self.log_step(f"用户在主线程取消了异响确认")
                user_choice = None

            # 将结果发送回请求的线程
            self.noise_confirmation_result_received.emit(user_choice)

        except Exception as e:
            self.log_step(f"在主线程显示异响确认对话框时发生异常: {str(e)}", "ERROR")
            self.noise_confirmation_result_received.emit(None)

    @pyqtSlot(object)
    def _on_noise_confirmation_result_received(self, result: bool | None):
        """此槽函数在发出请求的原始线程中执行，用于接收结果并唤醒等待线程。"""
        self._user_noise_confirmation_result = result
        self._noise_confirmation_event.set()

    def teardown(self) -> bool:
        """测试后置清理"""
        try:
            self.log_step("开始小电机控制测试后置清理", "INFO")

            # 小电机断电
            self.log_step("开始小电机断电操作", "INFO")
            if self.api_client:
                try:
                    self.api_client.power_off("laser")
                    power_result = self.api_client.power_off("motor")
                    if power_result.get("success", False):
                        self.log_step("✓ 小电机断电成功", "INFO")
                    else:
                        error_msg = power_result.get("message", "未知错误")
                        self.log_step(f"⚠ 小电机断电失败: {error_msg}", "WARNING")
                except Exception as e:
                    self.log_step(f"⚠ 小电机断电异常: {str(e)}", "WARNING")

            self.log_step("小电机控制测试后置清理完成", "INFO")
            return True

        except Exception as e:
            self.log_step(f"小电机控制测试后置清理异常: {str(e)}", "WARNING")
            return False
