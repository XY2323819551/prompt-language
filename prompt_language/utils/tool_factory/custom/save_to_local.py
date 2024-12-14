import json
import os
import aiofiles

async def save_to_local(data: dict = None, file_path: str = "", format: str = 'json'):
    """
    将数据保存到本地文件
    
    Args:
        data: 要保存的数据
        file_path: 保存路径
        format: 文件格式，目前支持json
    
    Returns:
        bool: 保存成功返回True
    
    Raises:
        Exception: 当文件格式不支持或保存失败时
    """
    if not data or not file_path:
        raise Exception("无效的输入参数")
        
    if format not in ['json']:
        raise Exception("不支持的文件格式")
        
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if format == 'json':
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
                await f.write(json_str)
                
        return True
        
    except Exception as e:
        raise Exception(f"保存文件失败: {str(e)}")