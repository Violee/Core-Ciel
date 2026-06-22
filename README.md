# Core Ciel — 🇺🇸 English

Core Ciel is an automation platform designed to centralize, monitor, and process operational reports generated across multiple independent systems.

### Overview

Many organizations rely on multiple third-party platforms that operate independently and do not communicate with one another. This often leads to fragmented workflows, delayed report submissions, manual follow-ups, and increased operational overhead.

Core Ciel was created to solve this problem by acting as a centralized automation layer between these systems, improving visibility, reducing manual work, and streamlining reporting processes.

### Why I Built This

I developed Core Ciel after identifying inefficiencies caused by disconnected third-party platforms used in daily operations.

The lack of integration required significant manual effort to collect reports, track overdue submissions, organize files and images, and prepare final deliverables for clients.

Core Ciel was designed to automate these processes, improve operational visibility, and provide a scalable foundation for future workflow automation.

### Features

#### Report Consolidation

Collects reports from multiple departments and third-party systems and consolidates them into a single structured dataset, eliminating the need for manual aggregation.

#### Delay Monitoring

Automatically identifies overdue reports and notifies responsible personnel through:

* Email notifications
* Telegram bot alerts

This allows managers and team members to track compliance and pending activities in real time.

#### Media Processing

Downloads and organizes report-related files and images, ensuring all supporting documentation is properly structured and accessible.

#### Final Report Pipeline

Processes validated information and prepares the final dataset used by reporting platforms responsible for generating customer-facing deliverables.

### Architecture

```text
Third-Party Systems
        ↓
 Report Collection
        ↓
 Data Consolidation
        ↓
 Delay Monitoring
        ↓
 Email & Telegram Notifications
        ↓
 Media Processing
        ↓
 Final Reporting Platform
        ↓
 Client Deliverables
```

### Future Roadmap

The project was originally designed with an AI-assisted validation module capable of detecting and correcting inconsistent data. While this functionality was removed from the first production version, future releases may include:

* AI-powered data validation
* Automatic detection and removal of invalid images
* PDF report generation
* Advanced analytics and dashboards
* Workflow approval automation
* Additional third-party integrations
* Expanded monitoring and notification capabilities

## Tech Stack

* **Backend:** FastAPI, Uvicorn
* **Language:** Python, JavaScript
* **Automation:** Selenium
* **Data Validation:** Pydantic
* **Integrations:** Requests, REST APIs
* **Notifications:** Email, Telegram Bot API
* **Workflow Orchestration:** n8n

### Goals

* Reduce manual operational effort
* Improve visibility across teams
* Centralize information from disconnected systems
* Increase reporting reliability
* Create a scalable automation foundation

---

## Core Ciel — 🇧🇷 Português

Core Ciel é uma plataforma de automação desenvolvida para centralizar, monitorar e processar relatórios operacionais gerados por múltiplos sistemas independentes.

### Visão Geral

Muitas organizações dependem de diversas plataformas terceirizadas que operam de forma isolada e não compartilham informações entre si. Isso frequentemente resulta em fluxos de trabalho fragmentados, atrasos na entrega de relatórios, acompanhamentos manuais e aumento da carga operacional.

O Core Ciel foi criado para resolver esse problema atuando como uma camada central de automação entre esses sistemas, aumentando a visibilidade dos processos, reduzindo tarefas manuais e tornando o fluxo de relatórios mais eficiente.

### Por Que Eu Criei Este Projeto

Desenvolvi o Core Ciel após identificar diversas ineficiências causadas pela falta de integração entre plataformas utilizadas no dia a dia operacional.

A ausência de comunicação entre esses sistemas exigia um esforço significativo para coletar relatórios, identificar atrasos, organizar arquivos e imagens, além de preparar as entregas finais destinadas aos clientes.

O Core Ciel foi projetado para automatizar essas atividades, aumentar a visibilidade operacional e servir como base para futuras automações.

### Funcionalidades

#### Consolidação de Relatórios

Coleta relatórios provenientes de diferentes setores e plataformas terceirizadas, consolidando todas as informações em uma única base estruturada.

#### Monitoramento de Atrasos

Identifica automaticamente relatórios pendentes ou em atraso e notifica os responsáveis por meio de:

* E-mail
* Bot do Telegram

Isso permite o acompanhamento em tempo real das entregas e pendências operacionais.

#### Processamento de Arquivos e Imagens

Realiza o download e a organização automática de arquivos e imagens relacionados aos relatórios, garantindo que toda a documentação esteja estruturada e acessível.

#### Pipeline de Relatórios Finais

Processa os dados consolidados e prepara as informações utilizadas pelas plataformas responsáveis pela geração dos relatórios finais enviados aos clientes.

### Arquitetura

```text
Sistemas Terceirizados
          ↓
 Coleta de Relatórios
          ↓
 Consolidação de Dados
          ↓
 Monitoramento de Atrasos
          ↓
 Notificações por E-mail e Telegram
          ↓
 Organização de Arquivos e Imagens
          ↓
 Plataforma de Relatórios Finais
          ↓
 Entrega ao Cliente
```

### Próximas Funcionalidades

O projeto originalmente possuía um módulo de validação assistida por Inteligência Artificial capaz de identificar e corrigir inconsistências nos dados. Essa funcionalidade foi removida da primeira versão por questões operacionais, mas poderá retornar em futuras evoluções do sistema.

Funcionalidades planejadas:

* Validação de dados com IA
* Identificação automática de imagens inválidas
* Remoção de fotos inadequadas utilizando IA
* Geração automática de PDFs
* Dashboards e métricas operacionais
* Fluxos de aprovação automatizados
* Integração com novas plataformas
* Monitoramento avançado e alertas inteligentes

## Tecnologias Utilizadas

* **Backend:** FastAPI, Uvicorn
* **Language:** Python, JavaScript
* **Automation:** Selenium
* **Data Validation:** Pydantic
* **Integrations:** Requests, REST APIs
* **Notifications:** Email, Telegram Bot API
* **Workflow Orchestration:** n8n

### Objetivos

* Reduzir atividades manuais
* Centralizar informações de sistemas desconectados
* Melhorar a visibilidade operacional
* Aumentar a confiabilidade dos relatórios
* Criar uma base escalável para futuras automações

## Disclaimer / Aviso

This repository contains a public and sanitized version of the project. Any confidential, proprietary, or company-specific information has been removed.

Este repositório contém uma versão pública e sanitizada do projeto. Todas as informações confidenciais, proprietárias ou específicas da empresa foram removidas.

The purpose of this repository is to demonstrate software architecture, automation workflows, data processing techniques, and system integration concepts.

O objetivo deste repositório é demonstrar conceitos de arquitetura de software, automação de processos, integração de sistemas e processamento de dados.
