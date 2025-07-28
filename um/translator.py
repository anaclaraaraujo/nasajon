# Importação das libs
import xml.etree.ElementTree as ET
from googletrans import Translator

# Carrega o XML original
tree = ET.parse('um/arquivos/localization_en.xml')
root = tree.getroot()

# Atualiza o atributo culture para pt
root.set('culture', 'pt')

# Cria um tradutor
translator = Translator()

# Namespace usado no XML
ns = {'ns': 'http://nasajon.com/schemas/localization.xsd'}

# Registra o namespace (para salvar corretamente depois)
ET.register_namespace('', ns['ns'])

# Itera por todas as tags <string> e traduz o texto
for string_element in root.findall('.//ns:string', ns):
    original_text = string_element.text
    if original_text and original_text.strip():
        translated = translator.translate(original_text, src='en', dest='pt').text
        string_element.text = translated
        print(f'Traduzido: "{original_text}" → "{translated}"')

# Salva o novo XML traduzido
tree.write('um/arquivos/localization_pt.xml', encoding='utf-8', xml_declaration=True)
