import requests
from bs4 import BeautifulSoup

# Methods for scraping student data from the UNMSM website
def _normalize_name(name: str) -> str:
    """
    Normalizes a name by converting it to lowercase and capitalizing the first letter of each word.
    """
    monosyllables = ['de', 'e', 'y', 'a', 'o', 'u']

    if not name:
        return ''

    capitalized = name.lower().title()  # Capitaliza la primera letra de cada palabra

    # Lowercase monosyllables
    capitalized = ' '.join(
        word if word.lower() in monosyllables else word.capitalize()
        for word in capitalized.split()
    )

    return capitalized

def _parse_alumno(html: str, base_url: str) -> dict:
    """
    Parses the student data from the HTML response.
    """
    soup = BeautifulSoup(html, 'html.parser')

    faculty = _normalize_name(
        soup.find('input', {'name': 'ctl00$ContentPlaceHolder1$txtFacultad'})['value']
    )
    major = _normalize_name(
        soup.find('input', {'name': 'ctl00$ContentPlaceHolder1$txtPrograma'})['value']
    )
    name = _normalize_name(
        soup.find('input', {'name': 'ctl00$ContentPlaceHolder1$txtAlumno'})['value']
    )

    photo = soup.find('img', {'id': 'ctl00_ContentPlaceHolder1_imgAlumno'})['src']
    user_photo = base_url + photo

    if not faculty or not major or not name:
        return None

    return {'faculty': faculty, 'major': major, 'name': name, 'user_photo': user_photo}

def _parse_form_data(html: str, codigo: str) -> dict:
    """
    Parses the form data from the HTML response.
    """
    soup = BeautifulSoup(html, 'html.parser')
    viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
    viewstate_generator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
    event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']

    return {
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstate_generator,
        '__EVENTVALIDATION': event_validation,
        '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$cmdConsultar',
        'ctl00$ContentPlaceHolder1$txtUsuario': codigo,
    }
    
# Methods for verifying student email addresses
def _email_existance(html: str, email: str) -> bool:
    soup = BeautifulSoup(html, 'html.parser')
    transformed_email = _transform_email(email)
    error_message = f"El usuario {transformed_email} no está registrado."

    login_error = soup.select_one('.login-error span')
    if login_error:
        login_error_text = login_error.text.strip()
        # Si el mensaje de error es diferente al esperado, entonces el email existe
        return login_error_text != error_message
    return False

def _transform_email(email: str) -> str:
    return email.split('@')[0]

def _filter_cookies(cookie_jar) -> dict:
    cookie_dict = cookie_jar.get_dict()
    filtered_cookies = {
        key: value for key, value in cookie_dict.items()
        if key in ['JSESSIONID', 'HWWAFSESID', 'HWWAFSESTIME', '8390ce12805d422a96ff76763b01e900']
    }
    return filtered_cookies    
    
    
def scrape_alumno_by_code(codigo: str) -> dict:
    url = 'http://websecgen.unmsm.edu.pe/carne/'
    aspx = 'carne.aspx'

    # Obtener la página inicial
    response = requests.get(url + aspx)
    form_data = _parse_form_data(response.text, codigo)

    # Hacer la solicitud POST con los datos del formulario
    alumno_html = requests.post(url + aspx, headers={
        'Content-Type': 'application/x-www-form-urlencoded',
    }, data=form_data)

    return _parse_alumno(alumno_html.text, url)

def scrape_alumno_by_email(email: str):
    domain = 'https://sum.unmsm.edu.pe'
    url = f"{domain}/alumnoWebSum/login"

    # Primero, obtenemos las cookies
    cookie_response = requests.get(url)
    if cookie_response.status_code != 200:
        raise Exception(
            f"Error {cookie_response.status_code}, origin: {cookie_response.url} failed to fetch"
        )
    
    cookies = _filter_cookies(cookie_response.cookies)

    # Luego, obtenemos el token CSRF
    soup = BeautifulSoup(cookie_response.text, 'html.parser')
    csrf = soup.find('input', {'name': '_csrf'})['value']

    # Ahora hacemos la solicitud para iniciar sesión
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'es-419,es;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': domain,
        'Referer': url,
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
        'Upgrade-Insecure-Requests': '1',
    }

    data = {
        '_csrf': csrf,
        'login': email,
        'clave': ''
    }

    response = requests.post(url, headers=headers, cookies=cookies, data=data)

    if response.status_code != 200:
        raise Exception(
            f"Error {response.status_code}, origin: {response.url} failed to fetch"
        )

    return _email_existance(response.text, email)
