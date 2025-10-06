import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from flask import current_app

def send_reset_email(recipient_email, reset_link):
    """Envía un correo para el reseteo de contraseña."""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Recuperación de Contraseña Evaluador"
        msg['From'] = current_app.config['GMAIL_USER']
        msg['To'] = recipient_email

        texto_plano = f"""
        ---IAsefimex - Evaluador de Credito---

        Has solicitado restablecer tu contraseña.\n
        Haz clic en el siguiente enlace para continuar.\n
        Es necesario recuerdes tu PIN para poder restablecer tu contraseña.
        Este enlace es valido por 15 minutos:\n\n{reset_link}\n\n

        Si no solicitaste esto, contacta a TI.
        https://172.30.1.108:5000
        
        https://asefimex.com
        
        Toda la informacion incluida en este correo electronico es informacion de uso exclusivamente interno de Asefimex
        """

        parte_texto = MIMEText(texto_plano, 'plain')
        msg.attach(parte_texto)

        # --- Parte HTML
        html_con_formato = f"""
        <html>
          <body>
            <h2>🤖 IAsefimex - Evaluador de Credito 💻</h2>
            <p>Has solicitado restablecer tu contraseña.</p>
            <p>Haz clic en el siguiente enlace para continuar.</p>
            <p>Es necesario recuerdes tu PIN para poder restablecer tu contraseña.</p>
            <p>Este enlace es valido por 15 minutos:</p>
            <p>
                <a href="{reset_link}" style="background-color: #4CAF50; color: white; padding: 14px 25px; text-align: center; text-decoration: none; display: inline-block; border-radius: 8px;">
                    <b>Restablecer Contraseña</b>
                </a>
            </p> 
            
            <p>Si no solicitaste esto, contacta a TI.</p>
            <a href="http://172.30.1.108:5000">Evauador IAsefimex<a>
            <br>
            <a href="https://asefimex.com">
                <img src="cid:logo_empresa" alt="Logo Pagina Asefimex">
            <a>
            <p style="font-size: 8px">Toda la informacion incluida en este correo electronico es informacion de uso exclusivamente interno de Asefimex</p>
          </body>
        </html>
        """
        parte_html = MIMEText(html_con_formato, 'html')
        msg.attach(parte_html)

        # --- ADJUNTAR IMAGEN
        try:
            with open('LogoAsefimexVF.png', 'rb') as f:
                imagen = MIMEImage(f.read())
                imagen.add_header('Content-ID', '<logo_empresa>')
                msg.attach(imagen)
        except FileNotFoundError:
            print("Advertencia: No se encontro la imagen para adjuntar.")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(current_app.config['GMAIL_USER'], current_app.config['GMAIL_PASSWORD'])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False
