from llvmlite import ir
from llvmlite import binding as llvm
from anytree import PreOrderIter
import tppsema


class LlvmGenCode:

    
    def __init__(self):
        self.module = None
        self.target = None
        self.target_machine = None
        self.functions = list()
        self.vars = list()
        self.visited_nodes = list()

    
    def start(self):
        llvm.initialize()
        llvm.initialize_all_targets()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        self.module = ir.Module('meu_modulo.bc')
        self.module.triple = llvm.get_process_triple()
        self.target = llvm.Target.from_triple(self.module.triple)
        self.target_machine = self.target.create_target_machine()
        self.module.data_layout = self.target_machine.target_data

        self.escreva_inteiro = ir.Function(self.module, ir.FunctionType(ir.VoidType(), [ir.IntType(32)]), name="escreva_inteiro")
        self.escreva_flutuante = ir.Function(self.module, ir.FunctionType(ir.VoidType(), [ir.FloatType()]), name="escreva_flutuante")
        self.leia_inteiro = ir.Function(self.module, ir.FunctionType(ir.IntType(32), []), name="leia_inteiro")
        self.leia_flutuante = ir.Function(self.module, ir.FunctionType(ir.FloatType(), []), name="leia_flutuante")

    
    def save_module(self):
        arquivo = open('meu_modulo.ll', 'w')
        arquivo.write(str(self.module))
        arquivo.close()
        print(self.module)

    
    def get_array_var(self, node, builder):
        # get_array_var(node.children[0], builder)
        ptr_arr = None
        arr = None
        arr_name = node.children[0].name
        index = node.children[1].children[0]
        Zero32 = ir.Constant(ir.IntType(32), 0)

        for i in self.vars:
            if i[0] == arr_name:
                arr = i[1]

        if len(index.children) > 1:
            var1 = index.children[0].name
            exp = index.children[1].name
            var2 = index.children[2].name

            temp_index = self.do_expression(exp, var1, var2, builder)

            ptr_arr = builder.gep(arr, [Zero32, temp_index], name=f'ptr_{arr_name}_{index.name}')
            
        else:
            arr_index = self.check_var(index.name, builder)

            ptr_arr = builder.gep(arr, [Zero32, arr_index], name=f'ptr_{arr_name}_{index.name}')
            

        return ptr_arr



    def decl_array_var(self, node, var_type, is_global=False, builder=None):
        var_name = node.children[0].name

        if is_global:
            if var_type == 'inteiro':
                arr_size = node.children[1].children[0].name
                type_arr = ir.ArrayType(ir.IntType(32), int(arr_size))
                var = ir.GlobalVariable(self.module, type_arr, var_name)
            elif var_type == 'flutuante':
                arr_size = node.children[1].children[0].name
                type_arr = ir.ArrayType(ir.FloatType(), int(arr_size))
                var = ir.GlobalVariable(self.module, type_arr, var_name)

            var.initializer = ir.Constant(type_arr, None)
            var.align = 4

        else:

            if var_type == 'inteiro':
                arr_size = node.children[1].children[0].name
                type_arr = ir.ArrayType(ir.IntType(32), int(arr_size))
                var = builder.alloca(type_arr, var_name)
            elif var_type == 'flutuante':
                arr_size = node.children[1].children[0].name
                type_arr = ir.ArrayType(ir.FloatType(), int(arr_size))
                var = builder.alloca(type_arr, var_name)
            
            var.align = 4


        self.vars.append([var_name, var])


    def decl_global_var(self, node):

        if len(node.children[2].children) > 1:
            if node.children[2].name == 'var':
                var_tipo = node.children[0].name
                
                if len(node.children[2].children[1].children) == 1:
                    self.decl_array_var(node.children[2], var_tipo, is_global=True)
                else:
                    #declarar matriz
                    pass
                
            else:
                for i in node.children[2].children:
                    if i.name == 'var':
                        var_tipo = node.children[0].name
                        self.decl_array_var(i, var_tipo, is_global=True)
                        
                    else:
                        var_tipo = node.children[0].name
                        var_name = i.name
                        var = None

                        if var_tipo == 'inteiro':
                            var = ir.GlobalVariable(self.module, ir.IntType(32), var_name)
                        elif var_tipo == 'flutuante':
                            var = ir.GlobalVariable(self.module, ir.FloatType(), var_name)

                        self.vars.append([var_name, var])

        else:
            var_tipo = node.children[0].name
            var_name = node.children[2].name
            var = None

            if var_tipo == 'inteiro':
                var = ir.GlobalVariable(self.module, ir.IntType(32), var_name)
            elif var_tipo == 'flutuante':
                var = ir.GlobalVariable(self.module, ir.FloatType(), var_name)

            self.vars.append([var_name, var])

    
    def decl_func_var(self, node, entry_block, exit_block, builder):

        if len(node.children[2].children) > 1:
            if node.children[2].name == 'var':
                var_tipo = node.children[0].name
                
                if len(node.children[2].children[1].children) == 1:
                    self.decl_array_var(node.children[2], var_tipo, builder=builder)
                else:
                    #declarar matriz
                    pass
                
            else:
                for i in node.children[2].children:
                    if i.name == 'var':
                        var_tipo = node.children[0].name
                        self.decl_array_var(i, var_tipo, builder=builder)
                        
                    else:
                        var_tipo = node.children[0].name
                        var_name = i.name
                        var = None

                        if var_tipo == 'inteiro':
                            var = builder.alloca(ir.IntType(32), name=var_name)
                            var.align = 4
                        elif var_tipo == 'flutuante':
                            var = builder.alloca(ir.FloatType(), name=var_name)
                            var.align = 4

                        # self.vars.append([var_name, var])

        else:
            var_tipo = node.children[0].name
            var_name = node.children[2].name
            var = None

            if var_tipo == 'inteiro':
                var = builder.alloca(ir.IntType(32), name=var_name)
                var.align = 4
            elif var_tipo == 'flutuante':
                var = builder.alloca(ir.FloatType(), name=var_name)
                var.align = 4

            # self.vars.append([var_name, var])

        self.vars.append([var_name, var])
        self.visited_nodes.append(node)

    
    def attr_global_var(self, node):

        var_name = node.children[0].name
        var_value = node.children[2].name

        for i in self.vars:
            if i[0] == var_name:
                if var_value.isnumeric():
                    i[1].initializer = ir.Constant(ir.IntType(32), int(var_value))
                elif var_value.replace('.', '', 1).isdigit() and var_value.count('.') < 2:
                    i[1].initializer = ir.Constant(ir.FloatType(), float(var_value))
                else:
                    pass

                i[1].linkage = "dso_local"
                i[1].align = 4

    
    def check_var(self, var_name, builder, name=''):

        var_temp = None

        if var_name.isnumeric():
            var_temp = ir.Constant(ir.IntType(32), int(var_name))
        elif var_name.replace('.', '', 1).isdigit() and var_name.count('.') < 2:
            var_temp = ir.Constant(ir.FloatType(), float(var_name))
        else:
            for j in self.vars:
                if j[0] == var_name:
                    var_temp = builder.load(j[1], name, align=4)

        return var_temp


    def call_function(self, node, builder):
        func = None
        func_name = node.children[0].name

        args = [i for i in node.children[1].children]
        loaded_args = list()

        for i in self.functions:
            if i[0] == func_name:
                func = i[1]
        
        for i in args:
            if i.name == 'chamada_funcao':
                loaded_args.append(self.call_function(i, builder))
            else:
                loaded_args.append(self.check_var(i.name, builder))

        call = builder.call(func, loaded_args)

        return call

    
    def do_expression(self, exp, var1, var2, builder):
        var1_temp = self.check_var(var1, builder)
        var2_temp = self.check_var(var2, builder)

        temp = None

        match exp:
            case '+':
                temp = builder.add(var1_temp, var2_temp, name='temp')
            
            case '-':
                temp = builder.sub(var1_temp, var2_temp, name='temp')

            case '*':
                temp = builder.mul(var1_temp, var2_temp, name='temp')

            case '/':
                temp = builder.sdiv(var1_temp, var2_temp, name='temp')
        
        return temp


    def attr_var(self, node, builder):

        if len(node.children[2].children) > 1:
            if node.children[2].name == 'chamada_funcao':
                # Criar lista para conferir chamadas de funcoes e limpar no fim
                var = node.children[0]
                func_name = node.children[2].children[0].name
                func = None

                args = [i for i in node.children[2].children[1].children]
                loaded_args = list()

                for i in self.functions:
                    if i[0] == func_name:
                        func = i[1]

                for i in args:
                    if i.name == 'chamada_funcao':
                        loaded_args.append(self.call_function(i, builder))
                    else:
                        loaded_args.append(self.check_var(i.name, builder))

                # for i in self.vars:
                #     if i[0] in args:
                #         loaded_args.append(builder.load(i[1]))

                call = builder.call(func, loaded_args)

                if var.name == 'var': # Array
                    pass
                else:
                    for i in self.vars:
                        if i[0] == var.name:
                            builder.store(call, i[1], align=4)



            
            elif node.children[2].name == 'var':
                ptr_arr_2 = self.get_array_var(node.children[2], builder)
                elem_2 = builder.load(ptr_arr_2, align=4)

                # Aqui pode ser uma chamada de funcao ou var || Ou nao
                temp_value = self.check_var(node.children[2].name, builder)
                
                if node.children[0].name == 'var': # A[0] = A[1]
                    ptr_arr_1 = self.get_array_var(node.children[0], builder)
                    builder.store(elem_2, ptr_arr_1, align=4)
                
                else: # a = A[1]
                    var = self.check_var(node.children[0].name, builder)
                    builder.store(elem_2, var, align=4)

            else:
                var_name = node.children[0].name
                var1 = node.children[2].children[0].name
                exp = node.children[2].children[1].name
                var2 = node.children[2].children[2].name

                temp = self.do_expression(exp, var1, var2, builder)

                for i in self.vars:
                    if i[0] == var_name:
                        builder.store(temp, i[1], align=4)

        else:
            if node.children[0].name == 'var':
                # A[1024] = var

                ptr_arr = self.get_array_var(node.children[0], builder)

                # Aqui pode ser uma chamada de funcao ou var || Ou nao
                temp_value = self.check_var(node.children[2].name, builder)

                builder.store(temp_value, ptr_arr)

            else:
                var_name = node.children[0].name
                var_value = node.children[2].name

                for i in self.vars:
                    if i[0] == var_name:
                        if var_value.isnumeric():
                            builder.store(ir.Constant(ir.IntType(32), int(var_value)), i[1], align=4)
                        elif var_value.replace('.', '', 1).isdigit() and var_value.count('.') < 2:
                            builder.store(ir.Constant(ir.FloatType(), float(var_value)), i[1], align=4)
                        else:
                            for j in self.vars:
                                if j[0] == var_value:
                                    builder.store(builder.load(j[1]), i[1], align=4)

        self.visited_nodes.append(node)

    
    def simp_cond(self, node, function, builder):

        corpo = node.children[-2]

        if_block = function.append_basic_block(name='if')
        builder.branch(if_block)
        builder.position_at_end(if_block)

        if node.children[1].name == 'fator':
            exp = node.children[1].children[0].children
        else:
            exp = node.children[1].children

        cmp_type = exp[1].name
        
        if cmp_type == '<>':
            cmp_type = '!='

        cmp_name = f"{exp[0].name} {exp[1].name} {exp[2].name}"

        var1_cmp = self.check_var(exp[0].name, builder, 'var1_cmp')
        var2_cmp = self.check_var(exp[2].name, builder, 'var2_cmp')

        cmp_ref = builder.icmp_signed(cmp_type, var1_cmp, var2_cmp, cmp_name)

        with builder.if_then(cmp_ref):
            for no in PreOrderIter(corpo):
                match no.name:
                    case 'atribuicao':
                        if no not in self.visited_nodes:
                            self.attr_var(no, builder)
                
                    case 'se':
                        if no not in self.visited_nodes:
                            if len(no.children) == 5:
                                self.simp_cond(no, function, builder)
                            elif len(no.children) == 7:
                                self.comp_cond(no, function, builder)

        self.visited_nodes.append(node)

    
    def comp_cond(self, node, function, builder):
        corpo1 = node.children[-4]
        corpo2 = node.children[-2]

        if_block = function.append_basic_block(name='if')
        builder.branch(if_block)
        builder.position_at_end(if_block)

        if node.children[1].name == 'fator':
            exp = node.children[1].children[0].children
        else:
            exp = node.children[1].children

        cmp_type = exp[1].name
        
        if cmp_type == '<>':
            cmp_type = '!='

        cmp_name = f"{exp[0].name} {exp[1].name} {exp[2].name}"

        var1_cmp = self.check_var(exp[0].name, builder, 'var1_cmp')
        var2_cmp = self.check_var(exp[2].name, builder, 'var2_cmp')

        cmp_ref = builder.icmp_signed(cmp_type, var1_cmp, var2_cmp, cmp_name)

        with builder.if_else(cmp_ref) as (then, otherwise):

            with then:
                for no in PreOrderIter(corpo1):
                    match no.name:
                        case 'atribuicao':
                            if no not in self.visited_nodes:
                                self.attr_var(no, builder)
                        
                        case 'se':
                            if no not in self.visited_nodes:
                                if len(no.children) == 5:
                                    self.simp_cond(no, function, builder)
                                elif len(no.children) == 7:
                                    self.comp_cond(no, function, builder)

            with otherwise:
                for no in PreOrderIter(corpo2):
                    match no.name:
                        case 'atribuicao':
                            if no not in self.visited_nodes:
                                self.attr_var(no, builder)
                        
                        case 'se':
                            if no not in self.visited_nodes:
                                if len(no.children) == 5:
                                    self.simp_cond(no, function, builder)
                                elif len(no.children) == 7:
                                    self.comp_cond(no, function, builder)

        self.visited_nodes.append(node)

    
    def repeat(self, node, function, builder):
        loop = builder.append_basic_block('loop')
        loop_val = builder.append_basic_block('loop_val')
        loop_end = builder.append_basic_block('loop_end')

        builder.branch(loop)
        builder.position_at_end(loop)

        corpo = node.children[1]

        for no in PreOrderIter(corpo):
            match no.name:
                case 'leia':
                    if no not in self.visited_nodes:
                        self.read_function(no, builder)

                case 'escreva':
                    if no not in self.visited_nodes:
                        self.write_function(no, builder)

                case 'atribuicao':
                    if no not in self.visited_nodes:
                        self.attr_var(no, builder)

                case 'se':
                    if no not in self.visited_nodes:
                        if len(no.children) == 5:
                            self.simp_cond(no, function, builder)
                        elif len(no.children) == 7:
                            self.comp_cond(no, function, builder)

        exp = node.children[-1].children

        cmp_type = exp[1].name
        if cmp_type == '=':
            cmp_type = '=='
            cmp_name = f"{exp[0].name} {cmp_type} {exp[2].name}"
        else:
            cmp_name = f"{exp[0].name} {exp[1].name} {exp[2].name}"

        var1_cmp = self.check_var(exp[0].name, builder, 'var1_cmp')
        var2_cmp = self.check_var(exp[2].name, builder, 'var2_cmp')

        builder.branch(loop_val)
        builder.position_at_end(loop_val)

        cmp_ref = builder.icmp_signed(cmp_type, var1_cmp, var2_cmp, cmp_name)

        builder.cbranch(cmp_ref, loop, loop_end)

        builder.position_at_end(loop_end)


    def read_function(self, node, builder):
        var = node.children[0]

        if var.name == 'var':
            ptr_arr = self.get_array_var(var, builder)

            if str(ptr_arr.type) in ['i32*', 'i32']:
                resultado_leia = builder.call(self.leia_inteiro, args=[])

            elif str(ptr_arr.type) in ['float*', 'float']:
                resultado_leia = builder.call(self.leia_flutuante, args=[])

            builder.store(resultado_leia, ptr_arr, align=4)

        else:
            for i in self.vars:
                if i[0] == var.name:
                    var_loaded = i[1]

            if str(var_loaded.type) in ['i32*', 'i32']:
                resultado_leia = builder.call(self.leia_inteiro, args=[])

            elif str(var_loaded.type) in ['float*', 'float']:
                resultado_leia = builder.call(self.leia_flutuante, args=[])

            builder.store(resultado_leia, var_loaded, align=4)

            self.visited_nodes.append(node)
        

    def write_function(self, node, builder):
        var = node.children[0]

        if var.name == 'var': # Is an array
            ptr_arr = self.get_array_var(var, builder)

            if str(ptr_arr.type) in ['i32*', 'i32']:
                builder.call(self.escreva_inteiro, args=[builder.load(ptr_arr)])

            elif str(ptr_arr.type) in ['float*', 'float']:
                builder.call(self.escreva_flutuante, args=[builder.load(ptr_arr)])
        
        else:
            for i in self.vars:
                if i[0] == var.name:
                    var_loaded = i[1]

            if str(var_loaded.type) in ['i32*', 'i32']:
                builder.call(self.escreva_inteiro, args=[builder.load(var_loaded)])

            elif str(var_loaded.type) in ['float*', 'float']:
                builder.call(self.escreva_flutuante, args=[builder.load(var_loaded)])

            self.visited_nodes.append(node)
        

    def get_params(self, node):
        p_types = list()
        p_vars = list()

        for no in PreOrderIter(node):
            match no.name:
                case 'parametro':
                    if no.children[0].name == 'inteiro':
                        p_types.append(ir.IntType(32))
                    elif no.children[0].name == 'flutuante':
                        p_types.append(ir.FloatType())

                    p_vars.append(no.children[2].name)
                    
        return p_types, p_vars


    def decl_function(self, node):
        func = None
        func_type = None
        params_types = list()
        params_vars = list()

        cabecalho = node.children[1]

        if len(cabecalho.children) == 4:
            params_types, params_vars = self.get_params(cabecalho.children[1])

        # Funcao possui um tipo
        if len(node.children) == 2:
            func_tipo = node.children[0].name
            func_nome = node.children[1].children[0].name

            if func_nome == 'principal':
                func_nome = 'main'

            if func_tipo == 'inteiro':
                func_type = ir.FunctionType(ir.IntType(32), params_types)
            elif func_tipo == 'flutuante':
                func_type = ir.FunctionType(ir.FloatType(), params_types)

            func = ir.Function(self.module, func_type, func_nome)
            
            if len(params_vars) != 0:
                for i in range(len(params_vars)):
                    func.args[i].name = params_vars[i]

        self.functions.append([func_nome, func])

        entry_block = func.append_basic_block("entry")
        exit_block = func.append_basic_block("exit")
        builder = ir.IRBuilder(entry_block)

        corpo = node.children[1].children[-2]

        # Criacao de blocos de entrada e saida
        for no in PreOrderIter(corpo):
            
            match no.name:
                case 'declaracao_variaveis':
                    if no not in self.visited_nodes:
                        self.decl_func_var(no, entry_block, exit_block, builder)

                case 'atribuicao':
                    if no not in self.visited_nodes:
                        self.attr_var(no, builder)

                case 'se':
                    if no not in self.visited_nodes:
                        if len(no.children) == 5:
                            self.simp_cond(no, func, builder)
                        elif len(no.children) == 7:
                            self.comp_cond(no, func, builder)

                case 'repita':
                    if no not in self.visited_nodes:
                        if len(no.children) > 1:
                            self.repeat(no, func, builder)

                case 'leia':
                    if no not in self.visited_nodes:
                        self.read_function(no, builder)

                case 'escreva':
                    if no not in self.visited_nodes:
                        self.write_function(no, builder)
                        

                case 'retorna':
                    if len(no.children) == 1:
                        if len(no.children[0].children) == 3:
                            # var1 = no.children[0].children[0]
                            exp = no.children[0].children[1]
                            # var2 = no.children[0].children[2]

                            match exp.name:
                                case '+':
                                    res = builder.add(func.args[0], func.args[1])
                                
                                case '-':
                                    res = builder.sub(func.args[0], func.args[1])

                                case '*':
                                    res = builder.mul(func.args[0], func.args[1])

                                case '/':
                                    res = builder.sdiv(func.args[0], func.args[1])

                            # res = builder.add(func.args[0], func.args[1])

                            # Cria salto para bloco de saida
                            builder.branch(exit_block)

                            # Adiciona bloco de saida
                            builder.position_at_end(exit_block)

                            # Cria o return
                            builder.ret(res)


                        elif no.children[0].name == '0':
                            # Declara e aloca var 'retorno', com o tipo inteiro
                            retorno = builder.alloca(ir.IntType(32), name='retorno')

                            # Define alinhamento
                            retorno.align = 4

                            # Define constante 0
                            zero32 = ir.Constant(ir.IntType(32), 0)

                            # Armazena 0 na var retorno
                            builder.store(zero32, retorno, align=4)

                            # Cria salto para bloco de saida
                            builder.branch(exit_block)

                            # Adiciona bloco de saida
                            builder.position_at_end(exit_block)

                            # Cria o return
                            return_val_temp = builder.load(retorno, name='ret_temp', align=4)
                            builder.ret(return_val_temp)

                        else:

                            if no.children[0].name.isnumeric():

                                # Declara e aloca var 'retorno', com o tipo inteiro
                                retorno = builder.alloca(ir.IntType(32), name='retorno')
                                retorno.align = 4
                                ret = ir.Constant(ir.IntType(32), int(no.children[0].name))
                                builder.store(ret, retorno, align=4)

                                # Cria salto para bloco de saida
                                builder.branch(exit_block)

                                # Adiciona bloco de saida
                                builder.position_at_end(exit_block)

                                # Cria o return
                                return_val_temp = builder.load(retorno, name='ret_temp', align=4)
                                builder.ret(return_val_temp)

                            elif no.children[0].name.replace('.', '', 1).isdigit() and no.children[0].name.count(
                                    '.') < 2:

                                # Declara e aloca var 'retorno', com o tipo inteiro
                                retorno = builder.alloca(ir.FloatType(), name='retorno')
                                retorno.align = 4
                                ret = ir.Constant(ir.FloatType(), float(no.children[0].name))
                                builder.store(ret, retorno, align=4)

                                # Cria salto para bloco de saida
                                builder.branch(exit_block)

                                # Adiciona bloco de saida
                                builder.position_at_end(exit_block)

                                # Cria o return
                                return_val_temp = builder.load(retorno, name='ret_temp', align=4)
                                builder.ret(return_val_temp)

                            else:
                                for j in self.vars:
                                    if j[0] == no.children[0].name:
                                        # Cria salto para bloco de saida
                                        builder.branch(exit_block)

                                        # Adiciona bloco de saida
                                        builder.position_at_end(exit_block)

                                        # Cria o return
                                        builder.ret(builder.load(j[1], ""))


    def generate(self, tree):

        for no in PreOrderIter(tree):
            
            match no.name:
                case 'declaracao_variaveis':
                    escopo = tppsema.get_function(no)
                    if escopo == 'global':
                        self.decl_global_var(no)

                case 'atribuicao':
                    escopo = tppsema.get_function(no)
                    if escopo == 'global':
                        self.attr_global_var(no)

                    # if no.children[2].name not in self.var_names:
                    #     self.decl_global_var(no)

                case 'declaracao_funcao':
                    self.decl_function(no)

            # print(self.vars)
            # if i.name == 'var':
            #     var_name = return_leaf(i).name
            #     if var_name not in all_vars:
            #         all_vars.append(var_name)

        # return all_vars
