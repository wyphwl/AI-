from langchain.tools import BaseTool

class TextLengthTool(BaseTool):
    name: str = "文本字数计算工具"
    description: str = "当你被要求计算文本字数或者生成指定字数文本时，使用此工具"

    def _run(self, text):
        return len(text)
