from flask import Flask, request, redirect, send_file
import mappingGenerator
import os
app = Flask(__name__)
@app.route('/generateMapping', methods=["POST"])
def generateMapping():
    
    uploaded_file = request.files['files']
    resultName = request.form['args']
    filepath = "./uploads/" + uploaded_file.filename
    uploaded_file.save(filepath)
    mappingGenerator.generateMapping(filepath, resultName)
    return send_file(f"./results/{resultName}.js")



@app.route('/getTarget', methods=["POST"])
def getTarget():

    sourceFile = request.files['files']
    resultName = request.form['args']
    filepath = "./uploads/" + sourceFile.filename
    sourceFile.save(filepath)
    os.system(f"node ./results/{resultName}.js")
    print('here')
    return send_file(f"results/{resultName}.json")


if __name__ == "__main__":
    app.run()
