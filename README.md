# Sistema de Gestión de Requerimientos - Pomalca

Proyecto web desarrollado con Flask y MySQL para la gestión de requerimientos internos y control de maquinaria.

## Tecnologías

- Python
- Flask
- MySQL
- PyMySQL
- HTML
- CSS

## Instalación del proyecto

### 1. Clonar el repositorio

```terminal
git clone URL_DEL_REPOSITORIO
```

### 2. Entrar a la carpeta del proyecto

```terminal
cd Pry-DAW-Grupo-2
```

### 3. Crear entorno virtual

```terminal
# opcion 1 
python -3 venv .venv
#opcion 2
py -3 venv .venv 
#opcion 3`
python -m venv .venv

### 4. Activar entorno virtual

```terminal
.venv\Scripts\activate
```

### 5. Instalar dependencias
```terminal
pip install -r requirements.txt
```

### 6. Crear la base de datos

Abrir phpMyAdmin y ejecutar el archivo:

```text
script.sql
```

### 7. Ejecutar el proyecto

```terminal
flask --app main run --debug
```