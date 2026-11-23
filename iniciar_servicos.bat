@echo off
REM Abre 4 janelas, uma para cada servico (alternativa ao VS Code).
for %%P in (servico_produtos servico_clientes servico_vendedores servico_vendas) do (
  start "%%P" cmd /k "cd /d %~dp0%%P && py app.py"
)
