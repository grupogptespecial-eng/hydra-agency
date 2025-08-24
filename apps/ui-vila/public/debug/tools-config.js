export const TOOL_CATALOG = {
  ferramentas: {
    label: 'Ferramentas',
    types: {
      esg: {
        label: 'ESG Reports',
        tools: {
          ESGReportsWorldUNSDG: {
            label: 'ESG World – UN SDG',
            descricao: 'Indicadores globais da ONU (UN SDG API).',
            inputs: [
              { name: 'series_code', label: 'Código da série', type: 'text', required: true },
              { name: 'country_code', label: 'Código do país', type: 'text' },
              { name: 'start_year', label: 'Ano inicial', type: 'number', required: true },
              { name: 'end_year', label: 'Ano final', type: 'number', required: true }
            ],
            output: 'Lista de observações {series, country, year, value, attributes}',
            tags: ['esg', 'world', 'unsdg']
          },
          ESGReportsSectorWikiRate: {
            label: 'ESG Sector – WikiRate',
            descricao: 'Indicadores ESG por setor via WikiRate.',
            inputs: [
              { name: 'metric', label: 'Métrica', type: 'text', required: true },
              { name: 'industry', label: 'Setor/Indústria', type: 'text', required: true },
              { name: 'year', label: 'Ano', type: 'number' },
              { name: 'country', label: 'País', type: 'text' }
            ],
            output: 'Lista {metric, company, year, value, meta}',
            tags: ['esg', 'sector', 'wikirate']
          },
          ESGReportsCompanyWikiRate: {
            label: 'ESG Company – WikiRate',
            descricao: 'Indicadores ESG por empresa via WikiRate.',
            inputs: [
              { name: 'metric', label: 'Métrica', type: 'text', required: true },
              { name: 'company_name', label: 'Empresa', type: 'text', required: true },
              { name: 'year', label: 'Ano', type: 'number' }
            ],
            output: 'Lista {metric, company, year, value, meta}',
            tags: ['esg', 'company', 'wikirate']
          }
        }
      },
      datasets: {
        label: 'Datasets',
        tools: {
          DatasetsWorldWorldBank: {
            label: 'Dataset World – World Bank',
            descricao: 'Séries macro do World Bank.',
            inputs: [
              { name: 'country_code', label: 'Código do país', type: 'text', required: true },
              { name: 'series', label: 'Indicador/Série', type: 'text', required: true },
              { name: 'start_year', label: 'Ano inicial', type: 'number', required: true },
              { name: 'end_year', label: 'Ano final', type: 'number', required: true }
            ],
            output: 'Observações {country, indicator, date, value, unit}',
            tags: ['dataset', 'world', 'worldbank']
          },
          DatasetsSectorFRED: {
            label: 'Dataset Sector – FRED',
            descricao: 'Indicadores setoriais via FRED.',
            inputs: [
              { name: 'series_id', label: 'ID da série', type: 'text', required: true },
              { name: 'start_date', label: 'Data inicial (YYYY-MM-DD)', type: 'text', required: true },
              { name: 'end_date', label: 'Data final (YYYY-MM-DD)', type: 'text', required: true },
              { name: 'frequency', label: 'Frequência', type: 'text' }
            ],
            output: 'Observações {series_id, date, value, units}',
            tags: ['dataset', 'sector', 'fred']
          },
          DatasetsCompanyAlphaVantage: {
            label: 'Dataset Company – Alpha Vantage',
            descricao: 'Preços diários via Alpha Vantage.',
            inputs: [
              { name: 'symbol', label: 'Ticker', type: 'text', required: true },
              { name: 'adjusted', label: 'Ajustado?', type: 'checkbox' },
              { name: 'outputsize', label: 'Tamanho do output', type: 'text' }
            ],
            output: 'OHLCV diário {symbol, date, open, high, low, close, volume}',
            tags: ['dataset', 'company', 'alphavantage']
          }
        }
      },
      news: {
        label: 'News',
        tools: {
          NewsWorldGDELT: {
            label: 'News World – GDELT',
            descricao: 'Eventos globais do GDELT 2.0.',
            inputs: [
              { name: 'query', label: 'Consulta', type: 'text', required: true },
              { name: 'start_datetime', label: 'Início (YYYYMMDDHHMMSS)', type: 'text', required: true },
              { name: 'end_datetime', label: 'Fim (YYYYMMDDHHMMSS)', type: 'text', required: true }
            ],
            output: 'Eventos {date, source, country, theme, actor1, actor2, tone}',
            tags: ['news', 'world', 'gdelt']
          },
          NewsSectorRSS: {
            label: 'News Sector – RSS',
            descricao: 'Feed RSS/Atom setorial.',
            inputs: [
              { name: 'feed_url', label: 'URL do feed', type: 'text', required: true },
              { name: 'min_date_iso', label: 'Data mínima ISO', type: 'text' }
            ],
            output: 'Itens {title, url, published}',
            tags: ['news', 'sector', 'rss']
          },
          NewsCompanyRSS: {
            label: 'News Company – RSS',
            descricao: 'Feed RSS/Atom da empresa.',
            inputs: [
              { name: 'feed_url', label: 'URL do feed', type: 'text', required: true },
              { name: 'min_date_iso', label: 'Data mínima ISO', type: 'text' }
            ],
            output: 'Itens {title, url, published}',
            tags: ['news', 'company', 'rss']
          }
        }
      },
      reports: {
        label: 'General Reports',
        tools: {
          GeneralReportsWorldWDS: {
            label: 'Reports World – WDS',
            descricao: 'Relatórios do World Bank Documents.',
            inputs: [
              { name: 'start_year', label: 'Ano inicial', type: 'number', required: true },
              { name: 'end_year', label: 'Ano final', type: 'number', required: true },
              { name: 'q', label: 'Consulta', type: 'text' },
              { name: 'rows', label: 'Limite', type: 'number' }
            ],
            output: 'Docs {title, year, url, region, topics}',
            tags: ['reports', 'world', 'wds']
          },
          GeneralReportsSECEdgar: {
            label: 'Reports Sector – SEC EDGAR',
            descricao: 'Filings da SEC EDGAR.',
            inputs: [
              { name: 'cik', label: 'CIK', type: 'text', required: true },
              { name: 'accession_no', label: 'Accession', type: 'text' }
            ],
            output: 'JSON bruto de submissões ou filings da SEC',
            tags: ['reports', 'sector', 'sec']
          },
          GeneralReportsCVMDadosAbertos: {
            label: 'Reports Company – CVM',
            descricao: 'Datasets da CVM Dados Abertos.',
            inputs: [
              { name: 'path', label: 'Caminho do dataset', type: 'text', required: true }
            ],
            output: 'Linhas CSV em JSON (até 1000 itens)',
            tags: ['reports', 'company', 'cvm']
          }
        }
      }
    }
  }
};
