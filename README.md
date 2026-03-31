## health-data-client

The **health-data-client** application corresponds to the analytical layer of the HERO architecture. It consumes data from the ETL service and performs efficiency analysis using Data Envelopment Analysis (DEA), generating rankings, correlation analyses, spatial visualizations, and decision-support outputs.

This application depends on the ETL pipeline for data integration:

➡️ ETL service: https://github.com/izabelnascimento/health-data-etl

### 🔗 Data Sources
The data used in the analysis are originally collected from:
- SIOPS (Public Health Budget Information System): http://siops.datasus.gov.br/filtro_rel_ges_dt_municipal.php  
- SISAB (Primary Health Care Information System): https://sisab.saude.gov.br/paginas/acessoRestrito/relatorio/federal/saude/RelSauProducao.xhtml  
- e-Gestor APS: https://relatorioaps.saude.gov.br/cobertura/aps  

### 📄 Related Publication
This analytical pipeline is part of the HERO architecture validation and is based on previous research:

- SBSI 2025 (SmartAPSUS project context): https://sol.sbc.org.br/index.php/sbsi/article/view/34367
- SBCAS 2025 (DEA proof of concept): https://sol.sbc.org.br/index.php/sbcas/article/view/35541
- SBSI 2026 (Primary Healthcare Efficiency Indicators): not available yet

🔗 Repository: https://github.com/izabelnascimento/health-data-client