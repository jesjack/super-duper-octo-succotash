# TODO - Pruebas Sistema de Actualización USB

## 📋 Pruebas Pendientes

### ✅ Completadas
- [x] Creación de paquete de actualización (versión 1.0.7)
- [x] Descarga de dependencias (25 wheels)

### ⏳ Por Realizar

#### 1. Prueba de Detección USB
- [ ] Iniciar aplicación POS (versión 1.0.7)
- [ ] Verificar en consola: `USB Monitor iniciado (Versión actual: 1.0.7)`
- [ ] Conectar USB D: con carpeta `pos_update/`
- [ ] Verificar que aparece diálogo en 2-4 segundos
- [ ] **Resultado esperado**: Diálogo "Actualizando a versión 1.0.X..."

#### 2. Prueba de Actualización Completa (Misma Máquina)
- [ ] Modificar un archivo (ej: agregar comentario en `pos_app.py`)
- [ ] Crear nuevo paquete con `python build_update.py D:`
- [ ] Conectar USB mientras app está corriendo
- [ ] Esperar proceso de actualización
- [ ] Verificar "Puede retirar USB de forma segura"
- [ ] Click "Reiniciar Aplicación"
- [ ] **Resultado esperado**: 
  - Archivo modificado fue reemplazado (comentario desapareció)
  - Nueva versión en consola
  - App funciona correctamente

#### 3. Prueba de Respaldo
- [ ] Realizar una actualización
- [ ] Verificar carpeta `backups/`
- [ ] Verificar que existe carpeta con timestamp
- [ ] Verificar que contiene archivos originales
- [ ] **Resultado esperado**: Backup completo antes de actualizar

#### 4. Prueba de Preservación de Datos
- [ ] Agregar un producto de prueba a la base de datos
- [ ] Realizar actualización
- [ ] Verificar que producto sigue existiendo
- [ ] **Resultado esperado**: Base de datos NO fue sobrescrita

#### 5. Prueba de Dependencias
- [ ] Modificar versión en `requirements.txt` (ej: `flask==3.0.0` → `flask==3.1.0`)
- [ ] Crear paquete de actualización
- [ ] Ejecutar actualización
- [ ] Verificar nueva versión: `.venv\Scripts\python -m pip show flask`
- [ ] **Resultado esperado**: Dependencia actualizada correctamente

#### 6. Prueba en Máquina de Producción (SIN Internet)
- [ ] Copiar `D:\pos_update\` a USB física
- [ ] Llevar USB a máquina sin internet
- [ ] Conectar USB mientras POS está corriendo
- [ ] Verificar proceso completo de actualización
- [ ] **Resultado esperado**: Actualización exitosa sin conexión

#### 7. Prueba de Cierre Limpio
- [ ] Iniciar aplicación POS
- [ ] Verificar monitor USB activo
- [ ] Cerrar aplicación normalmente
- [ ] Verificar que no quedan procesos huérfanos
- [ ] **Resultado esperado**: Todos los threads terminan correctamente

---

## 🐛 Si Encuentras Problemas

### USB no se detecta
- Verificar nombre exacto de carpeta: `pos_update/` (minúsculas)
- Verificar que existe `update_info.json` dentro
- Revisar consola para mensajes del monitor

### Error instalando dependencias
- Verificar que todos los .whl están en `dependencies/`
- Verificar espacio en disco suficiente
- Revisar logs en consola

### App no se reinicia
- Verificar que `pos_app.py` está en directorio raíz
- Revisar permisos de ejecución

---

## 📝 Notas

- **Versión actual del sistema**: 1.0.7
- **Último paquete creado**: `D:\pos_update\` (versión 1.0.7)
- **Comando para crear paquete**: `python build_update.py D:`
