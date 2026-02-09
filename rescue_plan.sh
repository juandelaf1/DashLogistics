#!/bin/bash
# SCRIPT DE RESCATE - DashLogistics
# Este script guardará todo tu trabajo antes de reorganizar

echo "🚀 INICIANDO PLAN DE RESCATE DE DASHLOGISTICS"
echo "=============================================="
echo ""

# PASO 1: Crear backup de la rama actual
echo "📦 PASO 1: Creando backup de tu rama actual..."
git add -A
git commit -m "BACKUP: Guardando trabajo en advanced-analytics antes de reorganización - $(date +%Y-%m-%d)"
git push origin advanced-analytics

# PASO 2: Crear rama de backup adicional
echo ""
echo "🔒 PASO 2: Creando rama de backup de seguridad..."
BACKUP_BRANCH="backup-seguridad-$(date +%Y%m%d-%H%M%S)"
git checkout -b "$BACKUP_BRANCH"
git push origin "$BACKUP_BRANCH"

# PASO 3: Volver a advanced-analytics
echo ""
echo "🔄 PASO 3: Volviendo a advanced-analytics..."
git checkout advanced-analytics

echo ""
echo "✅ BACKUP COMPLETADO"
echo "===================="
echo ""
echo "📊 RESUMEN:"
echo "  - Trabajo guardado en: advanced-analytics"
echo "  - Backup de seguridad en: $BACKUP_BRANCH"
echo ""
echo "🎯 PRÓXIMOS PASOS:"
echo "  1. Revisar archivos locales vs GitHub"
echo "  2. Decidir qué mantener y qué eliminar"
echo "  3. Reorganizar estructura del proyecto"
echo ""
