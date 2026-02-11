#!/usr/bin/env python
"""
Script de inicialização do banco de dados
Execute este script para criar as tabelas necesárias no PostgreSQL

Uso:
    python setup_db.py

Certifique-se que DATABASE_URL está configurada no .env
"""

import os
import sys
from dotenv import load_dotenv
from database import engine, Base, Profissional, Procedimento, Agendamento, Feriado, HorarioFuncionamento

# Carregar variáveis de ambiente
load_dotenv()

def criar_tabelas():
    """Cria todas as tabelas no banco de dados"""
    print("🔄 Criando tabelas no banco de dados...")
    
    try:
        # Criar todas as tabelas definidas em Base
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
        
        # Verificar se tabelas foram criadas
        inspector_result = engine.inspect(engine)
        tables = inspector_result.get_table_names()
        print(f"\n📊 Tabelas criadas: {', '.join(tables)}")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def inserir_dados_iniciais():
    """Insere dados iniciais de exemplo"""
    from database import SessionLocal
    
    print("\n📝 Inserindo dados iniciais...")
    
    db = SessionLocal()
    try:
        # Verificar se já existem dados
        existing_profs = db.query(Profissional).count()
        if existing_profs > 0:
            print("⚠️  Dados iniciais já existem. Pulando inserção...")
            return True
        
        # Inserir profissionais
        profissionais = [
            Profissional(
                nome="Rayssa",
                especialidade="Corte e Penteado",
                dias_uteis=["segunda", "terca", "quarta", "quinta", "sexta", "sabado"],
                intervalo_entre_clientes=15
            ),
            Profissional(
                nome="Marcia",
                especialidade="Manicure/Pedicure",
                dias_uteis=["segunda", "terca", "quarta", "quinta", "sexta", "sabado"],
                intervalo_entre_clientes=20
            ),
            Profissional(
                nome="Mirian",
                especialidade="Tratamentos Capilares",
                dias_uteis=["segunda", "terca", "quarta", "quinta", "sexta"],
                intervalo_entre_clientes=30
            ),
        ]
        
        for prof in profissionais:
            db.add(prof)
        
        db.commit()
        print(f"✅ {len(profissionais)} profissionais inseridas com sucesso!")
        
        # Inserir procedimentos para cada profissional
        procedimentos_data = {
            1: [  # Rayssa
                {"codigo": "101", "nome": "Corte Simples", "duracao_minutos": 30, "preco": 50.00},
                {"codigo": "102", "nome": "Corte Progressiva", "duracao_minutos": 90, "preco": 120.00},
                {"codigo": "103", "nome": "Escova", "duracao_minutos": 45, "preco": 60.00},
            ],
            2: [  # Marcia
                {"codigo": "201", "nome": "Manicure", "duracao_minutos": 30, "preco": 40.00},
                {"codigo": "202", "nome": "Pedicure", "duracao_minutos": 40, "preco": 50.00},
                {"codigo": "203", "nome": "Alongamento de Unhas", "duracao_minutos": 60, "preco": 80.00},
            ],
            3: [  # Mirian
                {"codigo": "301", "nome": "Hidratação", "duracao_minutos": 60, "preco": 70.00},
                {"codigo": "302", "nome": "Botox", "duracao_minutos": 50, "preco": 90.00},
                {"codigo": "303", "nome": "Progressiva", "duracao_minutos": 120, "preco": 150.00},
            ],
        }
        
        total_procs = 0
        for prof_id, procs in procedimentos_data.items():
            for proc_data in procs:
                proc = Procedimento(
                    profissional_id=prof_id,
                    codigo=proc_data["codigo"],
                    nome=proc_data["nome"],
                    duracao_minutos=proc_data["duracao_minutos"],
                    preco=proc_data["preco"],
                    descricao=f"Procedimento: {proc_data['nome']}"
                )
                db.add(proc)
                total_procs += 1
        
        db.commit()
        print(f"✅ {total_procs} procedimentos inseridos com sucesso!")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao inserir dados: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Função principal"""
    print("=" * 50)
    print("🏢 Inicialização do Banco de Dados - Marcia Rocha Beauty")
    print("=" * 50)
    
    # Verificar se DATABASE_URL está configurada
    if not os.getenv('DATABASE_URL'):
        print("\n❌ Erro: DATABASE_URL não está configurada!")
        print("   Configure a variável DATABASE_URL no arquivo .env")
        sys.exit(1)
    
    # Criar tabelas
    if not criar_tabelas():
        sys.exit(1)
    
    # Inserir dados iniciais
    if not inserir_dados_iniciais():
        print("\n⚠️  Dados iniciais não foram inseridos. Você pode fazer isso manualmente.")
    
    print("\n" + "=" * 50)
    print("✨ Setup do banco de dados concluído com sucesso!")
    print("=" * 50)

if __name__ == "__main__":
    main()
