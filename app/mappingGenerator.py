from flask import Flask, request, jsonify
import csv
import time

def transformArrayIf(condition, then, elseStatement, queries, target):
    arrayVar, condition = condition.split('item')
    arrayVar = "source" + arrayVar
    found = False
    for i in queries:
        if target in i:
            found=True
    target = f"res.{target}"
    if not found:
        queries.append(f"{target}= [];\n")
    query = arrayVar + f"forEach(item => {{(item{condition})?{target}.{then}:{target}.{elseStatement}}});\n"
    queries.append(query)
    
    return queries

def transformIf(source, queries, target):
    conditionStart = source.find('IF(') + 3
    conditionEnd = source.find(') THEN')
    condition = source[conditionStart: conditionEnd].strip()

    thenStart = conditionEnd + 6
    thenEnd = source.find('ELSE')
    then = source[thenStart:thenEnd].strip()
    elseStart = -1 if thenEnd == -1 else thenEnd + 4
    elseStatement = source[elseStart: ].strip()

    if ("item" in condition):
        queries = transformArrayIf(condition, then, elseStatement, queries, target)
        return queries




def generateMapping(file, resultName):
    file = open(file)
    
    
    data = {}
    for line in csv.reader(file):
        enum = ""
        if len(line) > 4:
            for i in line[3:-1]:
                enum += i.strip()[:-1] + ",\""
            enum += line[-1]
        data[line[0]] = {'target': line[1].strip(
        ), 'source': line[2].strip(), 'enumeration': enum}
    del data['No.']


    res = open(f"./results/{resultName}.js", 'w')
    res.write(
        'source=require("../uploads/source.json");\ndata={"source": source};\nres={}\n')

    queries = []
    for i in data:
        target = data[i]['target']
        if "IF" in data[i]['source']:
            queries = transformIf(data[i]['source'],queries, target)
            continue
        source = data[i]['source'].split("+")
        
        if data[i]["enumeration"]:
            enum = data[i]["enumeration"]
            res.write(f"{target} = {enum};\n")
            if len(source) > 1:
                queries.append(f"res.{target} = ")
                for i in source[:-1]:
                    i = i.strip()
                    if "ENUM" in i:
                        start = i.find(".")
                        end = i.find(")")
                        enumSource = i[start: end]
                        queries[-1] += f"{target}[source{enumSource.strip()}]+' '+"
                    elif len(i) == 3:
                        queries[-1] = queries[-1][:-4]
                        queries[-1] += f"{i}+"
                    else:
                        queries[-1] += f"source{i}+' '+"

                source[-1] = source[-1].strip()
                if "ENUM" in source[-1]:
                        start = source[-1][0].find(".")
                        enumSource = source[-1][start: -1]
                        queries[-1] += f"{target}[source{enumSource.strip()}];\n"
                else:
                        queries[-1] += f"source{source[-1]};\n"
            else:
                start = source[0].find(".")
                source = source[0][start: -1]
                queries.append(
                    f"res.{target} = {target}[source{source}];\n")
        elif len(source) > 1:
            queries.append(f"res.{target} = ")
            for i in source[:-1]:
                if len(i) == 3:
                    queries[-1] = queries[-1][:-4]
                    queries[-1] += f"{i}+"
                else:
                    queries[-1] += f"source{i.strip()}+' '+"
            if len(source[-1]) == 1:
                queries[-1] += f"{source[-1]};\n"
            else:
                queries[-1] += f"source{source[-1].strip()};\n"
        else:
            queries.append(
                f"res.{target} = source{source[0]};\n")


    res.writelines(queries)

    res.write("console.log(res);\n")
    res.write(f"var fs = require('fs');\njsonData = JSON.stringify(res);\nfs.writeFile(\"./results/{resultName}.json\", jsonData, function (err) {{\n\tif(err){{\n\t\tconsole.log(err);\n\t}}\n}});")
    return 1


