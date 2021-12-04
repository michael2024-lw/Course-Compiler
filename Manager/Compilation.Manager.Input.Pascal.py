import MicroServerAPI
import random
import string

serv = MicroServerAPI.MicroService(url_get='http://localhost:8080/5-semestr/compiler/get-job',
                                   url_post='http://localhost:8080/5-semestr/compiler/post-job',
                                   persistentMode=True)

def ProcessResult(procres, procname, successneeded):
    result = { "success":False, "lines":[] }
    
    if "success" in procres:
        if procres["success"]:
            if all(entry in procres for entry in successneeded):
                return {"success":True}
            else:
                result["lines"] = ['Сервис "' + procname + '" неисправен!', 'Его ответ не содержит результата работы. Ожидалось следующее:'] + successneeded
        else:
            first = None
            if "errorDesc" in procres:
                first = ": " + procname + ": " + procres["errorDesc"]
            else:
                first = ": " + procname + ": Описание ошибки отсутствует."
            if "errorLine" in procres:
                if "errorColumn" in procres:
                    first = "; символ: " + procres["errorColumn"] + first
                    first = "Строка " + procres["errorLine"] + first
                    offset = ""
                    for i in range(0, procres["errorColumn"]):
                        offset += "~"
                    offset += "^"
                    result["lines"] = [first, codePascal[int(procres["errorLine"])], offset]
                else:
                    result["lines"] = [first, codePascal[int(procres["errorLine"])]]
    else:
        result["lines"] = ['Сервис "' + procname + '" неисправен!','Его ответ не содержит признака успешности выполнения.']

    return result

while True:
    codePascal,addr = serv.GetNextJob(job_type='Compilation.Manager.Input.Pascal')
    #Begin of data processing area

    session = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k = 16))
    
    serv.ProcessAsFunction(content={"session":session,"bank":None,"operation":"post","data":"Manager's Mandat: Create Session"},
                           requested_function='Compilation.Storage.Request')

    serv.ProcessAsFunction(content={"session":session,"bank":"source_raw","operation":"post","data":codePascal},
                           requested_function='Compilation.Storage.Request')
    
    listOfTokens = serv.ProcessAsFunction(content={"session":session,"source":codePascal},
                           requested_function='Compilation.Lexer')


    result = ProcessResult(listOfTokens, "лексер", ['tokens'])
    if result["success"]:
        abstractSyntaxTree = serv.ProcessAsFunction(content={"session":session,"tokens":listOfTokens["tokens"]},
                                   requested_function='Compilation.Parser')

        result = ProcessResult(listOfTokens, "парсер", ['variables', 'syntaxTree'])
        if result["success"]:
            codeAsm = serv.ProcessAsFunction(content={"session":session,"variables":abstractSyntaxTree["variables"],"syntaxTree":abstractSyntaxTree["syntaxTree"]},
                                   requested_function='Compilation.CodeGenerator')

            result = ProcessResult(listOfTokens, "генератор кода", ['asm'])
            if result["success"]:
                result["lines"] = codeAsm["asm"]



    serv.ProcessAsFunction(content={"session":session,"bank":None,"operation":"post","data":"Manager's Mandat: Remove Session"},
                           requested_function='Compilation.Storage.Request')
    
    #End of data processing area
    serv.PostFinalResult(content=result,
                         result_type='Compilation.Manager.Output',
                         responseAddress=addr)
