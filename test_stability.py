#!/usr/bin/env python
"""
Script de teste para validar correções de estabilidade
Execute: python test_stability.py
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5001"

class CoreTestStability:
    """Testa estabilidade e confiabilidade da API"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.start_time = time.time()
    
    def print_header(self, msg):
        print(f"\n{'='*60}")
        print(f"  {msg}")
        print(f"{'='*60}")
    
    def test(self, descricao, condicao, detalhes=""):
        """Registra resultado de teste"""
        if condicao:
            print(f"✅ {descricao}")
            self.passed += 1
        else:
            print(f"❌ {descricao}")
            if detalhes:
                print(f"   {detalhes}")
            self.failed += 1
    
    def warning(self, descricao, condicao, detalhes=""):
        """Registra warning"""
        if condicao:
            print(f"⚠️  {descricao}")
            if detalhes:
                print(f"   {detalhes}")
            self.warnings += 1
    
    def test_health_check(self):
        """Testa health check endpoint"""
        self.print_header("1️⃣ Health Check")
        
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=5)
            self.test(
                "GET /api/health retorna 200",
                response.status_code == 200
            )
            
            data = response.json()
            self.test(
                "Response tem campo 'status'",
                'status' in data
            )
            self.test(
                "Response tem campo 'database'",
                'database' in data
            )
            self.test(
                "Database está conectado",
                data.get('database') == 'connected',
                f"Status: {data.get('database')}"
            )
            
        except Exception as e:
            self.test("Health check acessível", False, str(e))
    
    def test_profissionais(self):
        """Testa endpoint de profissionais"""
        self.print_header("2️⃣ Profissionais")
        
        try:
            response = requests.get(f"{BASE_URL}/api/profissionais", timeout=5)
            self.test(
                "GET /api/profissionais retorna 200",
                response.status_code == 200
            )
            
            data = response.json()
            self.test(
                "Resposta é lista",
                isinstance(data, list)
            )
            self.test(
                "Tem pelo menos 1 profissional",
                len(data) > 0,
                f"Encontradas: {len(data)}"
            )
            
            if data:
                prof = data[0]
                self.test("Profissional tem 'id'", 'id' in prof)
                self.test("Profissional tem 'nome'", 'nome' in prof)
                self.test("Profissional tem 'especialidade'", 'especialidade' in prof)
                
        except Exception as e:
            self.test("Profissionais acessível", False, str(e))
    
    def test_cache_fallback(self):
        """Testa cache com fallback"""
        self.print_header("3️⃣ Cache com Fallback")
        
        try:
            # Primeira requisição (cache miss)
            start = time.time()
            response1 = requests.get(f"{BASE_URL}/api/profissionais", timeout=5)
            time1 = time.time() - start
            
            # Segunda requisição (cache hit)
            start = time.time()
            response2 = requests.get(f"{BASE_URL}/api/profissionais", timeout=5)
            time2 = time.time() - start
            
            self.test(
                "Ambas requisições retornam 200",
                response1.status_code == 200 and response2.status_code == 200
            )
            
            # Cache hit deve ser mais rápido
            self.warning(
                f"Cache hit ({time2*1000:.0f}ms) - mais rápido que miss ({time1*1000:.0f}ms)",
                time2 < time1,
                f"Diferença: {(time1-time2)*1000:.0f}ms"
            )
            
            self.test(
                "Cache retorna dados iguais",
                response1.json() == response2.json()
            )
            
        except Exception as e:
            self.test("Cache funcionando", False, str(e))
    
    def test_error_handling(self):
        """Testa tratamento de erro"""
        self.print_header("4️⃣ Tratamento de Erro")
        
        try:
            # Profissional inválida
            response = requests.get(f"{BASE_URL}/api/profissionais/99999", timeout=5)
            self.test(
                "GET profissional inválida retorna 404",
                response.status_code == 404
            )
            
            # Resposta de erro deve ser JSON
            try:
                erro = response.json()
                self.test(
                    "Erro retorna JSON",
                    'erro' in erro or 'error' in erro
                )
            except:
                self.test("Erro retorna JSON", False, "Resposta não é JSON")
            
            # Endpoint inválido
            response = requests.get(f"{BASE_URL}/api/invalid", timeout=5)
            self.test(
                "Endpoint inválido retorna 404",
                response.status_code == 404
            )
            
        except Exception as e:
            self.test("Error handling funcionando", False, str(e))
    
    def test_load(self, requisicoes=20):
        """Testa com carga"""
        self.print_header(f"5️⃣ Teste de Carga ({requisicoes} requisições)")
        
        try:
            sucesso = 0
            erro = 0
            tempos = []
            
            for i in range(requisicoes):
                try:
                    start = time.time()
                    response = requests.get(
                        f"{BASE_URL}/api/profissionais",
                        timeout=5
                    )
                    tempo = time.time() - start
                    tempos.append(tempo)
                    
                    if response.status_code == 200:
                        sucesso += 1
                    else:
                        erro += 1
                    
                    # Mostrar progresso
                    sys.stdout.write(f"\r  Progresso: {i+1}/{requisicoes}")
                    sys.stdout.flush()
                    
                except Exception as e:
                    erro += 1
            
            print()  # Nova linha
            
            taxa_sucesso = (sucesso / requisicoes) * 100
            self.test(
                f"Taxa de sucesso >= 95%",
                taxa_sucesso >= 95,
                f"Sucesso: {taxa_sucesso:.1f}% ({sucesso}/{requisicoes})"
            )
            
            tempo_medio = sum(tempos) / len(tempos) if tempos else 0
            tempo_max = max(tempos) if tempos else 0
            tempo_min = min(tempos) if tempos else 0
            
            print(f"  ⏱️  Tempo Médio: {tempo_medio*1000:.0f}ms")
            print(f"  ⏱️  Tempo Min: {tempo_min*1000:.0f}ms")
            print(f"  ⏱️  Tempo Max: {tempo_max*1000:.0f}ms")
            
            self.warning(
                "Tempo médio < 500ms",
                tempo_medio < 0.5,
                f"Tempo: {tempo_medio*1000:.0f}ms"
            )
            
        except Exception as e:
            print(f"  Erro: {e}")
    
    def test_parametros(self):
        """Testa validação de parâmetros"""
        self.print_header("6️⃣ Validação de Parâmetros")
        
        try:
            # Parâmetro faltando
            response = requests.get(
                f"{BASE_URL}/api/profissionais/1/horarios",
                timeout=5
            )
            self.test(
                "Parâmetro faltando retorna 400",
                response.status_code == 400
            )
            
            # Parâmetro inválido
            response = requests.get(
                f"{BASE_URL}/api/profissionais/abc/datas-disponiveis",
                timeout=5
            )
            self.test(
                "Parâmetro inválido (string em vez de int) retorna erro",
                response.status_code >= 400
            )
            
        except Exception as e:
            self.test("Validação de parâmetros", False, str(e))
    
    def run_all(self):
        """Executa todos os testes"""
        print("\n" + "="*60)
        print("  🧪 Testes de Estabilidade - Agenda App")
        print("="*60)
        print(f"  LocalHost: {BASE_URL}")
        print(f"  Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            self.test_health_check()
            self.test_profissionais()
            self.test_cache_fallback()
            self.test_error_handling()
            self.test_parametros()
            self.test_load(requisicoes=20)
        except KeyboardInterrupt:
            print("\n\n⚠️  Testes interrompidos")
            return
        
        # Resumo
        tempo_total = time.time() - self.start_time
        self.print_header("📊 Resumo de Testes")
        print(f"✅ Passaram: {self.passed}")
        print(f"❌ Falharam: {self.failed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print(f"⏱️  Tempo Total: {tempo_total:.1f}s")
        
        taxa = (self.passed / (self.passed + self.failed)) * 100 if (self.passed + self.failed) > 0 else 0
        
        if self.failed == 0 and self.passed > 0:
            print(f"\n🎉 Taxa de Sucesso: {taxa:.0f}%")
            print("✨ Sistema está ESTÁVEL!")
        else:
            print(f"\n⚠️  Taxa de Sucesso: {taxa:.0f}%")
            print("   Revise os testes que falharam acima.")
        
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    tester = CoreTestStability()
    tester.run_all()
