-- Marcia Rocha Beauty - Esquema PostgreSQL
-- Para usar no Neon Postgres

-- Criar tabela de profissionais
CREATE TABLE IF NOT EXISTS profissionais (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    especialidade VARCHAR(255),
    dias_uteis TEXT[], -- ['segunda', 'terca', ...]
    intervalo_entre_clientes INTEGER DEFAULT 10,
    tempo_medio_procedimento JSONB, -- {"101": 45, "102": 60, ...}
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de procedimentos
CREATE TABLE IF NOT EXISTS procedimentos (
    id SERIAL PRIMARY KEY,
    profissional_id INTEGER NOT NULL REFERENCES profissionais(id) ON DELETE CASCADE,
    codigo VARCHAR(10) NOT NULL,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10, 2),
    duracao_minutos INTEGER DEFAULT 30,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(profissional_id, codigo)
);

-- Criar tabela de agendamentos
CREATE TABLE IF NOT EXISTS agendamentos (
    id SERIAL PRIMARY KEY,
    codigo_agendamento VARCHAR(20) UNIQUE NOT NULL, -- AG1120260210185855
    profissional_id INTEGER NOT NULL REFERENCES profissionais(id) ON DELETE CASCADE,
    procedimento_id INTEGER NOT NULL REFERENCES procedimentos(id) ON DELETE CASCADE,
    cliente_nome VARCHAR(255) NOT NULL,
    cliente_telefone VARCHAR(20) NOT NULL,
    cliente_email VARCHAR(255),
    data_agendamento DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME,
    status VARCHAR(50) DEFAULT 'confirmado', -- confirmado, cancelado, concluido
    notas TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de feriados
CREATE TABLE IF NOT EXISTS feriados (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL UNIQUE,
    descricao VARCHAR(255),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de configurações de horário
CREATE TABLE IF NOT EXISTS horario_funcionamento (
    id SERIAL PRIMARY KEY,
    dia_semana VARCHAR(20) NOT NULL UNIQUE,
    hora_abertura TIME,
    hora_fechamento TIME,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de mensagens WhatsApp (histórico)
CREATE TABLE IF NOT EXISTS mensagens_whatsapp (
    id SERIAL PRIMARY KEY,
    telefone_usuario VARCHAR(20) NOT NULL,
    mensagem_enviada TEXT,
    mensagem_recebida TEXT,
    tipo VARCHAR(50), -- texto, agendamento, cancelamento, menu
    agendamento_id INTEGER REFERENCES agendamentos(id) ON DELETE SET NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir horários de funcionamento padrão
INSERT INTO horario_funcionamento (dia_semana, hora_abertura, hora_fechamento) VALUES
('segunda', '09:00', '19:00'),
('terca', '09:00', '19:00'),
('quarta', '09:00', '19:00'),
('quinta', '09:00', '19:00'),
('sexta', '09:00', '20:00'),
('sabado', '10:00', '17:00'),
('domingo', NULL, NULL)
ON CONFLICT (dia_semana) DO NOTHING;

-- Inserir profissionais
INSERT INTO profissionais (nome, especialidade, dias_uteis, intervalo_entre_clientes) VALUES
('Rayssa Tomaz', 'Serviços de Unhas e Pés', '{"segunda","terca","quarta","quinta","sexta","sabado"}', 10),
('Marcia Rocha', 'Beleza Avançada e Tratamentos Especializados', '{"segunda","terca","quarta","quinta","sexta","sabado"}', 10),
('Mirian Rocha', 'Cuidados com a Pele', '{"segunda","terca","quarta","quinta","sexta","sabado"}', 10)
ON CONFLICT DO NOTHING;

-- Inserir procedimentos para Rayssa (ID 1)
INSERT INTO procedimentos (profissional_id, codigo, nome, descricao, duracao_minutos) VALUES
(1, '101', 'Pedicure', 'Cuidado completo dos pés com hidratação e acabamento perfeito. Pés lindos e saudáveis! 💅', 45),
(1, '102', 'Gel', 'Unhas em gel com acabamento brilhante e durável. Escolha entre várias cores e designs! ✨', 60),
(1, '103', 'Manicure', 'Cuidado completo das unhas com design personalizado. Unhas sempre bonitas e bem cuidadas! 💄', 45),
(1, '104', 'Spa dos Pés', 'Relaxamento total com massagem e tratamento hidratante. Pés macios e revitalizados! 🧖', 60),
(1, '105', 'Plástica de Pés', 'Procedimento estético para remodelação dos pés. Pés mais bonitos e bem proporcionados! 💫', 90)
ON CONFLICT DO NOTHING;

-- Inserir procedimentos para Marcia (ID 2)
INSERT INTO procedimentos (profissional_id, codigo, nome, descricao, duracao_minutos) VALUES
(2, '201', 'Neutralização Labial', 'Ajuste de tom e pigmentação para lábios perfeitos. A técnica certa para o resultado que você quer! 👄', 45),
(2, '202', 'Micropigmentação', 'Lábios bem definidos e com coloração duradoura. Destaque natural que dura até 3 anos! 💋', 60),
(2, '203', 'Hidragloss', 'Hidratação profunda e brilho intenso para seus lábios. Maciez e brilho que todos vão notar! ✨', 45),
(2, '204', 'Lash Lifting e Design', 'Cilios naturais levantados ou extensões personalizadas. Olhar impactante e irresistível! 😍', 60),
(2, '205', 'Design de Sobrancelha', 'Design personalizado que realça seu olhar. Sobrancelhas perfeitas que harmonizam com seu rosto! 🎨', 45),
(2, '206', 'Laminação de Sobrancelha', 'Sobrancelhas estruturadas e volumosas com efeito natural. Beleza que dura semanas! 💫', 60),
(2, '207', 'Remoção de Tatuagem', 'Remoção segura e eficaz com laser especializado. Desperte-se do passado com confiança! 🖤', 90),
(2, '208', 'Peeling', 'Renovação profunda da pele com resultado brilhante. Pele radiante e renovada! 🌟', 45),
(2, '209', 'Remoção de Manchas', 'Eliminação de manchas com tecnologia avançada. Pele uniforme e Linda! 🎯', 60),
(2, '210', 'Remoção de Micropigmentação', 'Remoção de micropigmentação anterior com precisão. Comece do zero com segurança! ✨', 90)
ON CONFLICT DO NOTHING;

-- Inserir procedimentos para Mirian (ID 3)
INSERT INTO procedimentos (profissional_id, codigo, nome, descricao, duracao_minutos) VALUES
(3, '301', 'Limpeza de Pele', 'Limpeza profunda que remove impurezas sem danificar a pele. Pele limpa e revitalizada! 🧖‍♀️', 45),
(3, '302', 'Peeling Diamante', 'Esfoliação suave e eficaz com acabamento brilhante. Pele macia e luminosa! 💎', 60)
ON CONFLICT DO NOTHING;

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_agendamentos_profissional_data ON agendamentos(profissional_id, data_agendamento);
CREATE INDEX IF NOT EXISTS idx_agendamentos_status ON agendamentos(status);
CREATE INDEX IF NOT EXISTS idx_procedimentos_profissional ON procedimentos(profissional_id);
CREATE INDEX IF NOT EXISTS idx_mensagens_whatsapp_data ON mensagens_whatsapp(criado_em);

-- Views úteis
CREATE OR REPLACE VIEW v_agendamentos_proximos AS
SELECT 
    a.id,
    a.codigo_agendamento,
    p.nome as profissional,
    pr.nome as procedimento,
    a.cliente_nome,
    a.cliente_telefone,
    a.data_agendamento,
    a.hora_inicio,
    a.status
FROM agendamentos a
JOIN profissionais p ON a.profissional_id = p.id
JOIN procedimentos pr ON a.procedimento_id = pr.id
WHERE a.data_agendamento >= CURRENT_DATE
AND a.status = 'confirmado'
ORDER BY a.data_agendamento, a.hora_inicio;

CREATE OR REPLACE VIEW v_disponibilidade_profissionais AS
SELECT 
    p.id,
    p.nome,
    COUNT(a.id) as total_agendamentos_mes,
    COUNT(CASE WHEN a.status = 'confirmado' THEN 1 END) as agendamentos_confirmados
FROM profissionais p
LEFT JOIN agendamentos a ON p.id = a.profissional_id 
AND EXTRACT(YEAR FROM a.data_agendamento) = EXTRACT(YEAR FROM CURRENT_DATE)
AND EXTRACT(MONTH FROM a.data_agendamento) = EXTRACT(MONTH FROM CURRENT_DATE)
GROUP BY p.id, p.nome;
