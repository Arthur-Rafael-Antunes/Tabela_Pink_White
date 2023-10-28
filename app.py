from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import re
from sympy import Matrix, lcm




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tabela_periodica.db'
db = SQLAlchemy(app)

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# Defina o mecanismo de conexão
engine = create_engine('sqlite:///tabela_periodica.db')

# Crie uma instância da classe base declarativa
Base = declarative_base()

# Defina as classes de modelo para suas tabelas
class PropriedadesEletromagneticas(Base):
    __tablename__ = 'propriedades_eletromagneticas'

    id_propriedades_eletromagneticas = Column(Integer, primary_key=True)
    condutividade_eletromagnetica = Column(String(50))
    tipo_eletrico = Column (String(50))
    tipo_magnetico = Column (String(50))
    sensibilidade_magnetica_volume = Column (String(50))
    sensibilidade_magnetica_massa = Column (String(50))
    sensibilidade_magnetica_molaridade = Column (String(50))
    resistividade = Column (String(50))
    ponto_superconducao = Column (String(50))

class Reactividade(Base):
    __tablename__ = 'reatividade'

    id_reatividade = Column(Integer, primary_key=True)
    eletronegatividade = Column (String(50))
    camada_valencia = Column (String(50))
    afinidade_eletrons= Column (String(50))
    # Defina os outros campos aqui

class propriedades_atomicas(Base):
    __tablename__ = 'propriedades_atomica'

    id_propriedades_atomicas  = Column(Integer, primary_key=True)
    configuraçoes_eletrons = Column (String(50))
    estados_oxidaçao = Column (String(50))
    carga_ions = Column (String(50))
    potencial_ionizacao_atomo = Column (String(50))
    raio_atomico_pm = Column (String(50))
    raio_covalente_pm = Column (String(50))
    raio_vanderwaals_pm = Column (String(50))

class propriedades(Base):
    __tablename__ = 'propriedades'

    id_propriedades = Column(Integer, primary_key=True)
    numero_atomico = Column (String(50))
    massa_atomica = Column (String(50))
    densidade = Column (String(50))
    ponto_fusao = Column (String(50))
    ponto_ebulicao = Column (String(50))
    camada_valencia = Column (String(50))
    periodo = Column (String(50))
    grupo = Column (String(50))
    lugar_tabela = Column (String(50))
    expectro_emissao = Column (String(50))

class geral(Base):
    __tablename__ = 'geral'

    id_geral = Column(Integer, primary_key=True)
    nome= Column (String(50))
    nome_latim= Column (String(50))
    ano_descobrimento = Column (String(50))
    cas = Column (String(50))
    decoberto_por = Column (String(50))
    custo_100_gramas = Column (String(50))
    camada_eletron= Column (String(50))
    qtd_protons = Column (String(50))
    qtd_neutrons = Column (String(50))
    qtd_eletrons = Column (String(50))

class tabela_periodica(Base):
    __tablename__ = 'tabela_periodica'
    id_elemento = Column(Integer, primary_key=True)
    id_propriedades_eletromagneticas = Column(Integer, ForeignKey('propriedades_eletromagneticas.id_propriedades_eletromagneticas'))
    id_reatividade = Column(Integer, ForeignKey('reatividade.id_reatividade'))
    id_propriedades_atomicas = Column(Integer, ForeignKey('propriedades_atomicas.id_propriedades_atomicas'))
    id_propriedades = Column(Integer, ForeignKey('propriedades.id_propriedades'))
    id_geral = Column(Integer, ForeignKey('geral.id_geral'))

    elemento_propriedades_eletromagneticas = relationship('propriedades_eletromagneticas', foreign_keys=[id_propriedades_eletromagneticas])
    elemento_reatividade = relationship('reatividade', foreign_keys=[id_reatividade])
    elemento_propriedades_atomicas = relationship('propriedades_atomica', foreign_keys=[id_propriedades_atomicas])
    elemento_propriedades = relationship('propriedades', foreign_keys=[id_propriedades])
    elemento_geral = relationship('geral', foreign_keys=[id_geral])

# Crie as tabelas no banco de dados
Base.metadata.create_all(engine)

db.create_all()


@app.route('/')
def index():
    return render_template('index.html')



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

@app.route('/calculador',  methods=['GET', 'POST'])
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

def tabela_periodica():
    elementos = tabela_periodica.query.all()  # Recupera todos os elementos da tabela 'tabela_periodica'
    return render_template('tabela_periodica.html', elementos=elementos)
