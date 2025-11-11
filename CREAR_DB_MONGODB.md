# Crear Base de Datos MongoDB Atlas Manualmente

Como las escrituras están deshabilitadas temporalmente, la base de datos `emergent_etl` no se crea automáticamente. Puedes crearla manualmente usando uno de estos métodos:

## 🚀 Método 1: MongoDB Atlas Web UI (Más Fácil)

1. **Inicia sesión en MongoDB Atlas**: https://cloud.mongodb.com/
2. **Selecciona tu cluster**
3. **Haz clic en "Browse Collections"**
4. **Haz clic en el botón "+ Create Database"** (arriba a la izquierda)
5. **Ingresa:**
   - Database Name: `emergent_etl`
   - Collection Name: `sound_readings_clean` (puedes crear las demás después)
6. **Haz clic en "Create"**

### Crear las demás colecciones:

Después de crear la base de datos, crea las siguientes colecciones haciendo clic en "+ Create Collection":

- `sound_readings_clean`
- `distance_readings_clean`
- `air_readings_clean`
- `sound_predictions`
- `distance_predictions`
- `air_predictions`

## 🛠️ Método 2: Usando mongosh (Línea de Comandos)

1. **Abre una terminal**
2. **Conecta a MongoDB Atlas:**
   ```bash
   mongosh "<TU_MONGO_ATLAS_URI>"
   ```
   (Reemplaza con tu URI del archivo `.env`)

3. **Ejecuta el script:**
   ```bash
   mongosh "<TU_MONGO_ATLAS_URI>" < scripts/crear-db-mongodb.js
   ```

   O copia y pega el contenido del script directamente en mongosh.

## 📋 Método 3: Usando MongoDB Compass

1. **Descarga e instala** [MongoDB Compass](https://www.mongodb.com/products/compass)
2. **Conecta usando tu `MONGO_ATLAS_URI`**
3. **Crea la base de datos:**
   - Haz clic derecho en el cluster
   - Selecciona "Create Database"
   - Nombre: `emergent_etl`
   - Collection Name: `sound_readings_clean`
4. **Crea las demás colecciones** haciendo clic derecho en la base de datos y "Create Collection"

## ✅ Verificar que se Creó

Después de crear la base de datos, deberías verla en MongoDB Atlas:

1. **Refresca la página** de MongoDB Atlas
2. **Busca "emergent_etl"** en la lista de bases de datos
3. **Haz clic** para ver las colecciones

## 📝 Nota Importante

- **La base de datos aparecerá vacía** (0 documentos) hasta que se habiliten las escrituras
- **Las colecciones se crearán automáticamente** cuando Spark escriba el primer documento
- **Puedes crear las colecciones manualmente** para ver la estructura antes de que lleguen datos

## 🔄 Una Vez que se Habiliten las Escrituras

Cuando se resuelvan los errores y se habiliten las escrituras nuevamente:
1. Los datos comenzarán a escribirse automáticamente
2. Verás documentos apareciendo en las colecciones
3. No necesitas esperar 5 minutos - los datos se escriben en tiempo real

