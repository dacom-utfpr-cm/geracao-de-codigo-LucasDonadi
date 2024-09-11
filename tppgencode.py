import sys
import os
import logging
import ply.yacc as yacc
import tppsema
from sys import argv, exit
from tpplex import tokens
from mytree import MyNode
from anytree.exporter import DotExporter, UniqueDotExporter
from anytree import RenderTree, AsciiStyle
from myerror import MyError

from llvmlite import ir
from llvmlite import binding as llvm
from llvm_gen_code import LlvmGenCode

logging.basicConfig(
    level=logging.DEBUG,
    filename="gencode.log",
    filemode="w",
    format="%(filename)10s:%(lineno)4d:%(message)s"
)

log = logging.getLogger()

error_handler = MyError('GenCodeErrors')

# Programa Principal.
if __name__ == "__main__":
    tree = tppsema.main()

    if len(sys.argv) < 2:
        raise TypeError(error_handler.newError('ERR-SEM-USE'))

    aux = argv[1].split('.')
    if aux[-1] != 'tpp':
        raise IOError(error_handler.newError('ERR-SEM-NOT-TPP'))
    elif not os.path.exists(argv[1]):
        raise IOError(error_handler.newError('ERR-SEM-FILE-NOT-EXISTS'))
    else:
        UniqueDotExporter(tree).to_picture(argv[1] + ".unique.ast.png")

        code = LlvmGenCode()
        code.start()
        code.generate(tree)
        code.save_module()

        # data = open(argv[1])
        # source_file = data.read()
