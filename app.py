from flask import Flask, render_template, url_for, request, redirect
import re
from sympy import Matrix, lcm




app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tabela')
def tabela():
    return render_template('tabela.html')

def balanciamento(reactants, products):
    elementList=[]
    elementMatrix=[]
    reactants=reactants.replace(' ', '').split("+")
    products=products.replace(' ', '').split("+")
    def addToMatrix(element, index, count, side):
        if(index == len(elementMatrix)):
            elementMatrix.append([])
            for x in elementList:
                elementMatrix[index].append(0)
        if(element not in elementList):
            elementList.append(element)
            for i in range(len(elementMatrix)):
                elementMatrix[i].append(0)
        column=elementList.index(element)
        elementMatrix[index][column]+=count*side

    def findElements(segment,index, multiplier, side):
        elementsAndNumbers=re.split('([A-Z][a-z]?)',segment)
        i=0
        while(i<len(elementsAndNumbers)-1):#Ultimo elemento sempre vazio
            i+=1
            if(len(elementsAndNumbers[i])>0):
                if(elementsAndNumbers[i+1].isdigit()):
                    count=int(elementsAndNumbers[i+1])*multiplier
                    addToMatrix(elementsAndNumbers[i], index, count, side)
                    i+=1
                else:
                    addToMatrix(elementsAndNumbers[i], index, multiplier, side)

    def compoundDecipher(compound, index, side):
        segments=re.split('(\([A-Za-z0-9]*\)[0-9]*)',compound)    
        for segment in segments:
            if segment.startswith("("):
                segment=re.split('\)([0-9]*)',segment)
                multiplier=int(segment[1])
                segment=segment[0][1:]
            else:
                multiplier=1
            findElements(segment, index, multiplier, side)

    for i in range(len(reactants)):
        compoundDecipher(reactants[i],i,1)
    for i in range(len(products)):
        compoundDecipher(products[i],i+len(reactants),-1)
    try:
        elementMatrix = Matrix(elementMatrix)
        elementMatrix = elementMatrix.transpose()
        solution=elementMatrix.nullspace()[0]
        multiple = lcm([val.q for val in solution])
        solution = multiple*solution
        coEffi=solution.tolist()
        output=""
        for i in range(len(reactants)):
            output+=str(coEffi[i][0])+reactants[i]
            if i<len(reactants)-1:
                output+=" + "
        output+=" -> "
        for i in range(len(products)):
            output+=str(coEffi[i+len(reactants)][0])+products[i]
            if i<len(products)-1:
                output+=" + "
        return output
    except Exception as e:
        return "Erro, o balanciamento não deu certo " 

@app.route('/calculadora',  methods=['GET', 'POST'])
def calculator():
    
    resultado = None
    if request.method == 'POST':
        reactants = request.form['numero1']
        products = request.form['numero2']
        operacao = request.form['operacao']

        if operacao == 'soma':
           resultado = balanciamento(reactants, products)

        elif operacao == 'subtracao':
            resultado = reactants - products
        elif operacao == 'multiplicacao':
            resultado = reactants * products
        elif operacao == 'divisao':
            if products != 0:
                resultado = reactants / products
            else:
                resultado = "Erro: divisão por zero"

    return render_template('calculadora.html', resultado=resultado)

        
if __name__ == "__main__":
    app.run(debug=True)
