import { TOOL_CATALOG } from './tools-config.js';

const targetSelect = document.getElementById('test-target');
const typeSection = document.getElementById('type-section');
const typeSelect = document.getElementById('tool-type');
const toolSection = document.getElementById('tool-section');
const toolSelect = document.getElementById('tool-name');
const infoSection = document.getElementById('tool-info');
const descEl = document.getElementById('tool-description');
const inputDescEl = document.getElementById('tool-input-desc');
const outputDescEl = document.getElementById('tool-output-desc');
const formEl = document.getElementById('tool-form');
const runBtn = document.getElementById('run-tool');
const outputEl = document.getElementById('tool-output');

function hide(el){ el.classList.add('hidden'); }
function show(el){ el.classList.remove('hidden'); }
function resetSelect(sel){ sel.innerHTML = '<option value="">-- selecione --</option>'; }

function populateTargets(){
  Object.entries(TOOL_CATALOG).forEach(([key, info]) => {
    const opt = document.createElement('option');
    opt.value = key;
    opt.textContent = info.label || key;
    targetSelect.appendChild(opt);
  });
}

populateTargets();

// Top-level selection

targetSelect.addEventListener('change', () => {
  resetSelect(typeSelect);
  resetSelect(toolSelect);
  hide(typeSection); hide(toolSection); hide(infoSection); hide(formEl); hide(runBtn); hide(outputEl);

  const target = targetSelect.value;
  if (!target) return;
  const types = TOOL_CATALOG[target].types || {};
  Object.entries(types).forEach(([key, info]) => {
    const opt = document.createElement('option');
    opt.value = key;
    opt.textContent = info.label || key;
    typeSelect.appendChild(opt);
  });
  show(typeSection);
});

// Tool type selection

typeSelect.addEventListener('change', () => {
  resetSelect(toolSelect);
  hide(toolSection); hide(infoSection); hide(formEl); hide(runBtn); hide(outputEl);
  const target = targetSelect.value;
  const type = typeSelect.value;
  if (!target || !type) return;
  const tools = TOOL_CATALOG[target].types[type].tools || {};
  Object.entries(tools).forEach(([key, info]) => {
    const opt = document.createElement('option');
    opt.value = key;
    opt.textContent = info.label || key;
    toolSelect.appendChild(opt);
  });
  show(toolSection);
});

// Tool selection

toolSelect.addEventListener('change', () => {
  hide(infoSection); hide(formEl); hide(runBtn); hide(outputEl);
  const target = targetSelect.value;
  const type = typeSelect.value;
  const toolName = toolSelect.value;
  if (!target || !type || !toolName) return;
  const tool = TOOL_CATALOG[target].types[type].tools[toolName];
  if (!tool) return;

  // Description and expected IO
  descEl.textContent = tool.descricao || '';
  inputDescEl.textContent = tool.inputs.map(i => `${i.name}${i.required ? '*' : ''} (${i.type})`).join('\n');
  outputDescEl.textContent = tool.output || '';
  show(infoSection);

  // Build form
  formEl.innerHTML = '';
  tool.inputs.forEach(inp => {
    const wrap = document.createElement('div');
    const label = document.createElement('label');
    label.textContent = inp.label || inp.name;
    label.setAttribute('for', `arg-${inp.name}`);
    const input = document.createElement('input');
    input.id = `arg-${inp.name}`;
    input.name = inp.name;
    input.type = inp.type || 'text';
    if (inp.required) input.required = true;
    wrap.appendChild(label);
    wrap.appendChild(input);
    formEl.appendChild(wrap);
  });
  show(formEl);
  show(runBtn);
});

// Run button

runBtn.addEventListener('click', async (ev) => {
  ev.preventDefault();
  hide(outputEl);

  const target = targetSelect.value;
  const type = typeSelect.value;
  const toolName = toolSelect.value;
  if (!target || !type || !toolName) return;

  const fd = new FormData(formEl);
  let hasFile = false;
  for (const [, v] of fd.entries()) {
    if (v instanceof File && v.size > 0) {
      hasFile = true; break;
    }
  }

  let body;
  let headers = {};
  if (hasFile) {
    body = fd;
  } else {
    body = JSON.stringify(Object.fromEntries(fd.entries()));
    headers['Content-Type'] = 'application/json';
  }

  outputEl.textContent = 'Executando...';
  show(outputEl);

  try {
    const resp = await fetch(`/debug/tool/${type}/${toolName}`, {
      method: 'POST',
      headers,
      body
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const ctype = resp.headers.get('Content-Type') || '';
    if (ctype.includes('application/json')) {
      const json = await resp.json();
      outputEl.textContent = JSON.stringify(json, null, 2);
    } else {
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      outputEl.innerHTML = '';
      const a = document.createElement('a');
      a.href = url;
      const disposition = resp.headers.get('Content-Disposition');
      const match = disposition && disposition.match(/filename="?([^";]+)"?/);
      a.download = match ? match[1] : 'download';
      a.textContent = 'Download';
      outputEl.appendChild(a);
    }
  } catch (err) {
    outputEl.textContent = `Erro: ${err.message}`;
  }
});

console.log('Menu de Teste carregado');
