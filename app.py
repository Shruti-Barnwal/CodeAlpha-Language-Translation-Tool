# app.py — Flask backend for Language Translation Tool

from flask import Flask, render_template, request, jsonify
import requests
from urllib.parse import quote  # Safely encode text for URL parameters

app = Flask(__name__)


# Translation Logic with API Call
class TranslationService:
    def __init__(self):
        # Base URL of MyMemory Translation API
        self.base_url = "https://api.mymemory.translated.net/get"

    def translate_text(self, text, source_lang, target_lang):
        """
        Translate the given text using MyMemory API.
        """
        try:
            # Encode text for safe URL usage
            encoded_text = quote(text)

            # Construct the API URL
            url = f"{self.base_url}?q={encoded_text}&langpair={source_lang}|{target_lang}"

            # Send a GET request to MyMemory API
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise error if status is not 200

            # Convert response to JSON
            data = response.json()

            # Check API response
            if data.get('responseStatus') == 200:
                return {
                    'success': True,
                    'translated_text': data['responseData']['translatedText'],
                    'source_lang': source_lang,
                    'target_lang': target_lang
                }
            else:
                return {
                    'success': False,
                    'error': data.get('responseDetails', 'Translation failed')
                }

        except requests.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Translation error: {str(e)}'
            }

    def get_supported_languages(self):
        """
        Returns a dictionary of supported languages.
        Keys are language codes; values are language names.
        """
        return {
            'auto': 'Auto-detect',
            'en': 'English',
            'hi': 'Hindi',
            'bn': 'Bengali',
            'gu': 'Gujarati',
            'ml': 'Malayalam',
            'mr': 'Marathi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese (Simplified)',
            'zh-tw': 'Chinese (Traditional)',
            'ar': 'Arabic',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'no': 'Norwegian',
            'da': 'Danish',
            'fi': 'Finnish',
            'pl': 'Polish',
            'el': 'Greek',
            'ro': 'Romanian',
        }

# Flask Routes and API Setup
# Initialize translator object
translator = TranslationService()

@app.route('/')
def index():
    """
    Render the main HTML page with available languages.
    """
    languages = translator.get_supported_languages()
    return render_template('index.html', languages=languages)

@app.route('/translate', methods=['POST'])
def translate():
    """
    Handle translation POST requests via JSON.
    """
    try:
        data = request.get_json()

        # Basic validation
        if not data or 'text' not in data:
            return jsonify({'success': False, 'error': 'No text provided'})

        text = data['text'].strip()
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'en')

        if not text:
            return jsonify({'success': False, 'error': 'Please enter text to translate'})
        if len(text) > 5000:
            return jsonify({'success': False, 'error': 'Text too long (max 5000 characters)'})
        if source_lang == target_lang and source_lang != 'auto':
            return jsonify({'success': False, 'error': 'Source and target languages cannot be the same'})

        # Translate using the service
        result = translator.translate_text(text, source_lang, target_lang)
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})

@app.route('/languages')
def get_languages():
    """
    Return supported languages as JSON.
    Useful for frontend dropdowns.
    """
    return jsonify(translator.get_supported_languages())


# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# Start the Flask Server
if __name__ == '__main__':
    print("Starting Translation Server...")
    print("Open http://localhost:5000 in your browser")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)
