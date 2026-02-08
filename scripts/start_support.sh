#!/bin/bash
nohup /home/vostok/akira_system/venv/bin/python /home/vostok/akira_system/src/suporte_akira.py > /home/vostok/akira_system/logs/suporte.log 2>&1 &
echo "🎧 Akira Support Listener iniciado em Background (PID $!)"
