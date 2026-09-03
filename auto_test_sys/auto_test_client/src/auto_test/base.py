"""自动化测试框架基础模块"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Type
from dataclasses import dataclass, field
from enum import Enum
import time
import logging
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
import threading


class TestStatus(Enum):
    """测试状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestType(Enum):
    """测试类型枚举"""
    FUNCTIONAL = "functional"      # 功能测试
    PERFORMANCE = "performance"    # 性能测试
    STABILITY = "stability"        # 稳定性测试
    COMPATIBILITY = "compatibility" # 兼容性测试
    REGRESSION = "regression"      # 回归测试


@dataclass
class TestResult:
    """测试结果数据类"""
    test_name: str
    status: TestStatus
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: float = 0.0
    error_info: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "test_name": self.test_name,
            "status": self.status.value,
            "message": self.message,
            "data": self.data,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "error_info": self.error_info
        }


@dataclass
class TestCaseConfig:
    """测试用例配置"""
    name: str
    description: str = ""
    test_class: str = ""  # 测试类名
    test_type: TestType = TestType.FUNCTIONAL
    priority: int = 1  # 优先级 1-5，1最高
    timeout: int = 300  # 超时时间(秒)
    retry_count: int = 0  # 重试次数
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # 依赖的测试用例


class BaseTestCase(QObject):
    """测试用例基类"""

    # 进程日志信号
    process_log = pyqtSignal(str, str)  # (log_level, message)
    step_progress = pyqtSignal(str, int, int)  # (step_description, current, total)

    def __init__(self, config, api_client=None, logger=None):
        QObject.__init__(self)  # 先初始化QObject
        self.config = config
        self.api_client = api_client
        self.logger = logger or logging.getLogger(__name__)
        self.result: Optional[TestResult] = None

        # 【核心修改1】增强停止控制：使用线程锁保护标志，并添加一个通用事件用于唤醒等待
        self._should_stop = False
        self._stop_lock = threading.RLock()  # 改为可重入锁，更安全
        self._cancellation_event = threading.Event()  # 新增：用于中断 sleep、wait 等阻塞操作

    @abstractmethod
    def setup(self) -> bool:
        """
        测试前置准备
        返回True表示准备成功，False表示准备失败
        """
        pass

    @abstractmethod
    def execute(self) -> TestResult:
        """
        执行测试逻辑
        返回测试结果
        """
        pass

    @abstractmethod
    def teardown(self) -> bool:
        """
        测试后置清理
        返回True表示清理成功，False表示清理失败
        """
        pass

    def run(self) -> TestResult:
        """
        运行完整的测试流程
        """
        # 【核心修改2】在run开始前，重置停止标志和事件，确保状态干净
        with self._stop_lock:
            self._should_stop = False
            self._cancellation_event.clear()

        start_time = datetime.now()

        try:
            # 检查是否应该停止
            if self.should_stop():  # 改为调用线程安全的方法
                self.process_log.emit("INFO", "测试在开始前被用户停止")
                self.result = TestResult(
                    test_name=self.config.name,
                    status=TestStatus.SKIPPED,
                    message="测试在开始前被用户停止",
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=(datetime.now() - start_time).total_seconds()
                )
                return self.result

            # 发送测试开始信号
            self.process_log.emit("INFO", f"开始执行测试: {self.config.name}")
            self.step_progress.emit(f"执行测试: {self.config.name}", 1, 3)

            # 前置准备
            self.process_log.emit("INFO", "开始前置准备...")
            if self.should_stop():  # 改为调用线程安全的方法
                self.process_log.emit("INFO", "测试被用户停止")
                self.result = TestResult(
                    test_name=self.config.name,
                    status=TestStatus.SKIPPED,
                    message="测试被用户停止",
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=(datetime.now() - start_time).total_seconds()
                )
                return self.result

            if not self.setup():
                self.process_log.emit("ERROR", "测试前置准备失败")
                self.result = TestResult(
                    test_name=self.config.name,
                    status=TestStatus.ERROR,
                    message="测试前置准备失败",
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=(datetime.now() - start_time).total_seconds()
                )
                return self.result
            self.process_log.emit("INFO", "前置准备完成")
            self.step_progress.emit(f"执行测试: {self.config.name}", 2, 3)

            # 执行测试
            self.process_log.emit("INFO", "开始执行测试逻辑...")
            if self.should_stop():  # 改为调用线程安全的方法
                self.process_log.emit("INFO", "测试被用户停止")
                self.result = TestResult(
                    test_name=self.config.name,
                    status=TestStatus.SKIPPED,
                    message="测试被用户停止",
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=(datetime.now() - start_time).total_seconds()
                )
                return self.result

            self.result = self.execute()
            self.result.start_time = start_time
            self.result.end_time = datetime.now()
            self.result.duration = (self.result.end_time - start_time).total_seconds()

            # 发送测试完成信号
            status_text = "通过" if self.result.status == TestStatus.PASSED else "失败"
            self.process_log.emit("INFO", f"测试执行完成: {status_text} - {self.result.message}")
            self.step_progress.emit(f"执行测试: {self.config.name}", 3, 3)

            return self.result

        except RuntimeError as e:
            # 【核心修改3】捕获由 check_stop_and_throw 抛出的停止异常
            if "测试被用户停止" in str(e):
                self.process_log.emit("INFO", f"测试执行被中断: {str(e)}")
                self.result = TestResult(
                    test_name=self.config.name,
                    status=TestStatus.SKIPPED,
                    message=str(e),
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=(datetime.now() - start_time).total_seconds()
                )
                return self.result
            else:
                # 其他RuntimeError按原逻辑处理
                self.process_log.emit("ERROR", f"测试执行异常: {str(e)}")
                self.result = TestResult(
                    test_name=self.config.name,
                    status=TestStatus.ERROR,
                    message=f"测试执行异常: {str(e)}",
                    error_info=str(e),
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=(datetime.now() - start_time).total_seconds()
                )
                self.logger.error(f"测试执行异常: {self.config.name} - {str(e)}")
                return self.result
        except Exception as e:
            self.process_log.emit("ERROR", f"测试执行异常: {str(e)}")
            self.result = TestResult(
                test_name=self.config.name,
                status=TestStatus.ERROR,
                message=f"测试执行异常: {str(e)}",
                error_info=str(e),
                start_time=start_time,
                end_time=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds()
            )
            self.logger.error(f"测试执行异常: {self.config.name} - {str(e)}")
            return self.result

        finally:
            # 后置清理
            try:
                if not self.should_stop():  # 改为调用线程安全的方法
                    self.process_log.emit("INFO", "开始后置清理...")
                    self.teardown()
                    self.process_log.emit("INFO", "后置清理完成")
            except Exception as e:
                self.process_log.emit("WARNING", f"测试后置清理异常: {str(e)}")
                self.logger.warning(f"测试后置清理异常: {self.config.name} - {str(e)}")

    def wait_for_condition(self, condition_func, timeout: int = 30,
                           interval: float = 1.0, description: str = "") -> bool:
        """
        等待条件满足

        Args:
            condition_func: 条件检查函数，返回bool
            timeout: 超时时间(秒)
            interval: 检查间隔(秒)
            description: 条件描述

        Returns:
            bool: True表示条件满足，False表示超时或被停止
        """
        start_time = time.time()

        # 发送等待开始信号
        if description:
            self.process_log.emit("INFO", f"等待条件: {description} (超时: {timeout}s)")

        while time.time() - start_time < timeout:
            # 检查是否应该停止
            if self.should_stop():  # 改为调用线程安全的方法
                self.process_log.emit("INFO", "等待被用户中断")
                return False

            if condition_func():
                self.logger.info(f"条件满足: {description}")
                if description:
                    self.process_log.emit("INFO", f"条件满足: {description}")
                return True

            # 发送等待进度信号
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            if description and elapsed % 5 == 0:  # 每5秒报告一次
                self.process_log.emit("INFO", f"等待中... 剩余时间: {remaining}s")

            # 【核心修改4】使用可中断的sleep，以便及时响应停止请求
            self.sleep_with_interrupt(interval)
            # 注意：原 time.sleep(interval) 被替换为上述方法

        # 检查停止标志，以区分是超时还是被停止
        if self.should_stop():
            self.logger.info(f"等待被用户中断: {description}")
            if description:
                self.process_log.emit("INFO", f"等待被用户中断: {description}")
            return False

        self.logger.warning(f"等待条件超时: {description} (timeout: {timeout}s)")
        if description:
            self.process_log.emit("WARNING", f"等待条件超时: {description} (timeout: {timeout}s)")
        return False

    def stop_test(self):
        """
        停止测试执行
        """
        with self._stop_lock:  # 加锁保证线程安全
            if not self._should_stop:
                self._should_stop = True
                self._cancellation_event.set()  # 设置事件，唤醒可能正在等待的线程
                self.process_log.emit("INFO", "收到停止测试指令")

    # ========== 【核心新增方法】以下是为支持优雅停止而新增的公共方法 ==========

    def should_stop(self) -> bool:
        """
        线程安全地检查是否收到停止请求。
        子类在其 `execute()` 方法内部的循环或长时间操作中，应定期调用此方法。
        如果返回 True，则用例应尽快、安全地清理资源并退出。
        """
        with self._stop_lock:
            return self._should_stop

    def check_stop_and_throw(self, message: str = "测试被用户停止"):
        """
        一个更严格的检查方法：如果停止请求被标记，则直接抛出 RuntimeError 以中断执行流。
        子类可以根据需要选择使用 `should_stop()` 或本方法。
        这对于中断深度嵌套的调用或难以传播返回值的场景很有用。
        """
        if self.should_stop():
            raise RuntimeError(message)

    def sleep_with_interrupt(self, seconds: float):
        """
        可被停止请求中断的 sleep 方法。
        替代 time.sleep()，在等待期间会定期检查停止标志。

        Args:
            seconds: 需要休眠的总秒数
        """
        if seconds <= 0:
            return

        start = time.time()
        while time.time() - start < seconds:
            # 每次只睡一小段时间，以便快速响应停止
            remain = seconds - (time.time() - start)
            sleep_interval = min(0.5, remain)  # 最多睡0.5秒

            if sleep_interval <= 0:
                break

            # 使用事件等待，可被 set() 提前唤醒
            if self._cancellation_event.wait(timeout=sleep_interval):
                # 事件被设置，意味着收到了停止请求
                self._cancellation_event.clear()  # 清除事件状态以供下次使用
                if self.should_stop():
                    raise RuntimeError("休眠被停止请求中断")

    def wait_for_event(self, event: threading.Event, timeout: Optional[float] = None) -> bool:
        """
        等待一个 threading.Event，但可被停止请求中断。
        这是对 `_cancellation_event` 的封装，为子类提供便利。

        Args:
            event: 要等待的事件对象
            timeout: 超时时间(秒)，None表示无限等待

        Returns:
            bool: 如果事件在超时前被设置，返回True；否则返回False。
                  如果在等待过程中收到停止请求，会抛出 RuntimeError。
        """
        if timeout is None:
            # 无限等待，需要循环检查停止
            while not event.is_set():
                if self._cancellation_event.wait(timeout=0.5):
                    self._cancellation_event.clear()
                    if self.should_stop():
                        raise RuntimeError("等待被停止请求中断")
            return True
        else:
            # 有限时间等待
            start = time.time()
            while time.time() - start < timeout:
                if event.is_set():
                    return True

                remain = timeout - (time.time() - start)
                wait_time = min(0.5, remain)

                if wait_time <= 0:
                    break

                if self._cancellation_event.wait(timeout=wait_time):
                    self._cancellation_event.clear()
                    if self.should_stop():
                        raise RuntimeError("等待被停止请求中断")

            return event.is_set()

    def log_step(self, message: str, level: str = "INFO"):
        """
        记录测试步骤日志

        Args:
            message: 日志消息
            level: 日志级别 (INFO, WARNING, ERROR, DEBUG)
        """
        # 检查是否应该停止 (原逻辑保留，但INFO级别也允许记录停止相关日志)
        if self.should_stop() and level == "INFO" and "停止" not in message:
            return
        formatted_message = f"[{self.config.name}] {message}"
        self.process_log.emit(level, formatted_message)

        # # 同时记录到标准日志
        # if level == "INFO":
        #     self.logger.info(message)
        # elif level == "WARNING":
        #     self.logger.warning(message)
        # elif level == "ERROR":
        #     self.logger.error(message)
        # elif level == "DEBUG":
        #     self.logger.debug(message)


@dataclass
class TestTemplate:
    """测试模板"""
    name: str
    description: str
    test_cases: List[TestCaseConfig] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def add_test_case(self, test_case: TestCaseConfig):
        """添加测试用例"""
        self.test_cases.append(test_case)
    
    def remove_test_case(self, test_case_name: str) -> bool:
        """移除测试用例"""
        for i, case in enumerate(self.test_cases):
            if case.name == test_case_name:
                self.test_cases.pop(i)
                return True
        return False
    
    def get_test_case(self, test_case_name: str) -> Optional[TestCaseConfig]:
        """获取测试用例"""
        for case in self.test_cases:
            if case.name == test_case_name:
                return case
        return None


class TestSuite:
    """测试套件 - 管理多个测试用例的执行"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.test_cases: List[BaseTestCase] = []
        self.results: List[TestResult] = []
        self.logger = logging.getLogger(__name__)
    
    def add_test_case(self, test_case: BaseTestCase):
        """添加测试用例"""
        self.test_cases.append(test_case)
    
    def remove_test_case(self, test_case_name: str) -> bool:
        """移除测试用例"""
        for i, case in enumerate(self.test_cases):
            if case.config.name == test_case_name:
                self.test_cases.pop(i)
                return True
        return False
    
    def run_all(self, stop_on_failure: bool = False) -> List[TestResult]:
        """
        运行所有测试用例
        
        Args:
            stop_on_failure: 是否在第一个失败时停止
            
        Returns:
            List[TestResult]: 所有测试结果列表
        """
        self.results.clear()
        
        self.logger.info(f"开始运行测试套件: {self.name}")
        self.logger.info(f"共 {len(self.test_cases)} 个测试用例")
        
        for i, test_case in enumerate(self.test_cases, 1):
            self.logger.info(f"运行测试用例 ({i}/{len(self.test_cases)}): {test_case.config.name}")
            
            try:
                result = test_case.run()
                self.results.append(result)
                
                # 记录结果
                if result.status == TestStatus.PASSED:
                    self.logger.info(f"✓ 测试通过: {test_case.config.name}")
                elif result.status == TestStatus.FAILED:
                    self.logger.warning(f"✗ 测试失败: {test_case.config.name} - {result.message}")
                else:
                    self.logger.error(f"⚠ 测试异常: {test_case.config.name} - {result.message}")
                
                # 检查是否需要停止
                if stop_on_failure and result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                    self.logger.warning(f"因测试失败而停止执行后续测试")
                    break
                    
            except Exception as e:
                error_result = TestResult(
                    test_name=test_case.config.name,
                    status=TestStatus.ERROR,
                    message=f"测试套件执行异常: {str(e)}",
                    error_info=str(e)
                )
                self.results.append(error_result)
                self.logger.error(f"测试套件执行异常: {test_case.config.name} - {str(e)}")
                
                if stop_on_failure:
                    break
        
        self.logger.info(f"测试套件执行完成: {self.name}")
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """获取测试汇总信息"""
        total = len(self.results)
        passed = len([r for r in self.results if r.status == TestStatus.PASSED])
        failed = len([r for r in self.results if r.status == TestStatus.FAILED])
        errors = len([r for r in self.results if r.status == TestStatus.ERROR])
        skipped = len([r for r in self.results if r.status == TestStatus.SKIPPED])
        
        return {
            "suite_name": self.name,
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "error_tests": errors,
            "skipped_tests": skipped,
            "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
            "results": [r.to_dict() for r in self.results]
        }
