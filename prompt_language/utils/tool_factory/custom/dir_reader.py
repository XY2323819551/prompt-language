import os


async def dir_reader(dirs=[], params_format=False):
    if params_format:
        return ['code', 'code_params']
    try:
        results = []
        for dir in dirs:
            for file in os.listdir(dir):
                with open(os.path.join(dir, file), 'r', encoding='utf-8') as f:
                    results.append(f.read())
        return results
    except:
        raise Exception("文件夹内容读取出错！")
    
"""
"dir_reader":{
    "object":dir_reader,
    "describe":"读取一个文件夹下的全部文件的内容，需要参数{'dirs':待读取的文件夹路径，格式为[dir1, dir22, ...]}",
}
"""