from camel.toolkits.base import BaseToolkit
from camel.toolkits.function_tool import FunctionTool

import yaml
from datetime import datetime
from typing import List
import os

class YamlWriterToolkit(BaseToolkit):
    def save_to_yaml(data: str, directory: str = ".") -> str:
        """
        将制定好的交易策略写入以当前日期命名的 YAML 文件中。

        参数:
            data (str): 制定好的交易策略（纯文本格式）
            directory (str): 保存文件的目录，默认为当前目录

        返回:
            str: 保存的 YAML 文件路径
        """
        os.makedirs(directory, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = os.path.join(directory, f"{date_str}.yml")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(data)

        return filename

    def get_tools(self) -> List[FunctionTool]:
        r"""Returns a list of FunctionTool objects representing the
        functions in the toolkit.

        Returns:
            List[FunctionTool]: A list of FunctionTool objects
                representing the functions in the toolkit.
        """
        return [
            FunctionTool(self.save_to_yaml),
        ]