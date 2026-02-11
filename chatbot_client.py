"""
Cliente para Chatbot integrado com a API da Agenda App
"""

import requests
import logging
from typing import Tuple, List, Dict, Optional, Any

logger = logging.getLogger(__name__)


class ChatbotAPIClient:
    """Cliente HTTP para chamar endpoints da Agenda App"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def obter_profissionais(self) -> Tuple[bool, Optional[List[Dict]], str]:
        """
        Obtém lista de profissionais
        
        Returns:
            (sucesso, profissionais, mensagem)
        """
        try:
            response = self.session.get(f"{self.base_url}/api/profissionais")
            if response.status_code == 200:
                profs = response.json()
                return True, profs, "Profissionais obtidas com sucesso"
            else:
                return False, None, f"Erro ao obter profissionais: {response.status_code}"
        except Exception as e:
            logger.error(f"Erro ao obter profissionais: {e}")
            return False, None, str(e)
    
    def obter_procedimentos(self, prof_id: int) -> Tuple[bool, Optional[Dict], str]:
        """
        Obtém procedimentos de uma profissional
        
        Returns:
            (sucesso, procedimentos_dict, mensagem)
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/profissionais/{prof_id}/procedimentos"
            )
            if response.status_code == 200:
                procs = response.json()
                return True, procs, "Procedimentos obtidos com sucesso"
            else:
                return False, None, f"Erro ao obter procedimentos: {response.status_code}"
        except Exception as e:
            logger.error(f"Erro ao obter procedimentos: {e}")
            return False, None, str(e)
    
    def obter_datas_disponiveis(
        self, prof_id: int, dias_futuros: int = 30
    ) -> Tuple[bool, Optional[List[str]], str]:
        """
        Obtém datas disponíveis para uma profissional
        
        Returns:
            (sucesso, datas, mensagem)
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/profissionais/{prof_id}/datas-disponiveis",
                params={"dias_futuros": dias_futuros}
            )
            if response.status_code == 200:
                data = response.json()
                datas = data.get('datas', [])
                return True, datas, "Datas obtidas com sucesso"
            else:
                return False, None, f"Erro ao obter datas: {response.status_code}"
        except Exception as e:
            logger.error(f"Erro ao obter datas: {e}")
            return False, None, str(e)
    
    def obter_horarios(
        self, prof_id: int, data: str, proc_id: int
    ) -> Tuple[bool, Optional[List[str]], str]:
        """
        Obtém horários disponíveis para uma data e procedimento
        
        Args:
            prof_id: ID da profissional
            data: Data no formato DD/MM/YYYY
            proc_id: ID do procedimento
        
        Returns:
            (sucesso, horarios, mensagem)
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/profissionais/{prof_id}/horarios",
                params={"data": data, "procedimento_id": proc_id}
            )
            if response.status_code == 200:
                data_resp = response.json()
                horarios = data_resp.get('horarios', [])
                return True, horarios, "Horários obtidos com sucesso"
            else:
                return False, None, f"Erro ao obter horários: {response.status_code}"
        except Exception as e:
            logger.error(f"Erro ao obter horários: {e}")
            return False, None, str(e)
    
    def criar_agendamento(
        self,
        prof_id: int,
        data: str,
        hora: str,
        cliente_nome: str,
        cliente_telefone: str,
        procedimento_id: int,
        procedimento_nome: str,
        cliente_email: Optional[str] = None,
    ) -> Tuple[bool, Optional[str], str]:
        """
        Cria um novo agendamento
        
        Args:
            prof_id: ID da profissional
            data: Data no formato DD/MM/YYYY
            hora: Hora no formato HH:MM
            cliente_nome: Nome do cliente
            cliente_telefone: Telefone do cliente
            procedimento_id: ID do procedimento
            procedimento_nome: Nome do procedimento
            cliente_email: Email do cliente (opcional)
        
        Returns:
            (sucesso, agendamento_id, mensagem)
        """
        try:
            payload = {
                "profissional_id": prof_id,
                "data": data,
                "hora": hora,
                "cliente_nome": cliente_nome,
                "cliente_telefone": cliente_telefone,
                "procedimento_id": procedimento_id,
                "procedimento_nome": procedimento_nome,
            }
            if cliente_email:
                payload["cliente_email"] = cliente_email
            
            response = self.session.post(
                f"{self.base_url}/api/agendamentos",
                json=payload
            )
            
            if response.status_code == 201:
                data_resp = response.json()
                agendamento_id = data_resp.get('id') or data_resp.get('agendamento_id')
                return True, agendamento_id, "Agendamento criado com sucesso"
            else:
                return False, None, f"Erro ao criar agendamento: {response.status_code}"
        except Exception as e:
            logger.error(f"Erro ao criar agendamento: {e}")
            return False, None, str(e)
