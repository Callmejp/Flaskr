import os
import time
import subprocess
import sys

basedir = os.path.abspath(os.path.dirname(__file__))
EXEC = sys.executable


def get_version():
    v = sys.version_info
    version = "python %s.%s" % (v.major, v.minor)
    return version


def decode(s):
    try:
        return s.decode('utf-8')
    except UnicodeDecodeError:
        return s.decode('gbk')


def runcode(code):
    print(code)
    print(basedir)
    filename = int(time.time())
    filename = str(basedir) + '\\' + str(filename) + '.py'
    r = dict()
    r["version"] = get_version()

    with open(filename, 'w') as f:
        f.write(code)


    try:
        # subprocess.check_output 是 父进程等待子进程完成，返回子进程向标准输出的输出结果
        # stderr是标准输出的类型
        outdata = decode(subprocess.check_output([EXEC, filename], stderr=subprocess.STDOUT, timeout=5))
        # 成功返回的数据
        r['output'] = outdata
        r["code"] = "Success"
    except subprocess.CalledProcessError as e:
        # e.output是错误信息标准输出
        # 错误返回的数据
        r["code"] = 'Error'
        r["output"] = decode(e.output)
    finally:
        # 删除文件(其实不用删除临时文件会自动删除)
        print(r)
        try:
            os.remove(filename)
        except Exception as e:
            print(e)
        finally:
            return r

