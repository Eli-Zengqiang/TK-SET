"""测试模板管理器"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml

from .base import TestTemplate, TestCaseConfig, TestType


class TemplateManager:
    """测试模板管理器"""
    
    def __init__(self, template_dir: str = None):
        """
        初始化模板管理器
        
        Args:
            template_dir: 模板文件存储目录
        """
        if template_dir is None:
            # 默认使用文件目录下的templates文件夹
            current_dir = Path(__file__).parent
            self.template_dir = current_dir / "templates"
            print(f"模板目录: {self.template_dir}")
        else:
            self.template_dir = Path(template_dir)
        
        # 确保目录存在
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # 内存中的模板缓存
        self._templates: Dict[str, TestTemplate] = {}
        
        # 加载现有模板
        self.load_templates()
    
    def load_templates(self):
        """从文件系统加载所有模板"""
        self._templates.clear()
        
        # 支持的文件格式
        extensions = ['.yaml', '.yml', '.json']
        
        for ext in extensions:
            pattern = f"*{ext}"
            for file_path in self.template_dir.glob(pattern):
                try:
                    template = self._load_template_from_file(file_path)
                    if template:
                        self._templates[template.name] = template
                        print(f"加载模板: {template.name}")
                except Exception as e:
                    print(f"加载模板文件失败 {file_path}: {str(e)}")
    
    def _load_template_from_file(self, file_path: Path) -> Optional[TestTemplate]:
        """从文件加载单个模板"""
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:  # json
                data = json.load(f)
        
        return self._dict_to_template(data)
    
    def _dict_to_template(self, data: Dict[str, Any]) -> TestTemplate:
        """将字典转换为测试模板对象"""
        # 创建测试用例配置
        test_cases = []
        for case_data in data.get('test_cases', []):
            test_case = TestCaseConfig(
                name=case_data['name'],
                description=case_data.get('description', ''),
                test_class=case_data.get('test_class', ''),
                test_type=TestType(case_data.get('test_type', 'functional')),
                priority=case_data.get('priority', 1),
                timeout=case_data.get('timeout', 300),
                retry_count=case_data.get('retry_count', 0),
                enabled=case_data.get('enabled', True),
                parameters=case_data.get('parameters', {}),
                dependencies=case_data.get('dependencies', [])
            )
            test_cases.append(test_case)
        
        return TestTemplate(
            name=data['name'],
            description=data.get('description', ''),
            test_cases=test_cases,
            parameters=data.get('parameters', {})
        )
    
    def _template_to_dict(self, template: TestTemplate) -> Dict[str, Any]:
        """将测试模板对象转换为字典"""
        test_cases_data = []
        for case in template.test_cases:
            case_data = {
                'name': case.name,
                'description': case.description,
                'test_class': case.test_class,
                'test_type': case.test_type.value,
                'priority': case.priority,
                'timeout': case.timeout,
                'retry_count': case.retry_count,
                'enabled': case.enabled,
                'parameters': case.parameters,
                'dependencies': case.dependencies
            }
            test_cases_data.append(case_data)
        
        return {
            'name': template.name,
            'description': template.description,
            'test_cases': test_cases_data,
            'parameters': template.parameters
        }
    
    def save_template(self, template: TestTemplate, format_type: str = 'yaml') -> bool:
        """
        保存模板到文件
        
        Args:
            template: 测试模板对象
            format_type: 文件格式 ('yaml' 或 'json')
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 更新内存缓存
            self._templates[template.name] = template
            
            # 准备文件路径
            if format_type.lower() == 'json':
                file_path = self.template_dir / f"{template.name}.json"
            else:
                file_path = self.template_dir / f"{template.name}.yaml"
            
            # 转换为字典格式
            data = self._template_to_dict(template)
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                if format_type.lower() == 'json':
                    json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    yaml.dump(data, f, allow_unicode=True, default_flow_style=False, indent=2)
            
            print(f"模板已保存: {file_path}")
            return True
            
        except Exception as e:
            print(f"保存模板失败: {str(e)}")
            return False
    
    def get_template(self, name: str) -> Optional[TestTemplate]:
        """
        获取模板
        
        Args:
            name: 模板名称
            
        Returns:
            TestTemplate: 模板对象，如果不存在返回None
        """
        return self._templates.get(name)
    
    def get_all_templates(self) -> List[TestTemplate]:
        """获取所有模板"""
        return list(self._templates.values())
    
    def get_template_names(self) -> List[str]:
        """获取所有模板名称"""
        return list(self._templates.keys())
    
    def template_exists(self, name: str) -> bool:
        """检查模板是否存在"""
        return name in self._templates
    
    def delete_template(self, name: str) -> bool:
        """
        删除模板
        
        Args:
            name: 模板名称
            
        Returns:
            bool: 删除是否成功
        """
        if name not in self._templates:
            return False
        
        # 从内存中删除
        del self._templates[name]
        
        # 删除文件
        for ext in ['.yaml', '.yml', '.json']:
            file_path = self.template_dir / f"{name}{ext}"
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"删除模板文件: {file_path}")
                    return True
                except Exception as e:
                    print(f"删除模板文件失败: {str(e)}")
        
        return True
    
    def create_template(self, name: str, description: str = "") -> TestTemplate:
        """
        创建新模板
        
        Args:
            name: 模板名称
            description: 模板描述
            
        Returns:
            TestTemplate: 新创建的模板对象
        """
        if self.template_exists(name):
            raise ValueError(f"模板 '{name}' 已存在")
        
        template = TestTemplate(name=name, description=description)
        self._templates[name] = template
        return template
    
    def add_test_case_to_template(self, template_name: str, 
                                test_case: TestCaseConfig) -> bool:
        """
        向模板添加测试用例
        
        Args:
            template_name: 模板名称
            test_case: 测试用例配置
            
        Returns:
            bool: 添加是否成功
        """
        template = self.get_template(template_name)
        if not template:
            return False
        
        # 检查是否已存在同名测试用例
        if template.get_test_case(test_case.name):
            print(f"测试用例 '{test_case.name}' 在模板 '{template_name}' 中已存在")
            return False
        
        template.add_test_case(test_case)
        return True
    
    def remove_test_case_from_template(self, template_name: str, 
                                     test_case_name: str) -> bool:
        """
        从模板移除测试用例
        
        Args:
            template_name: 模板名称
            test_case_name: 测试用例名称
            
        Returns:
            bool: 移除是否成功
        """
        template = self.get_template(template_name)
        if not template:
            return False
        
        return template.remove_test_case(test_case_name)
    
    def reload_templates(self):
        """重新加载所有模板"""
        print("重新加载所有模板...")
        self.load_templates()


# 预定义的常用模板
PREDEFINED_TEMPLATES = {
    "basic_function_test": {
        "name": "基础功能测试",
        "description": "包含基本功能验证的测试模板",
        "test_cases": [
            {
                "name": "系统连接测试",
                "description": "验证与服务器的基本连接",
                "test_type": "functional",
                "priority": 1,
                "timeout": 30,
                "parameters": {
                    "expected_response": "pong"
                }
            },
            {
                "name": "设备状态查询",
                "description": "查询各设备的基本状态",
                "test_type": "functional",
                "priority": 2,
                "timeout": 60,
                "parameters": {}
            }
        ]
    },
    
    "comprehensive_test": {
        "name": "综合测试",
        "description": "全面的硬件功能测试",
        "test_cases": [
            {
                "name": "电源管理测试",
                "description": "测试电源模块的开关功能",
                "test_type": "functional",
                "priority": 1,
                "timeout": 120,
                "parameters": {
                    "modules": ["radar", "motor", "camera1"]
                }
            },
            {
                "name": "电机控制测试",
                "description": "测试电机的基本控制功能",
                "test_type": "functional",
                "priority": 2,
                "timeout": 180,
                "parameters": {
                    "positions": [0, 90, 180, 270, 0]
                }
            },
            {
                "name": "相机拍照测试",
                "description": "测试相机拍照功能",
                "test_type": "functional",
                "priority": 2,
                "timeout": 120,
                "parameters": {
                    "cameras": ["/dev/video0", "/dev/video2"],
                    "resolution": "1080p"
                }
            },
            {
                "name": "LED控制测试",
                "description": "测试LED灯的控制功能",
                "test_type": "functional",
                "priority": 3,
                "timeout": 60,
                "parameters": {
                    "colors": ["red", "green", "blue", "white"]
                }
            }
        ]
    },
    
    "performance_test": {
        "name": "性能测试",
        "description": "测试系统的性能表现",
        "test_cases": [
            {
                "name": "响应时间测试",
                "description": "测量系统响应时间",
                "test_type": "performance",
                "priority": 1,
                "timeout": 300,
                "parameters": {
                    "request_count": 100,
                    "concurrent": 5
                }
            },
            {
                "name": "连续运行稳定性测试",
                "description": "长时间连续运行测试",
                "test_type": "stability",
                "priority": 2,
                "timeout": 3600,
                "parameters": {
                    "duration_hours": 1
                }
            }
        ]
    }
}
