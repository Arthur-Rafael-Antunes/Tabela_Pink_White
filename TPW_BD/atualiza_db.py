from app import db  # Importe o objeto 'db' do seu aplicativo Flask

# Importe o modelo da tabela em que deseja inserir os dados
from app.models import tabela_periodica  # Substitua 'seu_app' e 'models' com os nomes corretos

# Crie uma instância do modelo e defina os valores
novo_elemento = tabela_periodica(
    nome="Hidrogênio",
    elemento_propriedades_eletromagneticas="0,0,Diamagnético,-2.23 ⋅ 10-9,-2.48 ⋅ 10-8-4.999 ⋅ 10-11 (m³/mol),0,0",
    elemento_reatividade="2.2,1,72.8 (kJ/mol)",
    elemento_propriedades_atomicas="1s1,0,H+  H-,13.53 (eV),53 (pm),38 (pm),120 (pm)",
    elemento_propriedades="1,1.00784 (g/mol),0.0000899 (g/cm³),-259.14°C = -434.45°F = 14.01K,-252.87°C = -423.17°F = 20.28K,1,1,IA,s - quadra,0",
    elemento_geral="0"
)

# Adicione o objeto à sessão do SQLAlchemy
db.session.add(Hidrogênio)

# Cometa a sessão para inserir os dados no banco de dados
db.session.commit()
