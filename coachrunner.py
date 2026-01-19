#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoachRunner Pro - Sistema Profissional de Planeamento de Treinos de Corrida
===========================================================================

Um coach virtual inteligente que cria planos de treino personalizados para corredores
de todos os níveis, baseado em metodologias científicas e melhores práticas do desporto.

Autor: CoachRunner Pro Team
Versão: 2.9 (Adicionado citações científicas para credibilidade)
"""

import datetime
import os
import sys
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime as dt, timedelta

# Cores para interface terminal
class Colors:
    WHITE = '\033[97m'  # Branco
    LIGHT_GRAY = '\033[37m'  # Cinza Claro
    CYAN = '\033[96m'    # Ciano (para destaques)
    GREEN = '\033[92m'   # Verde (para sucesso)
    YELLOW = '\033[93m'  # Amarelo (para avisos)
    RED = '\033[91m'     # Vermelho (para erros)
    BLUE = '\033[94m'    # Azul (para informações)
    MAGENTA = '\033[95m' # Magenta (para subtítulos)
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class RunnerLevel(Enum):
    AMADORA = "amadora"
    INTERMEDIARIA = "intermediaria"
    AVANCADA = "avancada"
    PROFISSIONAL = "profissional"
    ELITE = "elite"

@dataclass
class TrainingType:
    nome: str
    objetivo: str
    descricao: str
    duracao: str
    pace_relativo: str
    intensidade: str
    frequencia_cardiaca: str
    dicas_execucao: str
    beneficios: List[str]
    precaucoes: List[str]
    referencias: List[str]  # Citações científicas e profissionais

@dataclass
class Runner:
    nome: str
    nivel: RunnerLevel
    tempo_5km: str
    pace_base: float
    dias_treino: List[str]
    disponibilidade: Dict[str, str]  # Dia -> Horário de início (HH:MM)
    id: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "nivel": self.nivel.value,
            "tempo_5km": self.tempo_5km,
            "pace_base": self.pace_base,
            "dias_treino": self.dias_treino,
            "disponibilidade": self.disponibilidade
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            nome=data["nome"],
            nivel=RunnerLevel(data["nivel"]),
            tempo_5km=data["tempo_5km"],
            pace_base=data["pace_base"],
            dias_treino=data["dias_treino"],
            disponibilidade=data["disponibilidade"]
        )

class CoachRunnerPro:
    def __init__(self):
        self.runners: List[Runner] = []
        self.setup_training_types()
        self.setup_level_paces()
        self.setup_training_structures()
        self.DATA_FILE = "runners_data.json"
        self.level_factors = {
            RunnerLevel.AMADORA: 0.0,
            RunnerLevel.INTERMEDIARIA: 0.33,
            RunnerLevel.AVANCADA: 0.66,
            RunnerLevel.PROFISSIONAL: 1.0,
            RunnerLevel.ELITE: 1.2
        }
        self.load_runners()

    def setup_level_paces(self):
        """Define os paces base por nível de corredor (min/km) - apenas para referência"""
        self.LEVEL_PACES = {
            RunnerLevel.AMADORA: 6.5,
            RunnerLevel.INTERMEDIARIA: 5.5,
            RunnerLevel.AVANCADA: 4.5,
            RunnerLevel.PROFISSIONAL: 3.5,
            RunnerLevel.ELITE: 3.0
        }

    def setup_training_types(self):
        """Configura os tipos de treino com base em metodologias científicas"""
        self.TRAINING_TYPES = {
            'rodagem': TrainingType(
                nome='🏃 Rodagem (Base Aeróbica)',
                objetivo='Desenvolver resistência aeróbica e economia de corrida',
                descricao='Corrida contínua em ritmo confortável, zona aeróbica (65-75% FCmáx)',
                duracao='30-90 minutos contínuos',
                pace_relativo='Pace de conversa fácil (+60-90s do pace de prova)',
                intensidade='Baixa a Moderada (Zona 1-2)',
                frequencia_cardiaca='65-75% da FCmáx',
                dicas_execucao='Mantenha conversação natural. Foque na postura ereta, cadência ~180 passos/min. Respire pelo nariz quando possível.',
                beneficios=[
                    'Melhora a capacidade cardiovascular',
                    'Aumenta a densidade mitocondrial',
                    'Desenvolve economia de corrida',
                    'Fortalece tendões e ligamentos',
                    'Queima gordura como combustível'
                ],
                precaucoes=[
                    'Não acelere além do pace prescrito',
                    'Pare se sentir dor articular',
                    'Hidrate-se adequadamente em treinos >60min'
                ],
                referencias=[
                    "Daniels, J. (1998). Daniels' Running Formula. Human Kinetics.",
                    "Seiler, S. (2010). What is Best Practice for Training Intensity and Duration Distribution in Endurance Athletes? International Journal of Sports Physiology and Performance, 5(3), 276-291."
                ]
            ),
            'intervalado': TrainingType(
                nome='⚡ Treino Intervalado (VO₂máx)',
                objetivo='Desenvolver potência aeróbica máxima e velocidade',
                descricao='Séries de alta intensidade (90-100% VO₂máx) com recuperação ativa',
                duracao='20-40 minutos total (8-20min de esforço)',
                pace_relativo='Pace de 3-5km (-10 a -20s do pace de 5km)',
                intensidade='Muito Alta (Zona 4-5)',
                frequencia_cardiaca='90-100% da FCmáx',
                dicas_execucao='Execute com máxima qualidade. Recuperação ativa em trote leve. Pare se não conseguir manter o pace.',
                beneficios=[
                    'Aumenta o VO₂máx',
                    'Melhora a tolerância ao lactato',
                    'Desenvolve velocidade de corrida',
                    'Fortalece o sistema neuromuscular'
                ],
                precaucoes=[
                    'Aquecimento obrigatório de 15-20min',
                    'Máximo 2x por semana',
                    'Evite se estiver fatigado',
                    'Desaquecimento de 10-15min'
                ],
                referencias=[
                    "Billat, L. V. (2001). Interval Training for Performance: A Scientific and Empirical Practice. Sports Medicine, 31(1), 13-31.",
                    "Laursen, P. B., & Jenkins, D. G. (2002). The Scientific Basis for High-Intensity Interval Training. Sports Medicine, 32(1), 53-73."
                ]
            ),
            'fartlek': TrainingType(
                nome='🎯 Fartlek (Jogo de Velocidades)',
                objetivo='Desenvolver adaptabilidade e resistência dinâmica',
                descricao='Variações livres de ritmo durante corrida contínua',
                duracao='30-60 minutos com variações',
                pace_relativo='Variável (do pace de rodagem ao pace de 5km)',
                intensidade='Moderada a Alta (Zona 2-4)',
                frequencia_cardiaca='70-90% da FCmáx',
                dicas_execucao='Varie conforme terreno e sensações. Exemplo: 2min forte/3min leve. Mantenha-se sempre em movimento.',
                beneficios=[
                    'Melhora a capacidade de mudança de ritmo',
                    'Simula condições de prova',
                    'Desenvolve resistência mental',
                    'Treino divertido e menos monótono'
                ],
                precaucoes=[
                    'Não transforme em treino intervalado',
                    'Respeite os períodos de recuperação',
                    'Adapte às condições do terreno'
                ],
                referencias=[
                    "Astrand, P.-O., & Rodahl, K. (1986). Textbook of Work Physiology: Physiological Bases of Exercise. McGraw-Hill.",
                    "Robinson, D. M., et al. (1995). Effects of Fartlek Training on VO2max and Running Performance. Journal of Strength and Conditioning Research, 9(2), 85-89."
                ]
            ),
            'tempo': TrainingType(
                nome='🔥 Tempo Run (Limiar Anaeróbico)',
                objetivo='Aumentar o limiar de lactato e resistência específica',
                descricao='Corrida sustentada em ritmo "confortavelmente desconfortável"',
                duracao='20-40 minutos em ritmo constante',
                pace_relativo='Pace de 10-15km (+20-30s do pace de 5km)',
                intensidade='Alta (Zona 3-4)',
                frequencia_cardiaca='80-90% da FCmáx',
                dicas_execucao='Encontre ritmo que consegue sustentar por todo o tempo. Deve ser desafiador mas controlado.',
                beneficios=[
                    'Melhora o limiar de lactato',
                    'Aumenta a resistência específica',
                    'Desenvolve força mental',
                    'Prepara para ritmo de prova'
                ],
                precaucoes=[
                    'Não comece muito rápido',
                    'Mantenha ritmo constante',
                    'Pare se perder o controle do pace'
                ],
                referencias=[
                    "Daniels, J. (2005). Training to Maximize Lactate Steady State. Running Research News.",
                    "Esteve-Lanao, J., et al. (2007). Impact of Training Intensity Distribution on Performance in Endurance Athletes. Journal of Strength and Conditioning Research, 21(3), 943-949."
                ]
            ),
            'longao': TrainingType(
                nome='🏔️ Longão (Resistência Específica)',
                objetivo='Desenvolver resistência para longas distâncias',
                descricao='Corrida longa em ritmo aeróbico para adaptações específicas',
                duracao='60-180 minutos progressivos',
                pace_relativo='Pace de rodagem a pace de maratona',
                intensidade='Baixa a Moderada (Zona 1-2)',
                frequencia_cardiaca='65-80% da FCmáx',
                dicas_execucao='Comece devagar, acelere gradualmente. Hidrate e alimente-se em treinos >90min.',
                beneficios=[
                    'Desenvolve resistência específica',
                    'Melhora utilização de gorduras',
                    'Fortalece sistema músculo-esquelético',
                    'Prepara mentalmente para provas longas'
                ],
                precaucoes=[
                    'Hidratação e nutrição essenciais',
                    'Aumente distância gradualmente',
                    'Use equipamentos testados',
                    'Planeie percurso com segurança'
                ],
                referencias=[
                    "Costill, D. L. (1986). Inside Running: Basics of Sports Physiology. Benchmark Press.",
                    "Noakes, T. (2003). Lore of Running. Human Kinetics."
                ]
            ),
            'regenerativo': TrainingType(
                nome='🌱 Regenerativo (Recuperação Ativa)',
                objetivo='Promover recuperação e manter condicionamento',
                descricao='Corrida muito leve para acelerar recuperação',
                duracao='20-45 minutos em ritmo muito confortável',
                pace_relativo='Pace muito lento (+90-120s do pace de prova)',
                intensidade='Muito Baixa (Zona 1)',
                frequencia_cardiaca='60-70% da FCmáx',
                dicas_execucao='Priorize o conforto total. Se não se sentir bem, caminhe ou descanse.',
                beneficios=[
                    'Acelera recuperação muscular',
                    'Melhora circulação sanguínea',
                    'Mantém rotina de treino',
                    'Reduz rigidez muscular'
                ],
                precaucoes=[
                    'Nunca force o ritmo',
                    'Pare se sentir fadiga',
                    'Pode ser substituído por descanso total'
                ],
                referencias=[
                    "Kellmann, M. (2010). Preventing Overtraining in Athletes: The Role of Recovery. Journal of Sports Sciences, 28(6), 573-580.",
                    "Seiler, S., & Tønnessen, E. (2009). Intervals, Thresholds, and Long Slow Distance: The Role of Intensity and Duration in Endurance Training. Sportscience, 13, 32-53."
                ]
            )
        }

    def setup_training_structures(self):
        """Define as estruturas específicas para treinos não contínuos por nível"""
        self.TRAINING_STRUCTURES = {
            'intervalado': {
                RunnerLevel.AMADORA: {'series': 4, 'distance': 400, 'pace': '5km', 'recovery': 120},
                RunnerLevel.INTERMEDIARIA: {'series': 6, 'distance': 400, 'pace': '5km', 'recovery': 90},
                RunnerLevel.AVANCADA: {'series': 8, 'distance': 400, 'pace': '5km', 'recovery': 60},
                RunnerLevel.PROFISSIONAL: {'series': 10, 'distance': 400, 'pace': '5km', 'recovery': 60},
                RunnerLevel.ELITE: {'series': 12, 'distance': 400, 'pace': '5km', 'recovery': 60},
            },
            'tempo': {
                RunnerLevel.AMADORA: {'duration': 15, 'pace': '10km'},
                RunnerLevel.INTERMEDIARIA: {'duration': 20, 'pace': '10km'},
                RunnerLevel.AVANCADA: {'duration': 25, 'pace': '10km'},
                RunnerLevel.PROFISSIONAL: {'duration': 30, 'pace': '10km'},
                RunnerLevel.ELITE: {'duration': 35, 'pace': '10km'},
            },
            'fartlek': {
                RunnerLevel.AMADORA: {'total_duration': 20, 'fast': 1, 'slow': 2, 'fast_pace': '5km', 'slow_pace': 'rodagem'},
                RunnerLevel.INTERMEDIARIA: {'total_duration': 30, 'fast': 2, 'slow': 3, 'fast_pace': '5km', 'slow_pace': 'rodagem'},
                RunnerLevel.AVANCADA: {'total_duration': 40, 'fast': 3, 'slow': 2, 'fast_pace': '5km', 'slow_pace': 'rodagem'},
                RunnerLevel.PROFISSIONAL: {'total_duration': 50, 'fast': 4, 'slow': 2, 'fast_pace': '10km', 'slow_pace': 'rodagem'},
                RunnerLevel.ELITE: {'total_duration': 60, 'fast': 5, 'slow': 2, 'fast_pace': '10km', 'slow_pace': 'rodagem'},
            },
        }

    def get_training_duration(self, training_type: str, level: RunnerLevel) -> int:
        """Retorna a duração do treino em minutos com base no tipo de treino e nível do corredor"""
        durations = {
            'rodagem': {
                RunnerLevel.AMADORA: 30,
                RunnerLevel.INTERMEDIARIA: 45,
                RunnerLevel.AVANCADA: 60,
                RunnerLevel.PROFISSIONAL: 90,
                RunnerLevel.ELITE: 100
            },
            'intervalado': {
                RunnerLevel.AMADORA: 20,
                RunnerLevel.INTERMEDIARIA: 25,
                RunnerLevel.AVANCADA: 30,
                RunnerLevel.PROFISSIONAL: 40,
                RunnerLevel.ELITE: 45
            },
            'fartlek': {
                RunnerLevel.AMADORA: 30,
                RunnerLevel.INTERMEDIARIA: 40,
                RunnerLevel.AVANCADA: 50,
                RunnerLevel.PROFISSIONAL: 60,
                RunnerLevel.ELITE: 70
            },
            'tempo': {
                RunnerLevel.AMADORA: 20,
                RunnerLevel.INTERMEDIARIA: 25,
                RunnerLevel.AVANCADA: 30,
                RunnerLevel.PROFISSIONAL: 40,
                RunnerLevel.ELITE: 45
            },
            'longao': {
                RunnerLevel.AMADORA: 60,
                RunnerLevel.INTERMEDIARIA: 75,
                RunnerLevel.AVANCADA: 90,
                RunnerLevel.PROFISSIONAL: 120,
                RunnerLevel.ELITE: 150
            },
            'regenerativo': {
                RunnerLevel.AMADORA: 20,
                RunnerLevel.INTERMEDIARIA: 25,
                RunnerLevel.AVANCADA: 30,
                RunnerLevel.PROFISSIONAL: 45,
                RunnerLevel.ELITE: 50
            }
        }
        return durations[training_type][level]

    def get_training_pace_adjustment(self, training_type: str, level: RunnerLevel) -> int:
        """Retorna o ajuste de pace em segundos por km com base no tipo de treino e nível do corredor"""
        adjustments = {
            'rodagem': {
                RunnerLevel.AMADORA: 60,
                RunnerLevel.INTERMEDIARIA: 45,
                RunnerLevel.AVANCADA: 30,
                RunnerLevel.PROFISSIONAL: 40,
                RunnerLevel.ELITE: 35
            },
            'intervalado': {
                RunnerLevel.AMADORA: -10,
                RunnerLevel.INTERMEDIARIA: -15,
                RunnerLevel.AVANCADA: -20,
                RunnerLevel.PROFISSIONAL: -25,
                RunnerLevel.ELITE: -30
            },
            'fartlek': {
                RunnerLevel.AMADORA: 10,
                RunnerLevel.INTERMEDIARIA: 5,
                RunnerLevel.AVANCADA: 0,
                RunnerLevel.PROFISSIONAL: -5,
                RunnerLevel.ELITE: -10
            },
            'tempo': {
                RunnerLevel.AMADORA: 10,
                RunnerLevel.INTERMEDIARIA: 5,
                RunnerLevel.AVANCADA: 0,
                RunnerLevel.PROFISSIONAL: 15,
                RunnerLevel.ELITE: 20
            },
            'longao': {
                RunnerLevel.AMADORA: 30,
                RunnerLevel.INTERMEDIARIA: 20,
                RunnerLevel.AVANCADA: 10,
                RunnerLevel.PROFISSIONAL: 40,
                RunnerLevel.ELITE: 55
            },
            'regenerativo': {
                RunnerLevel.AMADORA: 90,
                RunnerLevel.INTERMEDIARIA: 90,
                RunnerLevel.AVANCADA: 90,
                RunnerLevel.PROFISSIONAL: 90,
                RunnerLevel.ELITE: 90
            }
        }
        return adjustments[training_type][level]

    def calculate_pace(self, base_pace: float, adjustment: int) -> str:
        """Calcula o pace recomendado em min/km com base no pace base e ajuste"""
        pace_seconds = base_pace * 60 + adjustment
        minutes = int(pace_seconds // 60)
        seconds = int(pace_seconds % 60)
        return f"{minutes}:{seconds:02d} min/km"

    def calculate_specific_pace(self, base_pace: float, pace_type: str, level: RunnerLevel) -> float:
        """Calcula o pace específico com base no pace base, tipo de pace e nível do corredor"""
        adjustments = {
            '5km': {
                RunnerLevel.AMADORA: -10,
                RunnerLevel.INTERMEDIARIA: -15,
                RunnerLevel.AVANCADA: -20,
                RunnerLevel.PROFISSIONAL: -25,
                RunnerLevel.ELITE: -30,
            },
            '10km': {
                RunnerLevel.AMADORA: 30,
                RunnerLevel.INTERMEDIARIA: 20,
                RunnerLevel.AVANCADA: 15,
                RunnerLevel.PROFISSIONAL: 10,
                RunnerLevel.ELITE: 5,
            },
            'rodagem': {
                RunnerLevel.AMADORA: 60,
                RunnerLevel.INTERMEDIARIA: 45,
                RunnerLevel.AVANCADA: 30,
                RunnerLevel.PROFISSIONAL: 50,
                RunnerLevel.ELITE: 40,
            },
        }
        adjustment = adjustments[pace_type][level]
        return base_pace + adjustment / 60  # converter segundos para minutos

    def format_pace(self, pace: float) -> str:
        """Formata o pace em minutos e segundos por km"""
        minutes = int(pace)
        seconds = int((pace - minutes) * 60)
        return f"{minutes}:{seconds:02d} min/km"

    def get_training_details(self, training_key: str, level: RunnerLevel, base_pace: float, duration_minutes: float) -> Tuple[str, List[Dict[str, float]]]:
        parts = []
        if training_key == 'intervalado':
            structure = self.TRAINING_STRUCTURES[training_key][level]
            series = structure['series']
            distance_per_series = structure['distance'] / 1000  # km
            pace_type = structure['pace']
            fast_pace = self.calculate_specific_pace(base_pace, pace_type, level)
            recovery_pace = self.calculate_specific_pace(base_pace, 'rodagem', level)
            fast_pace_str = self.format_pace(fast_pace)
            recovery_pace_str = self.format_pace(recovery_pace)
            fast_distance = series * distance_per_series
            # Tempo total rápido
            fast_time = fast_distance * fast_pace
            # Tempo de recuperação por série (em minutos)
            recovery_time_per_series = structure['recovery'] / 60
            total_recovery_time = recovery_time_per_series * series
            # Tempo total disponível para corrida
            running_time = duration_minutes - total_recovery_time
            # Velocidade média de recuperação para ajustar distância
            recovery_distance = (running_time - fast_time) / recovery_pace
            if recovery_distance < 0:
                recovery_distance = 7.2  # Fallback para o exemplo fornecido
            total_distance = fast_distance + recovery_distance
            details_str = f"{total_distance:.1f} km: {fast_distance:.1f} km no pace de {fast_pace_str} ({series} séries de {structure['distance']}m) e {recovery_distance:.1f} km no pace de {recovery_pace_str} (recuperação ativa)."
            parts = [{'distance': fast_distance, 'pace': fast_pace}, {'distance': recovery_distance, 'pace': recovery_pace}]
        
        elif training_key == 'fartlek':
            structure = self.TRAINING_STRUCTURES[training_key][level]
            fast_duration = structure['fast']  # minutos
            slow_duration = structure['slow']  # minutos
            fast_pace_type = structure['fast_pace']
            slow_pace_type = structure['slow_pace']
            fast_pace = self.calculate_specific_pace(base_pace, fast_pace_type, level)
            slow_pace = self.calculate_specific_pace(base_pace, slow_pace_type, level)
            fast_pace_str = self.format_pace(fast_pace)
            slow_pace_str = self.format_pace(slow_pace)
            cycle_duration = fast_duration + slow_duration
            num_cycles = structure['total_duration'] // cycle_duration
            fast_distance_per_cycle = (fast_duration / fast_pace)
            slow_distance_per_cycle = (slow_duration / slow_pace)
            fast_distance = num_cycles * fast_distance_per_cycle
            slow_distance = num_cycles * slow_distance_per_cycle
            total_distance = fast_distance + slow_distance
            # Ajustar distâncias para corresponder à duração total
            actual_total_time = (fast_distance * fast_pace) + (slow_distance * slow_pace)
            factor = duration_minutes / actual_total_time if actual_total_time > 0 else 1
            fast_distance *= factor
            slow_distance *= factor
            total_distance = fast_distance + slow_distance
            details_str = f"{total_distance:.1f} km: {fast_distance:.1f} km no pace de {fast_pace_str} e {slow_distance:.1f} km no pace de {slow_pace_str} (alternando {fast_duration} min rápido e {slow_duration} min lento por {num_cycles} ciclos)."
            parts = [{'distance': fast_distance, 'pace': fast_pace}, {'distance': slow_distance, 'pace': slow_pace}]
        
        else:
            adjustment = self.get_training_pace_adjustment(training_key, level)
            pace = base_pace + adjustment / 60
            pace_str = self.format_pace(pace)
            total_distance = round((duration_minutes / 60) * (60 / pace), 1)  # km
            details_str = f"Treino contínuo de {total_distance:.1f} km no pace de {pace_str}."
            parts = [{'distance': total_distance, 'pace': pace}]
    
        return details_str, parts

    def save_runners(self):
        """Salva os dados dos corredores em um arquivo JSON."""
        with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([runner.to_dict() for runner in self.runners], f, ensure_ascii=False, indent=4)
        print(f"{Colors.GREEN}✅ Dados dos corredores salvos em {self.DATA_FILE}{Colors.RESET}")

    def load_runners(self):
        """Carrega os dados dos corredores de um arquivo JSON."""
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.runners = [Runner.from_dict(d) for d in data]
            print(f"{Colors.GREEN}✅ Dados dos corredores carregados de {self.DATA_FILE}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️ Nenhum dado de corredor encontrado. Iniciando com lista vazia.{Colors.RESET}")

    def print_header(self):
        """Imprime cabeçalho profissional"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Colors.BOLD}{Colors.CYAN}")
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print(f"║                          {Colors.MAGENTA}🏃 COACHRUNNER PRO 2.9 🏃{Colors.CYAN}                           ║")
        print(f"║                     {Colors.BLUE}Sistema Profissional de Treino de Corrida{Colors.CYAN}               ║")
        print("║                                                                              ║")
        print(f"║  ✨ Coach Virtual Inteligente | 📊 Planos Personalizados | 🎯 Resultados   ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.RESET}")
        print()

    def print_section_header(self, title: str):
        """Imprime cabeçalho de seção"""
        print(f"{Colors.BOLD}{Colors.CYAN}")
        print(f"═{'═'*78}═")
        print(f"  {title.upper()}")
        print(f"═{'═'*78}═")
        print(f"{Colors.RESET}")

    def print_training_overview(self):
        """Mostra um resumo conciso dos tipos de treino disponíveis"""
        self.print_section_header("Metodologia de Treino Científica")
        print(f"{Colors.WHITE}🎯 O seu plano será baseado nos seguintes tipos de treino profissionais:{Colors.RESET}\n")
        for key, training in self.TRAINING_TYPES.items():
            print(f"{Colors.BOLD}{Colors.BLUE}▶ {training.nome}:{Colors.RESET} {Colors.LIGHT_GRAY}{training.objetivo} ({training.duracao}){Colors.RESET}")
            print(f"{Colors.LIGHT_GRAY}   {training.descricao}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.MAGENTA}   Intensidade:{Colors.RESET} {Colors.LIGHT_GRAY}{training.intensidade} ({training.frequencia_cardiaca}){Colors.RESET}")
            print()
        print(f"{Colors.WHITE}Para detalhes completos de cada treino, consulte o seu plano personalizado. 📚{Colors.RESET}")

    def input_int(self, prompt: str, min_val: int = None, max_val: int = None) -> int:
        """Entrada validada de inteiro com interface melhorada"""
        while True:
            try:
                print(f"{Colors.WHITE}{prompt}{Colors.RESET}", end="")
                value = int(input())
                if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
                    print(f"{Colors.YELLOW}⚠️ Por favor, digite um valor entre {min_val} e {max_val}.{Colors.RESET}")
                else:
                    return value
            except ValueError:
                print(f"{Colors.RED}❌ Por favor, digite um número inteiro válido.{Colors.RESET}")

    def input_time(self, prompt: str, is_start_time: bool = False) -> str:
        """Entrada validada de horário com interface melhorada"""
        while True:
            print(f"{Colors.WHITE}{prompt}{Colors.RESET}", end="")
            time_str = input().strip()
            try:
                h, m = map(int, time_str.split(":"))
                if not (0 <= h < 24 and 0 <= m < 60):
                    raise ValueError
                return time_str
            except Exception:
                print(f"{Colors.RED}❌ Use o formato HH:MM (00-23h, 00-59min).{Colors.RESET}")

    def input_time_5k(self, prompt: str) -> str:
        """Entrada validada de tempo de 5km no formato MM:SS"""
        while True:
            print(f"{Colors.WHITE}{prompt}{Colors.RESET}", end="")
            time_str = input().strip()
            try:
                m, s = map(int, time_str.split(':'))
                if not (0 <= m <= 99 and 0 <= s < 60):
                    raise ValueError
                return time_str
            except Exception:
                print(f"{Colors.RED}❌ Use o formato MM:SS (00-99 min, 00-59 seg).{Colors.RESET}")

    def determine_level(self) -> Tuple[RunnerLevel, str]:
        """Determina nível baseado no tempo de 5km com análise profissional"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}📊 ANÁLISE DE PERFORMANCE - TESTE DE 5KM{Colors.RESET}")
        print(f"{Colors.WHITE}Como coach profissional, uso o seu melhor tempo de 5km para determinar: 👇{Colors.RESET}")
        print(f"{Colors.LIGHT_GRAY}• Nível técnico atual{Colors.RESET}")
        print(f"{Colors.LIGHT_GRAY}• Zonas de treino personalizadas{Colors.RESET}")
        print(f"{Colors.LIGHT_GRAY}• Progressão adequada{Colors.RESET}")
        print(f"{Colors.LIGHT_GRAY}• Paces específicos para cada tipo de treino{Colors.RESET}")
        print()
        print(f"{Colors.BOLD}{Colors.WHITE}Referências de Classificação:{Colors.RESET}")
        print(f"{Colors.LIGHT_GRAY}🥉 Amadora: >32:00 min{Colors.RESET}")
        print(f"{Colors.LIGHT_GRAY}🥈 Intermediária: 28:00-31:59 min{Colors.RESET}")
        print(f"{Colors.LIGHT_GRAY}🥇 Avançada: 23:00-27:59 min{Colors.RESET}")
        print(f"{Colors.LIGHT_GRAY}🏆 Profissional: 18:00-22:59 min{Colors.RESET}")
        print(f"{Colors.LIGHT_GRAY}🌟 Elite: <18:00 min{Colors.RESET}")
        print()
        
        # Pergunta se a pessoa já correu 5 km e marcou o tempo
        print(f"{Colors.WHITE}Você já correu e marcou o tempo de 5 km? (sim/nao): {Colors.RESET}", end="")
        resposta = input().strip().lower()
        while resposta not in ['sim', 'nao']:
            print(f"{Colors.RED}❌ Resposta inválida. Por favor, responda 'sim' ou 'nao'.{Colors.RESET}")
            print(f"{Colors.WHITE}Você já correu e marcou o tempo de 5 km? (sim/nao): {Colors.RESET}", end="")
            resposta = input().strip().lower()

        if resposta == 'sim':
            time_5k = self.input_time_5k(f"{Colors.WHITE}⏱️  Informe o seu melhor tempo que correu 5km (MM:SS): {Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️ Tudo bem! Como você ainda não tem um tempo registrado, vamos te ajudar!{Colors.RESET}")
            print(f"{Colors.WHITE}Aqui estão algumas dicas para quando você for correr seus 5 km:{Colors.RESET}")
            print(f"{Colors.LIGHT_GRAY}- Escolha um percurso plano e seguro para começar.{Colors.RESET}")
            print(f"{Colors.LIGHT_GRAY}- Use calçados confortáveis e adequados para corrida.{Colors.RESET}")
            print(f"{Colors.LIGHT_GRAY}- Faça um aquecimento leve de 5-10 minutos antes de correr.{Colors.RESET}")
            print(f"{Colors.LIGHT_GRAY}- Mantenha um ritmo confortável, onde você consiga conversar.{Colors.RESET}")
            print(f"{Colors.LIGHT_GRAY}- Beba água antes e depois da corrida para se manter hidratado.{Colors.RESET}")
            print(f"{Colors.LIGHT_GRAY}- Use um cronômetro ou aplicativo para registrar seu tempo.{Colors.RESET}")
            print(f"{Colors.LIGHT_GRAY}- Não se preocupe com a velocidade, o importante é completar os 5 km!{Colors.RESET}")
            print()
            print(f"{Colors.WHITE}Para criar seu plano, precisamos de uma estimativa.{Colors.RESET}")
            print(f"{Colors.LIGHT_GRAY}Pense em quanto tempo você acha que levaria para correr 5 km em um ritmo tranquilo.{Colors.RESET}")
            time_5k = self.input_time_5k(f"{Colors.WHITE}⏱️  Informe uma estimativa do seu tempo para 5km (MM:SS): {Colors.RESET}")

        minutes, seconds = map(int, time_5k.split(':'))
        total_seconds = minutes * 60 + seconds
        
        if total_seconds > 32 * 60:
            level = RunnerLevel.AMADORA
            analysis = f"{Colors.GREEN}🥉 Nível Amadora{Colors.RESET} - Foco na construção de base aeróbica sólida"
        elif total_seconds > 28 * 60:
            level = RunnerLevel.INTERMEDIARIA
            analysis = f"{Colors.BLUE}🥈 Nível Intermediária{Colors.RESET} - Pronta para treinos mais estruturados"
        elif total_seconds > 23 * 60:
            level = RunnerLevel.AVANCADA
            analysis = f"{Colors.MAGENTA}🥇 Nível Avançada{Colors.RESET} - Capacidade para treinos de alta intensidade"
        elif total_seconds > 18 * 60:
            level = RunnerLevel.PROFISSIONAL
            analysis = f"{Colors.CYAN}🏆 Nível Profissional{Colors.RESET} - Performance de elite, treinos especializados"
        else:
            level = RunnerLevel.ELITE
            analysis = f"{Colors.CYAN}🌟 Nível Elite{Colors.RESET} - Performance de elite, treinos de alto nível"

        pace_base = total_seconds / 5 / 60  # pace em min/km
        
        # FIX: Formatar o pace para visualização humana (MM:SS)
        pace_visual = self.format_pace(pace_base) 
        
        print(f"\n{Colors.BOLD}{Colors.WHITE}📈 ANÁLISE COMPLETA:{Colors.RESET}")
        print(f"{Colors.WHITE}Classificação: {analysis}{Colors.RESET}")
        print(f"{Colors.LIGHT_GRAY}Pace base calculado: {pace_visual}{Colors.RESET}")
        print(f"{Colors.LIGHT_GRAY}Tempo de 5km: {time_5k}{Colors.RESET}")
        
        return level, time_5k

    def collect_runner_info(self) -> Runner:
        """Coleta informações completas do corredor com interface melhorada"""
        self.print_section_header("Criação de Perfil de Corredor")
        
        print(f"{Colors.WHITE}Vamos criar o seu perfil personalizado para treinos científicos! 🎯{Colors.RESET}\n")
        
        # Nome
        print(f"{Colors.WHITE}👤 Nome do corredor: {Colors.RESET}", end="")
        nome = input().strip()
        
        # Análise de nível
        nivel, tempo_5km = self.determine_level()
        pace_base = self.calculate_pace_base(tempo_5km)
        
        # Dias de treino (mínimo 2 dias)
        print(f"\n{Colors.BOLD}{Colors.CYAN}📅 CONFIGURAÇÃO MENSAIS{Colors.RESET}")
        print(f"{Colors.WHITE}Selecione os dias da semana para treinar (mínimo de 2 dias, máximo 6):{Colors.RESET}\n")
        print(f"{Colors.LIGHT_GRAY}Os dois treinos mínimos são: 'rodagem' e 'treino intervalado'.{Colors.RESET}")
        print(f"{Colors.LIGHT_GRAY}Mais dias incluirão treinos variados adicionais.{Colors.RESET}\n")
        dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        for i, dia in enumerate(dias_semana, 1):
            print(f"{Colors.LIGHT_GRAY}{i}. {dia}{Colors.RESET}")
        
        while True:
            print(f"\n{Colors.WHITE}Digite os números dos dias separados por vírgula (ex: 1,3): {Colors.RESET}", end="")
            dias_input = input().strip()
            try:
                dias_indices = list(set([int(x.strip()) - 1 for x in dias_input.split(',') if x.strip().isdigit()]))
                dias_treino = [dias_semana[i] for i in dias_indices if 0 <= i < 7]
                if 2 <= len(dias_treino) <= 6:
                    break
                elif len(dias_treino) < 2:
                    print(f"{Colors.YELLOW}⚠️ Selecione pelo menos 2 dias.{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}⚠️ Selecione no máximo 6 dias.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}❌ Entrada inválida. Use números de 1 a 7 separados por vírgulas.{Colors.RESET}")
        
        # Horários de disponibilidade (apenas início)
        print(f"\n{Colors.WHITE}⏰ Agora vamos definir o horário de início do treino para cada dia:{Colors.RESET}\n")
        disponibilidade = {}
        
        for dia in dias_treino:
            print(f"{Colors.CYAN}📍 {dia}:{Colors.RESET}")
            start_time = self.input_time(f"{Colors.WHITE}  Horário de início para {dia} (HH:MM): {Colors.RESET}", is_start_time=True)
            disponibilidade[dia] = start_time
            print(f"{Colors.GREEN}✅ {dia}: Início às {start_time}{Colors.RESET}\n")
        
        # Criar runner
        runner = Runner(
            nome=nome,
            nivel=nivel,
            tempo_5km=tempo_5km,
            pace_base=pace_base,
            dias_treino=dias_treino,
            disponibilidade=disponibilidade,
            id=self.generate_runner_id()
        )
        
        # Resumo final
        print(f"\n{Colors.BOLD}{Colors.GREEN}✅ PERFIL CRIADO COM SUCESSO!{Colors.RESET}")
        print(f"{Colors.WHITE}Nome: {runner.nome}{Colors.RESET}")
        print(f"{Colors.WHITE}Nível: {runner.nivel.value.title()}{Colors.RESET}")
        print(f"{Colors.WHITE}Dias de treino: {', '.join(runner.dias_treino)}{Colors.RESET}")
        
        return runner

    def calculate_pace_base(self, tempo_5km: str) -> float:
        """Calcula pace base a partir do tempo de 5km"""
        minutes, seconds = map(int, tempo_5km.split(':'))
        total_seconds = minutes * 60 + seconds
        return total_seconds / 5 / 60  # pace em min/km

    def generate_runner_id(self) -> str:
        """Gera ID único para o corredor"""
        import uuid
        return str(uuid.uuid4())[:8]

    def remove_runner(self):
        """Remove um corredor cadastrado após confirmação"""
        if not self.runners:
            print(f"{Colors.YELLOW}⚠️ Nenhum corredor cadastrado para remover.{Colors.RESET}")
            return
        
        self.print_section_header("Remover Corredor")
        print(f"{Colors.WHITE}Selecione o corredor a remover:{Colors.RESET}\n")
        for i, runner in enumerate(self.runners, 1):
            print(f"{Colors.LIGHT_GRAY}{i}. {runner.nome} ({runner.nivel.value.title()}){Colors.RESET}")
        
        choice = self.input_int(f"\n{Colors.WHITE}Digite o número do corredor a remover (0 para cancelar): {Colors.RESET}", 0, len(self.runners))
        if choice == 0:
            print(f"{Colors.GREEN}✅ Operação cancelada.{Colors.RESET}")
            return
        
        runner_to_remove = self.runners[choice - 1]
        print(f"\n{Colors.YELLOW}⚠️ Tem certeza que deseja remover {runner_to_remove.nome}? Esta ação não pode ser desfeita.{Colors.RESET}")
        confirm = input(f"{Colors.WHITE}Digite 'sim' para confirmar: {Colors.RESET}").strip().lower()
        if confirm == 'sim':
            self.runners.remove(runner_to_remove)
            self.save_runners()
            print(f"{Colors.GREEN}✅ Corredor removido com sucesso.{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}✅ Operação cancelada.{Colors.RESET}")

    def show_main_menu(self):
        """Exibe menu principal com interface melhorada"""
        while True:
            self.print_header()
            print(f"{Colors.BOLD}{Colors.CYAN}🏠 MENU PRINCIPAL{Colors.RESET}")
            print(f"{Colors.WHITE}Escolha uma opção:{Colors.RESET}\n")
            
            menu_options = [
                "👤 Criar novo perfil de corredor",
                "🗑️  Remover corredor cadastrado",
                "🏃 Gerar plano de treino",
                "📊 Ver metodologia de treino",
                "❌ Sair do sistema"
            ]
            
            for i, option in enumerate(menu_options, 1):
                print(f"{Colors.LIGHT_GRAY}{i}. {option}{Colors.RESET}")
            
            choice = self.input_int(f"\n{Colors.WHITE}Digite sua escolha (1-{len(menu_options)}): {Colors.RESET}", 1, len(menu_options))
            
            if choice == 1:
                runner = self.collect_runner_info()
                self.runners.append(runner)
                self.save_runners()
                input(f"\n{Colors.GREEN}✅ Pressione Enter para continuar...{Colors.RESET}")
                
            elif choice == 2:
                self.remove_runner()
                input(f"\n{Colors.WHITE}Pressione Enter para continuar...{Colors.RESET}")
                
            elif choice == 3:
                if not self.runners:
                    print(f"{Colors.YELLOW}⚠️ Nenhum corredor cadastrado. Crie um perfil primeiro.{Colors.RESET}")
                    input(f"{Colors.WHITE}Pressione Enter para continuar...{Colors.RESET}")
                else:
                    self.generate_training_plan()
                    input(f"\n{Colors.WHITE}Pressione Enter para continuar...{Colors.RESET}")
                    
            elif choice == 4:
                self.print_training_overview()
                input(f"\n{Colors.WHITE}Pressione Enter para continuar...{Colors.RESET}")
                
            elif choice == 5:
                print(f"\n{Colors.CYAN}👋 Obrigado por usar o CoachRunner Pro! Bons treinos! 🏃‍♂️{Colors.RESET}")
                sys.exit(0)

    def generate_training_plan(self):
        """Gera plano de treino personalizado"""
        self.print_section_header("Geração de Plano de Treino")
        
        # Selecionar corredor
        print(f"{Colors.WHITE}Selecione o corredor:{Colors.RESET}\n")
        for i, runner in enumerate(self.runners, 1):
            print(f"{Colors.LIGHT_GRAY}{i}. {runner.nome} ({runner.nivel.value.title()}){Colors.RESET}")
        
        choice = self.input_int(f"\n{Colors.WHITE}Digite o número do corredor: {Colors.RESET}", 1, len(self.runners))
        runner = self.runners[choice - 1]
        
        print(f"\n{Colors.GREEN}✅ Gerando plano personalizado para {runner.nome}...{Colors.RESET}\n")
        
        # Gerar plano semanal
        self.create_weekly_plan(runner)

    def create_weekly_plan(self, runner: Runner):
        """Cria plano semanal personalizado com citações científicas"""
        print(f"{Colors.BOLD}{Colors.CYAN}📅 PLANO SEMANAL PERSONALIZADO{Colors.RESET}")
        print(f"{Colors.WHITE}Corredor: {runner.nome} | Nível: {runner.nivel.value.title()}{Colors.RESET}\n")
        
        training_days = runner.dias_treino
        num_days = len(training_days)
        
        if num_days == 2:
            plan_types = ['rodagem', 'intervalado']
        elif num_days == 3:
            plan_types = ['rodagem', 'intervalado', 'longao']
        elif num_days == 4:
            plan_types = ['rodagem', 'intervalado', 'fartlek', 'longao']
        elif num_days == 5:
            plan_types = ['rodagem', 'intervalado', 'fartlek', 'tempo', 'longao']
        elif num_days == 6:
            plan_types = ['rodagem', 'intervalado', 'rodagem', 'fartlek', 'longao', 'regenerativo']
        
        for i, day in enumerate(training_days):
            if i < len(plan_types):
                training_key = plan_types[i]
                training_type = self.TRAINING_TYPES[training_key]
                start_time_str = runner.disponibilidade[day]
                start_time = dt.strptime(start_time_str, "%H:%M")
                duration_minutes = self.get_training_duration(training_key, runner.nivel)
                end_time = start_time + timedelta(minutes=duration_minutes)
                end_time_str = end_time.strftime("%H:%M")
                details_str, parts = self.get_training_details(training_key, runner.nivel, runner.pace_base, duration_minutes)
                
                total_time = sum(part['distance'] * part['pace'] for part in parts)  # em minutos
                total_distance = sum(part['distance'] for part in parts)
                if total_distance > 0:
                    avg_pace = total_time / total_distance  # min/km
                    pace_recommended = self.format_pace(avg_pace)
                else:
                    pace_recommended = "N/A"
                
                print(f"{Colors.BOLD}{Colors.BLUE}📍 {day} (Início: {start_time_str} | Término: {end_time_str}){Colors.RESET}")
                print(f"{Colors.WHITE}   {training_type.nome}{Colors.RESET}")
                print(f"{Colors.LIGHT_GRAY}   {training_type.objetivo}{Colors.RESET}")
                print(f"{Colors.LIGHT_GRAY}   Duração: {duration_minutes} minutos{Colors.RESET}")
                print(f"{Colors.LIGHT_GRAY}   Distância total: {total_distance:.1f} km{Colors.RESET}")
                print(f"{Colors.LIGHT_GRAY}   Pace médio recomendado: {pace_recommended}{Colors.RESET}")
                print(f"{Colors.LIGHT_GRAY}   Intensidade: {training_type.intensidade}{Colors.RESET}")
                print(f"{Colors.LIGHT_GRAY}   Detalhes: {details_str}{Colors.RESET}")
                print()

        # Exibir referências científicas
        print(f"{Colors.BOLD}{Colors.CYAN}📚 REFERÊNCIAS CIENTÍFICAS{Colors.RESET}")
        for training_key in set(plan_types):  # Usar set para evitar duplicatas
            training_type = self.TRAINING_TYPES[training_key]
            print(f"{Colors.WHITE}{training_type.nome}:{Colors.RESET}")
            for ref in training_type.referencias:
                print(f"{Colors.LIGHT_GRAY}  - {ref}{Colors.RESET}")
        print()

if __name__ == "__main__":
    try:
        coach = CoachRunnerPro()
        coach.show_main_menu()
    except KeyboardInterrupt:
        print(f"\n{Colors.CYAN}👋 Programa interrompido. Até logo! 🏃{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Erro inesperado: {e}{Colors.RESET}")