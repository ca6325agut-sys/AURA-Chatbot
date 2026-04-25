import streamlit as st
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import base64
import os
from datetime import datetime
# Agrégalo arriba de todo para que el programa siempre sepa qué es df_citas
df_citas = pd.DataFrame()

# Define esto aquí arriba para que sea fácil de editar luego
docentes_lista = ["Ana Gómez (Matemáticas)", "Luis Pérez (Coordinador)", "Marta Ruiz (Lenguaje)"]
horas_disponibles = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00"]
# --- SECCIÓN DE CONTACTO EN LA BARRA LATERAL ---
with st.sidebar:
    st.divider()
    with st.expander("📞 ¡Contáctanos!", expanded=False):
        st.write("**Atención inmediata:**")
        st.write("📲 [312 456 7890](https://wa.me/573124567890)")
        st.write("📧 [soporte@aura-segura.edu.co](mailto:soporte@aura-segura.edu.co)")
        
        st.write("---")
        st.write("**Nuestras Redes Sociales:**")
        
        # Iconos y enlaces simbólicos
        st.markdown("""
        🔵 [Facebook - Aura Segura](https://facebook.com)  
        📸 [Instagram - @AuraSegura](https://instagram.com)  
        🎵 [TikTok - @AuraSegura_Edu](https://tiktok.com)
        """)
        st.caption("Horario de atención: Lun - Vie (7am - 4pm)")

# --- FUNCIÓN DE CARGA SEGURA ---
def cargar_imagen_base64(nombre_archivo):
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# --- CARGA CON EL NOMBRE REAL DETECTADO ---
# Intentamos primero con el nombre que aparece en tu explorador de archivos
img_base64 = cargar_imagen_base64("image_7.png.jpeg")

# Si por alguna razón lo renombras después, estas líneas sirven de respaldo:
if not img_base64:
    img_base64 = cargar_imagen_base64("image_7.png")
if not img_base64:
    img_base64 = cargar_imagen_base64("image_7.jpg")

# 1. CONFIGURACIÓN E INTERFAZ
st.set_page_config(page_title="AURA - Sistema Académico", page_icon="🤖", layout="wide")
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# --- ENCABEZADO UNIFICADO Y ESTILIZADO (MÁXIMA VISIBILIDAD) ---
st.markdown(f"""
    <style>
    /* 1. Unificamos el fondo de toda la tarjeta en blanco puro */
    .hero-card {{
        background-color: #FFFFFF;
        padding: 0px; /* Importante: 0 padding */
        border-radius: 24px;
        display: flex;
        align-items: stretch; /* Estira las columnas a la misma altura */
        justify-content: space-between;
        border: 1px solid #F0F2F6;
        margin-bottom: 25px;
        overflow: hidden; /* Corta cualquier sobrante de la imagen */
        box-shadow: 0 10px 25px rgba(0,0,0,0.03); /* Sombra suave */
    }}

    /* 2. Columna de Texto - Limpia y centrada */
    .text-container {{
        flex: 1.4; /* Proporción ideal para texto */
        padding: 45px 50px; /* Relleno generoso y limpio */
        display: flex;
        flex-direction: column;
        justify-content: center;
        background-color: #FFFFFF; /* Fondo blanco explícito */
    }}

    /* 3. Columna de Imagen - ELIMINAMOS EL FONDO GRIS */
    .image-container {{
        flex: 1; /* Proporción para la imagen */
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #FFFFFF; /* FONDO BLANCO PURO AHORA */
        margin: 0px;
        padding: 0px;
        position: relative; /* Para control fino de posición */
    }}

    /* 4. Estilo de la Imagen - AJUSTE TOTAL */
    .hero-img {{
        width: 100%;
        height: 100%;
        object-fit: cover; /* Fuerza a la imagen a cubrir TODO el espacio sin deformarse */
        display: block; /* Elimina espacio fantasma inferior */
    }}

    /* 5. Tipografía Estilizada */
    .aura-title {{
        font-family: 'Inter', sans-serif;
        font-size: 85px; /* Más grande y visible */
        font-weight: 900;
        color: #1E3A8A;
        line-height: 0.9; /* Pegado para impacto visual */
        margin: 5px 0 15px 0;
        letter-spacing: -4px; /* Letras juntas estilo AI moderna */
    }}
    </style>

    <div class="hero-card">
        <div class="text-container">
            <p style="font-size: 20px; margin:0; font-weight:700; color: #1E3A8A;">¡Hola! Soy</p>
            <h1 class="aura-title">AURA</h1>
            <p style="color: #4B5563; font-size: 19px; margin-top: 5px; line-height: 1.3;">
                Tu Asistente Virtual para la Comunidad Educativa de <b>Cundinamarca y Boyacá</b>
            </p>
            <div style="background:#DBEAFE; color:#1E40AF; padding:8px 18px; border-radius:10px; display:inline-block; font-size:14px; font-weight:bold; margin-top:20px;">
                Agente de Utilidad para el Rendimiento Académico
            </div>
        </div>
        <div class="image-container">
            {"<img src='data:image/jpeg;base64," + img_base64 + "' class='hero-img'>" if img_base64 else "🖼️"}
        </div>
    </div>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS (Corregida)
@st.cache_data
def cargar_bases_datos():
    df_col, df_user = None, None
    try:
        # Usamos 'Colegios.xlsx' para ambas cosas ya que ahí están los usuarios
        if os.path.exists('Colegios.xlsx'):
            # Cargamos la base general
            df_col = pd.read_excel('Colegios.xlsx', engine='openpyxl')
            df_col.columns = df_col.columns.str.strip() 
            
            # Definimos df_user como el mismo archivo
            df_user = df_col.copy()
            
            # Normalización de ID y Contraseña para comparación segura
            # Usamos .replace('.0', '') por si Excel lee los IDs como números flotantes
            df_user['ID_NORMAL'] = df_user['ID Alumno'].astype(str).str.replace('.0', '', regex=False).str.strip()
            df_user['PASS_NORMAL'] = df_user['contraseña'].astype(str).str.replace('.0', '', regex=False).str.strip()
            df_user['ACUDIENTE_NAME'] = df_user['Acudiente'].astype(str).str.strip()
            df_user['ESTUDIANTE_NAME'] = df_user['Estudiante'].astype(str).str.strip()
            
            return df_col, df_user
        else:
            st.error("No se encontró el archivo 'Colegios.xlsx'. Asegúrate de que el nombre sea exacto.")
            return None, None
            
    except Exception as e:
        st.error(f"Error técnico al leer el Excel: {e}")
        return None, None

df_col, df_user = cargar_bases_datos()

# 3. ESTADOS DE SESIÓN
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None
if "materia_experta" not in st.session_state: st.session_state.materia_experta = None
if "etapa_matricula" not in st.session_state: st.session_state.etapa_matricula = 0
if "chat_bullying" not in st.session_state:
    st.session_state.chat_bullying = [{"role": "assistant", "content": "Hola, soy AURA. Este es un espacio seguro y privado. ¿Quieres contarme qué está pasando?"}]
if "bullying_interactuado" not in st.session_state: st.session_state.bullying_interactuado = False

# 4. MENÚ LATERAL (Sidebar con robot)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
    st.title("Menú Principal")
    seleccion = st.radio("Ir a:", ["Inicio / Chat General", "1. Padres/Acudientes", "2. Aprende con AURA", "3. Espacio Seguro","4. Docentes/Administrativos"])
    
    if st.session_state.logged_in:
        st.divider()
        st.write(f"👤 Bienvenido/a: **{st.session_state.user_data['ACUDIENTE_NAME']}**")
        if st.button("🔴 Cerrar Sesión"):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.session_state.etapa_matricula = 0
            st.rerun()

# --- SECCIÓN 1: PADRES / ACUDIENTES CORREGIDA ---
docentes = [
    {"id": 1, "nombre": "Ana Gómez", "rol": "Matemáticas"},
    {"id": 2, "nombre": "Luis Pérez", "rol": "Coordinador"},
    {"id": 3, "nombre": "Marta Ruiz", "rol": "Lenguaje"},
]
horas_disponibles = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00"]
df_citas = pd.DataFrame() # Esto crea una tabla vacía por defecto
if seleccion == "1. Padres/Acudientes":
    # 1. LÓGICA DE LOGIN
    if not st.session_state.logged_in:
        st.subheader("🔐 Área Privada de Padres y Acudientes")
        with st.form("login_aura"):
            u = st.text_input("ID de Alumno").strip()
            p = st.text_input("Contraseña", type="password").strip()
            submit = st.form_submit_button("Ingresar")
            
            if submit:
                if df_user is not None:
                    match = df_user[(df_user['ID_NORMAL'] == u) & (df_user['PASS_NORMAL'] == p)]
                    if not match.empty:
                        st.session_state.logged_in = True
                        st.session_state.user_data = match.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("ID de Alumno o contraseña incorrectos.")
                else:
                    st.error("Error: Base de datos de usuarios no encontrada.")
    
    # 2. CONTENIDO PROTEGIDO (Solo entra aquí si ya se logueó)
    else:
        st.info(f"Bienvenido/a {st.session_state.user_data['ACUDIENTE_NAME']}")
        
        # Aquí unificamos el nombre a 'opcion_menu'
        opcion_menu = st.selectbox("Seleccione una funcionalidad:", 
                                  ["Seleccione...", 
                                   "Matricula online", 
                                   "Certificados", 
                                   "Reportes de asistencia", 
                                   "Estado de matricula", 
                                   "Comunicados institucionales",
                                   "Agendar Cita / Acompañamiento"])

        # --- FUNCIONALIDAD: MATRÍCULA ONLINE (7 ETAPAS) ---
        if opcion_menu == "Matricula online":
            st.markdown("### 📝 Módulo de Matrícula Online")
            
            # ETAPA 1: BIENVENIDA
            if st.session_state.etapa_matricula == 0:
                st.markdown("#### PRIMERA ETAPA — BIENVENIDA Y VALIDACIÓN")
                st.write("“Bienvenido al módulo de Matrícula Online. Aquí podrás realizar el proceso de inscripción y matrícula de manera rápida, segura”")
                tipo_est = st.radio("¿La matrícula es para un estudiante nuevo o antiguo?", ["Estudiante nuevo", "Estudiante antiguo"])
                if st.button("Continuar"):
                    if tipo_est == "Estudiante antiguo":
                        st.success("Acceso permitido para actualización de datos y renovación de matrícula.")
                    else:
                        st.session_state.etapa_matricula = 1
                        st.rerun()

            # ETAPA 2: DATOS DEL ESTUDIANTE
            elif st.session_state.etapa_matricula == 1:
                st.write("#### SEGUNDA ETAPA — DATOS DEL ESTUDIANTE")
                with st.form("f_etapa2"):
                    col1, col2 = st.columns(2)
                    nombres = col1.text_input("Nombres completos")
                    apellidos = col2.text_input("Apellidos completos")
                    t_doc = st.selectbox("Tipo de documento", ["Registro civil", "Tarjeta de identidad", "Cédula de extranjería", "PPT"])
                    n_doc = st.text_input("Número de documento")
                    f_nac = st.date_input("Fecha de nacimiento")
                    eps = st.text_input("EPS")
                    grado = st.text_input("Grado al que aspira ingresar")
                    # (Puedes agregar aquí el resto de campos: Municipio, sexo, etc.)
                    if st.form_submit_button("Siguiente: Datos del Acudiente"):
                        if nombres and n_doc:
                            st.session_state.etapa_matricula = 2
                            st.rerun()
                        else: st.error("Complete los campos obligatorios.")

            # ETAPA 3: DATOS DEL ACUDIENTE
            elif st.session_state.etapa_matricula == 2:
                st.write("#### TERCERA ETAPA — DATOS DEL PADRE, MADRE O ACUDIENTE")
                with st.form("f_etapa3"):
                    st.text_input("Nombre completo del acudiente", value=st.session_state.user_data['ACUDIENTE_NAME'])
                    st.text_input("Parentesco")
                    st.text_input("Número de celular")
                    st.text_input("Correo electrónico")
                    st.text_input("Persona autorizada para recoger al menor")
                    if st.form_submit_button("Siguiente: Cargue de Documentos"):
                        st.session_state.etapa_matricula = 3
                        st.rerun()

            # ETAPA 4: CARGUE DE DOCUMENTOS (SIMULACIÓN DRAG AND DROP)
            elif st.session_state.etapa_matricula == 3:
                st.write("#### CUARTA ETAPA — CARGUE DE DOCUMENTOS")
                docs = ["Registro civil del estudiante", "Documento de identidad del acudiente", "Certificado de afiliación EPS"]
                for d in docs:
                    f = st.file_uploader(f"Subir {d} (PDF, JPG, PNG)", type=['pdf', 'jpg', 'png'])
                    if f: st.success(f"“{d} cargado correctamente”")
                
                if st.button("Siguiente: Validación Inteligente"):
                    st.session_state.etapa_matricula = 4
                    st.rerun()

            # ETAPA 5: VALIDACIÓN AUTOMÁTICA
            elif st.session_state.etapa_matricula == 4:
                st.write("#### QUINTA ETAPA — VALIDACIÓN AUTOMÁTICA")
                with st.spinner("Simulando validación IA..."):
                    st.warning("“Hemos detectado que falta adjuntar el certificado de afiliación EPS. Por favor súbelo para continuar.”")
                    if st.button("Simular corrección y continuar"):
                        st.session_state.etapa_matricula = 5
                        st.rerun()

            # ETAPA 6: RESUMEN
            elif st.session_state.etapa_matricula == 5:
                st.write("#### SEXTA ETAPA — RESUMEN DE MATRÍCULA")
                st.markdown(f"""
                - **Estudiante:** En proceso de registro
                - **Acudiente:** {st.session_state.user_data['ACUDIENTE_NAME']}
                - **Documentos:** 3 de 3 validados
                """)
                st.write("“¿Desea confirmar y enviar la solicitud de matrícula?”")
                c1, c2 = st.columns(2)
                if c1.button("Sí, confirmar"):
                    st.session_state.etapa_matricula = 6
                    st.rerun()
                if c2.button("Editar información"):
                    st.session_state.etapa_matricula = 1
                    st.rerun()

            # ETAPA 7: CONFIRMACIÓN FINAL
            elif st.session_state.etapa_matricula == 6:
                st.success("#### SÉPTIMA ETAPA — CONFIRMACIÓN FINAL")
                st.balloons()
                st.write("“Tu solicitud de matrícula ha sido registrada exitosamente. Número de radicado: **MAT-2026-00125**”")
                st.write("Estado inicial: **En revisión**")
                st.button("Descargar comprobante PDF")
                if st.button("Regresar al menú"):
                    st.session_state.etapa_matricula = 0
                    st.rerun()

        # --- FUNCIONALIDAD: CERTIFICADOS ---
        elif opcion_menu == "Certificados":
            st.subheader("📜 Menú de Certificados")
            cert_tipo = st.selectbox("Seleccione el certificado que requiere:", 
                                     ["Paz y Salvo", "Certificado de notas", "Constancia de matricula", "Certificado de buena conducta", "Constancia de estudio"])
            
            with st.form("form_certificados"):
                colegio = st.text_input("Nombre del colegio")
                estudiante_nom = st.text_input("Nombre del estudiante", value="", placeholder="Escriba el nombre completo")
                correo_envio = st.text_input("Correo electrónico")
                
                if st.form_submit_button("Guardar"):
                    if colegio and estudiante_nom and correo_envio:
                        # 1. PREPARAR LA FILA PARA TU EXCEL (Solicitudes.xlsx)
                        nueva_solicitud = {
                            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Remitente": st.session_state.user_data.get('ACUDIENTE_NAME', 'Acudiente'),
                            "Documento/ID": st.session_state.user_data.get('ID_NORMAL', 'N/A'),
                            "Tipo de tramite": f"SOLICITUD: {cert_tipo}", # Aquí guarda si es Paz y Salvo, Notas, etc.
                            "Descripción": f"Colegio: {colegio} | Enviar a: {correo_envio} | Estudiante: {estudiante_nom}",
                            "Estado": "En revisión"
                        }
                        
                        # 2. LÓGICA DE GUARDADO EN EL ARCHIVO EXISTENTE
                        archivo_sol = "Solicitudes.xlsx"
                        try:
                            if os.path.exists(archivo_sol):
                                df_ex = pd.read_excel(archivo_sol)
                                df_final = pd.concat([df_ex, pd.DataFrame([nueva_solicitud])], ignore_index=True)
                            else:
                                df_final = pd.DataFrame([nueva_solicitud])
                            
                            df_final.to_excel(archivo_sol, index=False)
                            st.success("✅ ¡Hecho! Estamos evaluando tu solicitud con el colegio, te compartiremos la información al correo indicado.")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Error al guardar en el Excel: {e}. Asegúrate de cerrar el archivo si lo tienes abierto.")
                    else:
                        st.warning("Por favor, completa todos los campos del formulario.")  
        # --- OPCIÓN: CITAS (CORREGIDA) ---
        elif opcion_menu == "Agendar Cita / Acompañamiento":
            st.subheader("📅 Citas y Acompañamiento")
            
            col1, col2 = st.columns([1, 1.5])
            
            with col1:
                fecha_sel = st.date_input("1. Selecciona la fecha:", min_value=datetime.now())
                docente_sel = st.selectbox("2. Selecciona el docente:", [d["nombre"] for d in docentes])
                
                # Lógica de filtrado de horas
                archivo_sol = "solicitudes.xlsx"
                horas_libres = horas_disponibles.copy()
                
                if os.path.exists(archivo_sol):
                    df_citas = pd.read_excel(archivo_sol)
                # Verificamos que la columna exista para no dar error
                if 'Tipo de tramite' in df_citas.columns:
                    fecha_str = str(fecha_sel)
                    # Buscamos citas agendadas para este docente y fecha
                    # Filtramos en la columna Descripción que es donde guardas todo
                    ocupadas = df_citas[
                        (df_citas['Tipo de tramite'] == "CITA AGENDADA") & 
                        (df_citas['Descripción'].str.contains(docente_sel, na=False)) & 
                        (df_citas['Descripción'].str.contains(fecha_str, na=False))
                    ]
                    
                    # Extraemos las horas que ya están ocupadas
                    horas_ocupadas = []
                    for desc in ocupadas['Descripción']:
                        for h in horas_disponibles:
                            if h in str(desc):
                                horas_ocupadas.append(h)
                    
                    horas_libres = [h for h in horas_disponibles if h not in horas_ocupadas]
                else:
                    horas_libres = horas_disponibles.copy()
                    ['Hora Cita'].tolist()
                    horas_libres = [h for h in horas_disponibles if h not in ocupadas]

            with col2:
                with st.form("form_citas"):
                    estudiante = st.text_input("Nombre del Estudiante", value=st.session_state.user_data.get('ESTUDIANTE_NAME', ''))
                    tipo_cita = st.selectbox("Tipo de cita", ["Académico", "Comportamiento"])
                    hora_sel = st.selectbox("Selecciona una hora disponible", horas_libres if horas_libres else ["Sin cupos"])
                    motivo = st.text_area("Motivo de la cita")
                    
                    if st.form_submit_button("Agendar Cita"):
                        if not horas_libres:
                            st.error("No hay turnos para este docente en la fecha seleccionada.")
                        elif estudiante and motivo:
                            nueva_cita = {  
                                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Remitente": st.session_state.user_data.get('ACUDIENTE_NAME', 'Acudiente'),
                            "Documento/ID": st.session_state.user_data.get('ID_NORMAL', 'N/A'),
                            "Tipo de tramite": "CITA AGENDADA",
                            "Descripción": f"Estudiante: {estudiante} | Docente: {docente_sel} | Fecha: {fecha_sel} | Hora: {hora_sel} | Motivo: {motivo}",
                            "Estado": "Programada"}
                           # 2. LÓGICA DE GUARDADO
                        archivo_sol = "Solicitudes.xlsx"
                        
                        try:
                            if os.path.exists(archivo_sol):
                                df_ex = pd.read_excel(archivo_sol)
                                df_final = pd.concat([df_ex, pd.DataFrame([nueva_cita])], ignore_index=True)
                            else:
                                df_final = pd.DataFrame([nueva_cita])
                            
                            # Guardar los cambios
                            df_final.to_excel(archivo_sol, index=False)
                            st.success(f"✅ Cita registrada en Solicitudes.xlsx para el {fecha_sel} a las {hora_sel}")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Error al guardar: {e}. Asegúrate de que el archivo Excel esté cerrado.")
                    else:
                        st.warning("Por favor completa el nombre del estudiante y el motivo.")

# --- SECCIÓN 2: APRENDE CON AURA (Materias por Grado) ---
elif seleccion == "2. Aprende con AURA":
    st.subheader("📚 Aula Virtual")
    grado = st.number_input("Ingresa tu grado (1-11):", min_value=1, max_value=11, value=1)
    
    # Lógica de materias solicitada
    m_basicas = ["Matemáticas", "Español", "Ciencias Naturales", "Ciencias Sociales", "Inglés", "Artes"]
    m_superiores = m_basicas + ["Física", "Química", "Trigonometría", "Filosofía", "Economía", "Cálculo"]
    
    materias_disponibles = m_superiores if grado >= 9 else m_basicas
    m_sel = st.selectbox("Selecciona la materia:", materias_disponibles)
    
    if st.button(f"Activar AURA experta en {m_sel}"):
        st.session_state.materia_experta = m_sel
        st.session_state.messages = [{"role": "assistant", "content": f"**Modo Experto en {m_sel} activado.** ¿Qué tema de grado {grado} quieres revisar?"}]
        st.rerun()

# --- SECCIÓN 3: APOYO PSICOLÓGICO Y DENUNCIA (AURA AMIGO CONFIDENTE) ---
elif seleccion == "3. Espacio Seguro":
    st.subheader("🤝 AURA: Tu espacio seguro")
    
    opc_espacio = st.sidebar.selectbox("Opciones del Espacio Seguro", ["Chat de Orientación", "Solicitudes recibidas"])

    if opc_espacio == "Chat de Orientación":
        # 1. Estados iniciales
        if "bullying_step" not in st.session_state: st.session_state.bullying_step = "conversando"
        if "mensajes_bullying" not in st.session_state:
            st.session_state.mensajes_bullying = [{"role": "assistant", "content": "Hola... soy AURA. Me doy cuenta de que algo te inquieta. Aquí puedes soltar todo lo que sientes, no te voy a juzgar. ¿Qué tienes en tu corazón hoy?"}]

        # 2. Historial siempre visible
        for m in st.session_state.mensajes_bullying:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        # --- PASO A: CONVERSACIÓN PSICOLÓGICA ---
        if st.session_state.bullying_step == "conversando":
            if p_bull := st.chat_input("Desahógate aquí..."):
                st.session_state.mensajes_bullying.append({"role": "user", "content": p_bull})
                
                # Lógica de detección de frases de "alivio" o "finalización"
                frases_alivio = ["gracias", "mejor", "ayudó", "tranquilo", "tranquila", "bien"]
                usuario_dijo_alivio = any(palabra in p_bull.lower() for palabra in frases_alivio)

                with st.chat_message("assistant"):
                    # SYSTEM PROMPT MUCHO MÁS PROFESIONAL
                    sys_psicologa = """Eres una psicóloga clínica experta en trauma infantil y juvenil. 
                    Tu tono es cálido, pausado y profundamente empático. 
                    REGLAS:
                    1. No des consejos genéricos. Valida sus emociones (ej. 'Es normal sentir miedo cuando eso pasa').
                    2. Haz preguntas que lo inviten a profundizar: '¿Desde cuándo te sientes así?', '¿Hay alguien en quien confíes?'.
                    3. Solo si el usuario dice que se siente 'mejor', 'agradecido' o si ya desahogó el problema principal, 
                       debes sugerir que para que esto no vuelva a pasar, se puede reportar de forma anónima.
                    4. Cuando decidas sugerir el reporte, DEBES terminar tu respuesta con el código: [ACTIVAR_REPORTE]"""
                    
                    # Forzamos a la IA si detectamos alivio manualmente en el código
                    if usuario_dijo_alivio:
                        p_bull += " (El usuario parece más tranquilo ahora. Es momento de sugerir el reporte anónimo)"

                    r = client.chat.completions.create(
                        model="gpt-4o", 
                        messages=[{"role":"system","content":sys_psicologa}] + st.session_state.mensajes_bullying
                    )
                    txt_respuesta = r.choices[0].message.content
                    
                    # Detección del trigger
                    if "[ACTIVAR_REPORTE]" in txt_respuesta:
                        st.session_state.bullying_step = "consentimiento"
                        txt_respuesta = txt_respuesta.replace("[ACTIVAR_REPORTE]", "").strip()
                    
                    st.session_state.mensajes_bullying.append({"role": "assistant", "content": txt_respuesta})
                    st.rerun()

        # --- PASO B: CONSENTIMIENTO (Se activa por trigger o por flujo) ---
        if st.session_state.bullying_step == "consentimiento":
            st.divider()
            st.info("✨ **AURA te escucha:** Me alegra que te sientas un poco mejor hablando. Para que podamos ayudarte a que esto cambie realmente, ¿te gustaría que enviemos un reporte anónimo a tus profesores?")
            c1, c2 = st.columns(2)
            if c1.button("✅ Sí, por favor"):
                st.session_state.bullying_step = "recopilando_datos"
                st.rerun()
            if c2.button("❌ No, solo quería hablar"):
                st.session_state.bullying_step = "conversando"
                st.success("Está bien, aquí estaré siempre que necesites desahogarte.")
                # Limpiamos para evitar bucle
                st.rerun()

        # --- PASO C: FORMULARIO DE DENUNCIA ---
        if st.session_state.bullying_step == "recopilando_datos":
            with st.form("form_denuncia_aura"):
                st.write("### 📝 Reporte Confidencial")
                colegio = st.text_input("Tu institución")
                desc = st.text_area("Cuéntame brevemente qué sucedió (sin nombres si prefieres)")
                if st.form_submit_button("Enviar a Directivas"):
                    # Lógica de guardado en Excel
                    st.session_state.bullying_step = "finalizado"
                    st.rerun()

        # --- PASO D: CIERRE ---
        if st.session_state.bullying_step == "finalizado":
            st.success("Tu valentía es increíble. El reporte ha sido enviado. Todo va a estar bien.")
            if st.button("Volver a hablar con AURA"):
                st.session_state.bullying_step = "conversando"
                st.rerun()
# OPCIÓN 4: DOCENTES / ADMINISTRATIVOS (EL NUEVO MÓDULO)
elif seleccion == "4. Docentes/Administrativos":
    if not st.session_state.logged_in:
        st.subheader("🔐 Acceso para Docentes y Administrativos")
        with st.form("login_docentes"):
            u = st.text_input("Usuario (ID)").strip()
            p = st.text_input("Contraseña", type="password").strip()
            if st.form_submit_button("Ingresar al Panel"):
                match = df_user[(df_user['ID_NORMAL'] == u) & (df_user['PASS_NORMAL'] == p)]
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_data = match.iloc[0].to_dict()
                    st.rerun()
                else: st.error("Credenciales no válidas")
    else:
        st.success(f"Panel Administrativo - {st.session_state.user_data['Institución Educativa']}")
        opc_adm = st.selectbox("Seleccione gestión:", ["Seleccione...", "Reportes", "Solicitudes Recibidas"])
        
        if opc_adm == "Reportes":
            st.subheader("📊 Reportes y Estadísticas")
            col1, col2 = st.columns(2)
            col1.metric("Total Alumnos", len(df_user))
            col2.metric("Sede", "Principal")
            st.write("### Listado de Control Académico")
            st.dataframe(df_user[['Estudiante', 'Fecha entrega boletines', 'Cuenta con servicio de restaurante']])
        elif opc_adm == "Solicitudes Recibidas":
            st.subheader("📩 Bandeja de Solicitudes Recibidas")
            archivo_sol = "Solicitudes.xlsx"

            # Verificamos si el archivo existe antes de hacer nada
            if os.path.exists(archivo_sol):
                # LEEMOS EL ARCHIVO AQUÍ (Esto define df_citas localmente)
                df_citas = pd.read_excel(archivo_sol)
                
                if not df_citas.empty:
                    # Mostramos la tabla al administrativo
                    st.dataframe(df_citas, use_container_width=True)
                    
                    st.divider()
                    st.subheader("🛠️ Gestionar Solicitud")
                    
                    # El usuario elige qué fila quiere cambiar
                    fila_idx = st.number_input("Seleccione el índice de la fila a gestionar:", 
                                               min_value=0, max_value=len(df_citas)-1, step=1)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Enviar / Aprobar"):
                            # Accedemos a df_citas que definimos arriba
                            df_citas.at[fila_idx, 'Estado'] = "Enviado / Aprobado"
                            df_citas.to_excel(archivo_sol, index=False)
                            st.success(f"Fila {fila_idx} actualizada con éxito.")
                            st.rerun() # Recarga para ver el cambio
                            
                    with col2:
                        if st.button("❌ Rechazar"):
                            df_citas.at[fila_idx, 'Estado'] = "Rechazado"
                            df_citas.to_excel(archivo_sol, index=False)
                            st.error(f"Fila {fila_idx} ha sido rechazada.")
                            st.rerun()
                else:
                    st.info("El archivo está vacío. No hay solicitudes que mostrar.")
            else:
                st.warning("Aún no se ha creado el archivo 'Solicitudes.xlsx'.")
# CHAT GENERAL (INICIO)
elif seleccion == "Inicio / Chat General":
    st.subheader("🤖 Chat con AURA")
    # Lógica de chat general...

# --- MOTOR DE CHAT GENERAL ---
if seleccion != "3. Denuncia el bullying":
    st.divider()
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if prompt := st.chat_input("Consulta general..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            sys = f"Eres AURA experta en {st.session_state.materia_experta}" if st.session_state.materia_experta else "Eres AURA asistente."
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role":"system","content":sys}]+st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()
