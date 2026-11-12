# Stitch

Framework modular de análisis web pasivo para pruebas de seguridad autorizadas.

`stitch` permite recorrer páginas dentro de un ámbito definido, revisar cabeceras HTTP,
identificar indicios de tecnologías y consultar el certificado TLS. Esta distribución
se centra en reconocimiento no intrusivo: no envía payloads de explotación, no intenta
eludir controles y no ejecuta pruebas de inyección.

## Uso autorizado

Utiliza esta herramienta únicamente en sistemas propios o para los que tengas permiso
expreso. Respeta siempre el alcance, las condiciones y la ventana de pruebas autorizadas.

Para practicar, utiliza laboratorios locales como OWASP Juice Shop o DVWA y sigue sus
instrucciones oficiales.

## Requisitos

- Python 3.11 o superior
- pip
- Git (para publicar el proyecto)
- Dependencias Python indicadas en `requirements.txt`

## Instalación

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

Si PowerShell impide activar el entorno, puedes ejecutar directamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Verificación

```bash
python stitch.py --version
```

## Ejemplos

Reconocimiento pasivo de un sitio propio:

```bash
python stitch.py -u https://example.com --scope example.com --recon
```

Recorrido limitado de páginas dentro del mismo ámbito:

```bash
python stitch.py -u https://example.com --scope example.com --crawl --max-pages 30
```

Guardar resultados en JSON:

```bash
python stitch.py -u https://example.com --scope example.com --recon --report report.json
```

## Funciones

- Comprobación de cabeceras HTTP habituales: HSTS, CSP, X-Frame-Options,
  X-Content-Type-Options, Referrer-Policy y Permissions-Policy.
- Identificación orientativa de tecnologías a partir de respuestas públicas.
- Consulta del certificado TLS del host.
- Rastreo limitado de enlaces HTML dentro del host y ámbito configurados.
- Exportación de resultados JSON.

Los resultados de identificación tecnológica son indicios, no una confirmación.
El rastreador realiza solicitudes GET normales y respeta el límite de páginas y el timeout.

## Estructura

```text
Stitchrep/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── stitch.py
├── setup_windows.ps1
├── publish_github.ps1
├── examples/
│   └── targets.md
└── scripts/
    └── check_project.ps1
```

## Publicar en GitHub

1. Crea el repositorio `Stitchrep` en tu cuenta de GitHub si todavía no existe.
2. Abre PowerShell dentro de esta carpeta.
3. Ejecuta:

```powershell
.\publish_github.ps1
```

El script configura el remoto indicado en el documento original
(`https://github.com/gfiuws19832/Stitchrep.git`), prepara el commit y ejecuta `git push`.
Si ese repositorio no es tuyo, cambia `$RemoteUrl` al URL de tu repositorio antes de
ejecutarlo. Git puede pedirte autenticarte mediante el navegador.

El script no fuerza cambios ni sobrescribe el historial remoto. Si GitHub ya tiene
commits que no están en tu copia local, resuelve primero esa sincronización.

## Licencia

MIT. Consulta `LICENSE`.
